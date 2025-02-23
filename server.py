import socket
import threading

host = "127.0.0.1"
port = 5555

clients = dict()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()

def send_msg(msg: bytes, name: str):
    try:
        for conn in clients:
            conn.send((name+":").encode()+msg)
            print("sending to", conn)
    except Exception as e:
        print("exception in send")
        print(e)

def incoming(conn: socket.socket, name: str):
    while True:
        try:
            data = conn.recv(1024)
            send_msg(data, name)
            del data
        except Exception as e:
            print("exception in incoming")
            print(e)
            clients.__delitem__(conn)
            print(name, "left")
            send_msg(f"{name} left".encode(), "Server")
            conn.close()
            break
            

def receive():
    
    print("Server Started....")
    while True:
        try:
            conn, addr = s.accept()
            print("acc")
            name = conn.recv(1024).decode('utf-8')
            clients[conn] = name
            print(name, "connected", addr)
            send_msg(f"{name} has connected!!".encode(), "Server")
            t = threading.Thread(target=incoming, args=(conn, name))
            t.start()
            print("Thread started")

        except Exception as e:
            print("exception in recv")
            print(e)
            break

        
            
receive()
s.close()