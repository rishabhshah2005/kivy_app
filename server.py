import socket
import threading

def server_send_msg(msg: bytes, name: str, clients: dict):
    try:
        for conn in clients:
            conn.send((name+":").encode()+msg)
            print("sending to", conn)
    except Exception as e:
        print("exception in send")
        print(e)

def incoming(conn: socket.socket, name: str, clients: dict):
    while True:
        try:
            data = conn.recv(1024)
            server_send_msg(data, name, clients=clients)
            del data
        except Exception as e:
            print("exception in incoming")
            print(e)
            clients.__delitem__(conn)
            print(name, "left")
            server_send_msg(f"{name} left".encode(), "Server", clients=clients)
            conn.close()
            break
            

def receive(host, port, thread_event: threading.Event = None):
    clients: dict[socket.socket, str] = dict()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    s.settimeout(1.0)
    print("Server Started....")
    thread_event.set()
    while thread_event.is_set():
        try:
            conn, addr = s.accept()
            print("acc")
            name: str = conn.recv(1024).decode('utf-8')
            if name in clients.values():
                conn.send("refused:name already taken!".encode())
            elif name.lower() == 'server':
                conn.send("refused:name cant be Server!".encode())
            else:
                conn.send("accepted".encode())
                clients[conn] = name
                print(name, "connected", addr)
                server_send_msg(f"{name}({addr[0]}) has connected!!".encode(), "Server", clients=clients)
                t = threading.Thread(target=incoming, args=(conn, name, clients))
                t.start()
                print("Thread started")
        except socket.timeout:
            continue
        except Exception as e:
            print("exception in recv")
            print(e)
            s.close()
            break
    else:
        for i in clients:
            i.close()
        s.close()
        print("Server closed") 
        return     

if __name__ == '__main__':   
    receive("127.0.0.1", 5555)
    