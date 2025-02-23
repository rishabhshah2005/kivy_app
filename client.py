import socket
import threading

def recieve(s: socket.socket, lst: list, event: threading.Event=None, print_flag=False):
    while not (event.is_set() if event else False):
        try:
            msg = s.recv(1024).decode('utf-8')
            lst.append(msg)
            if print_flag:
                print(msg)
        except Exception as e:
            print("Exception in receive")
            if event:
                event.set()
            print(e)
            break

        
def send_msg(s: socket.socket, msg: str=None):
    if msg==None:
        msg = input("Enter msg: ")
        while msg:
            try:
                s.send(msg.encode('utf-8'))
            except Exception as e:
                print(e)
                print("Exception in send_msg")
                s.close()
                break
            msg = input("Enter msg: ")
        else:
            s.close()
    else:
        if len(msg)==0:
            return
        try:
            s.send(msg.encode('utf-8'))
        except Exception as e:
            print(e)
            print("Exception in send_msg")
            s.close()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5555

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    name = input("Enter name: ")
    s.send(name.encode('utf-8'))
    msgs = []
    running = False
    t = threading.Thread(target=recieve, args=(s,msgs, running, True))
    t.start()
    send_msg(s)