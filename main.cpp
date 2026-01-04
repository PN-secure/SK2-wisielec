#include <iostream>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <fstream>
#include <string>
#include <sstream>
#include <random>
#include <map>
#include <set>



std::vector<int> waitForClients(int port, int clientCount) {
    std::vector<int> clientSockets;

    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket < 0) {
        perror("socket");
        return clientSockets;
    }

    int opt = 1;
    if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(serverSocket);
        return clientSockets;
    }

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr. sin_port = htons(port);
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("bind");
        close(serverSocket);
        return clientSockets;
    }

    if (listen(serverSocket, clientCount) < 0) {
        perror("listen");
        close(serverSocket);
        return clientSockets;
    }

    std::cout << "serwer czeka na " << clientCount << " klientów.. .\n";

    while ((int)clientSockets.size() < clientCount) {
        int clientSocket = accept(serverSocket, nullptr, nullptr);
        if (clientSocket < 0) {
            perror("accept");
            continue;
        }
        clientSockets.push_back(clientSocket);
        std::cout << "klient dołączony ("
                  << clientSockets. size() << "/"
                  << clientCount << ")\n";
    }

    close(serverSocket); 
    return clientSockets;
}

std::string randomWord(const std::string& nazwaPliku) {
    std::ifstream file(nazwaPliku);
    if (!file.is_open()) {
        return "";
    }

    std:: string linia;
    std:: getline(file, linia);
    file.close();

    std::vector<std::string> slowa;
    std::stringstream ss(linia);
    std::string slowo;

    while (std::getline(ss, slowo, ',')) {
        if (!slowo.empty())
            slowa.push_back(slowo);
    }

    if (slowa.empty()) {
        return "";
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(0, slowa.size() - 1);

    return slowa[dist(gen)];
}

void manageGame(const std::vector<int>& clientSockets, const std:: string& wylosowaneSlowo) {
    int totalClients = clientSockets.size();
    
    std::map<int,int> socketToClientNumber;
    
    std::set<int> activeSockets;
    
    for (size_t i = 0; i < clientSockets.size(); ++i) {
        socketToClientNumber[clientSockets[i]] = i + 1;
        activeSockets.insert(clientSockets[i]);
        
        std::string startMsg = "start " + std::to_string(i + 1) + " " + 
                               wylosowaneSlowo + " " + std:: to_string(totalClients) + "\n";
        send(clientSockets[i], startMsg.c_str(), startMsg.length(), 0);
        std::cout << "wysłano do klienta " << (i + 1) << ": " << startMsg;
    }

    fd_set readfds;
    int maxFd = 0;
    for (int sock : clientSockets) {
        if (sock > maxFd) maxFd = sock;
    }

    bool gameRunning = true;
    while (gameRunning) {
        if (activeSockets.empty()) {
            std::cout << "wszyscy klienci się rozłączyli gra zakończona\n";
            break;
        }


        FD_ZERO(&readfds);
        for (int sock : activeSockets) {
            FD_SET(sock, &readfds);
        }

        int activity = select(maxFd + 1, &readfds, nullptr, nullptr, nullptr);
        if (activity < 0) {
            perror("select");
            break;
        }

        std::set<int> socketsToCheck = activeSockets;
        for (int sock : socketsToCheck) {
            if (FD_ISSET(sock, &readfds)) {
                char buffer[1024] = {0};
                int bytesRead = recv(sock, buffer, sizeof(buffer) - 1, 0);
                
                if (bytesRead <= 0) {
                    int clientNumber = socketToClientNumber[sock];
                    std:: cout << "klient " << clientNumber << " utracił połączenie\n";
                    
                    activeSockets.erase(sock);
                    close(sock);
                    
                    std::string disconnectMsg = "utracono " + std::to_string(clientNumber) + "\n";
                    for (int clientSock : activeSockets) {
                        send(clientSock, disconnectMsg.c_str(), disconnectMsg.length(), 0);
                    }
                    std::cout << "wysłano wiadomość:  " << disconnectMsg;
                    
                    continue;
                }

                buffer[bytesRead] = '\0';
                std::string message(buffer);
                
                if (! message.empty() && message.back() == '\n') {
                    message.pop_back();
                }

                std::cout << "otrzymano: " << message << "\n";

                if (message.find("wygralem") == 0) {
                    std::string winMsg = message + "\n";
                    for (int clientSock : activeSockets) {
                        send(clientSock, winMsg. c_str(), winMsg.length(), 0);
                    }
                    std::cout << "Gra zakończona! " << message << "\n";
                    gameRunning = false;
                    break;
                } else {
                    std::string echoMsg = message + "\n";
                    for (int clientSock : activeSockets) {
                        send(clientSock, echoMsg.c_str(), echoMsg.length(), 0);
                    }
                }
            }
        }
    }

    for (int sock :  activeSockets) {
        close(sock);
    }
    std::cout << "Wszystkie sockety zamknięte\n";
}


int main(int argc, char *argv[]) {
    int port = 8000;    
    int clientCount = 2;  
    std::string wordsFile = "words.txt"; 


    if (argc >= 2) {
        port = std::atoi(argv[1]);
        if (port <= 0 || port > 65535) {
            std::cerr << "błąd: nieprawidłowy numer portu\n";
            return 1;
        }
    }

    if (argc >= 3) {
        clientCount = std::atoi(argv[2]);
        if (clientCount <= 0) {
            std::cerr << "liczba klientów musi być większa od 0\n";
            return 1;
        }
    }

    if (argc >= 4) {
        wordsFile = argv[3];
    }


    while (true) {
        std::cout << "\nNOWA GRA\n";
        
        std::vector<int> clients = waitForClients(port, clientCount);
        
        if (clients.size() != clientCount) {
            std::cerr << "błąd przy łączeniu klientów\n";
            for (int sock : clients) {
                close(sock);
            }
            continue; 
        }

        std::string slowo = randomWord(wordsFile);
        if (slowo.empty()) {
            std:: cerr << "błąd przy wczytywaniu słowa\n";
            for (int sock : clients) {
                close(sock);
            }
            continue; 
        }
        std::cout << "wylosowane słowo: " << slowo << "\n";

        manageGame(clients, slowo);
        
        std::cout << "gra zakończona  oczekiwanie na nowych klientów\n";
    }

    return 0;
}