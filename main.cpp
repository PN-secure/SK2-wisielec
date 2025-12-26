#include <iostream>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#include <fstream>
#include <string>
#include <sstream>
#include <random>






std::vector<int> waitForClients(int port, int clientCount) {
    std::vector<int> clientSockets;

    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket < 0) {
        perror("socket");
        return clientSockets;
    }

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
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

    std::cout << "Serwer czeka na " << clientCount << " klientów...\n";

    while ((int)clientSockets.size() < clientCount) {
        int clientSocket = accept(serverSocket, nullptr, nullptr);
        if (clientSocket < 0) {
            perror("accept");
            continue;
        }

        clientSockets.push_back(clientSocket);
        std::cout << "Klient dołączony ("
                  << clientSockets.size() << "/"
                  << clientCount << ")\n";
    }

    close(serverSocket); // nie przyjmujemy więcej
    return clientSockets;
}

std::string randomWord(const std::string& nazwaPliku) {
    std::ifstream file(nazwaPliku);
    if (!file.is_open()) {
        return "";
    }

    std::string linia;
    std::getline(file, linia);
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

int main() {

    std::cout << randomWord("words.txt");
    return 0;
}
