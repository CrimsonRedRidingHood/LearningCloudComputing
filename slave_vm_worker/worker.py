import random
import socket

quotes_list = [\
"Everything popular is wrong (Oscrar Wilde)",\
"Second thoughts are the reinforcements of the firsts thoughts you were trying to ignore. (Steve)",
"No one can resolve your conflicts and battles in your heart, but you. (Steve)",\
"It's just good business. (Lord Beckett)",\
"Some are born great, others achieve greatness. (William Shakespeare)",\
"You know, you can't be best at everything... hold on... no, it's just a limiting belief - you can be best at everything.",\
"We never start our day with intention (Zan)",\
"What most people actually like doing is crying complaining and dreaming.",\
"Don't trust those who don't believe in you.",\
"You are what you eat.",\
]

port = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port))
server_socket.listen(1)
connected_master, addr = server_socket.accept()
while True:
    data = connected_master.recv(1)
    connected_master.sendall(random.choice(quotes_list).encode())
connected_master.close()