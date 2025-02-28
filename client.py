import socket
import threading

def recieve(s: socket.socket, lst: list, event: threading.Event=None, print_flag=False, on_end: callable=None):
    if event:
        event.clear()
    while not (event.is_set() if event else False):
        try:
            msg = s.recv(1024).decode('utf-8')
            lst.append(msg)
            if print_flag:
                print(msg)
        except ConnectionResetError:
            if on_end!=None:
                on_end()
            if event:
                event.set()
            break
        except Exception as e:
            print(type(e))
            # print("Exception in receive")
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
            # print("Exception in send_msg")
            s.close()

if __name__ == "__main__":
    host = "192.168.29.33"
    port = 5555

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    name = input("Enter name: ")
    s.send(name.encode('utf-8'))
    answer = s.recv(1024).decode()
    answer = answer.split(":")
    if answer[0]=="refused":
        print("Name already taken!!")
    else:
        msgs = []
        running = False
        t = threading.Thread(target=recieve, args=(s,msgs, running, True))
        t.start()
        send_msg(s)