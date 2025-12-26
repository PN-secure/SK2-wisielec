import socket

HOST = "127.0.0.1"  # adres serwera (localhost)
PORT = 12345        # ten sam port co w serwerze

# tworzymy socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# łączymy się z serwerem
sock.connect((HOST, PORT))

# odbieramy dane
data = sock.recv(1024)

# wyświetlamy odpowiedź
print("Odpowiedź z serwera:")
print(data.decode("utf-8"))

# zamykamy połączenie
sock.close()
