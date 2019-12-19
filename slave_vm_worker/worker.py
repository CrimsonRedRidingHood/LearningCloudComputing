import random
import socket

quotes_list = ["Second thoughts are the reinforcements of the first thoughts you were trying to ignore (Steve Piccus)", "If I don't succeed, then let seed suck me. (Steve Piccus)"];

PORT = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', PORT))
server_socket.listen(1)
connected_master, addr = server_socket.accept()
while True:
    data = connected_master.recv(1)
    connected_master.sendall(random.choice(quotes_list).encode())
connected_master.close()