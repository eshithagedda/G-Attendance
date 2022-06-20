import socket
from threading import Thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0',6666))
s.listen(100)

def thread(cs):
    argument = cs.recv(1024)
    argument = argument.decode('utf-8')

    if argument == 'LOGIN':
        with open('cred.json', 'r') as f:
            data = f.read()

        cs.send(bytes(data,'utf-8'))
        
        return_code = cs.recv(1024)
        return_code = return_code.decode('utf-8')

        if return_code == 'SUCCESS':
            cs.close()
            print(f'{address} has logged in.')


        f.close()

while True:
    cs, address = s.accept()

    t = Thread(target= thread, args = (cs,))
    t.daemon = True
    t.start()

