from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
import threading, time, socket
from client import recieve, send_msg
from server import receive


Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '300')
Config.set('graphics', 'resizable', '1')

serverThread = None

class MsgWindow(Screen):
    def create_popup(self, title, msg: str=None, dur=3):
        if msg:
            popup = Popup(title=title,
                content=Label(text=msg),
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        else:
            popup = Popup(title=title,
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        popup.open()
        Clock.schedule_interval(lambda x: popup.dismiss(), dur)
    
    def create_upper_tab(self, x: Widget):
        box = BoxLayout(orientation='horizontal', size_hint=(1, None), pos=(0, Window.height), height=Window.height*0.1)
        leave_button = Button(
            text="Leave Server",
            size_hint=(0.3,1),
            background_color=[1,0,0,1],
            color=[0,0,0,1],
        )
        
        def back_to_home(instance):
            global serverThread
            self.manager.current = 'home'
            self.sm.remove_widget(self)
            self.thread_event.set()
            if server_event.is_set():
                server_event.clear()
            self.s.close()
        
        # Font changes accordinf to screensize
        def change_leave_font(instance, value):
            leave_button.font_size = box.height-leave_button.width    
        Window.bind(size=change_leave_font)
        
        leave_button.bind(on_press=back_to_home)
        filler_button = Button(
            size_hint=(0.7,1),
            disabled=True,
            # 71, 69, 69
            disabled_color = [71/255, 69/255, 69/255, 1]
        )
        
        box.add_widget(leave_button)
        box.add_widget(filler_button)
           
        def change_box_height(instance, value):
            leave_button.font_size=box.height*0.5
            
        Window.bind(size=change_box_height)
        Clock.schedule_once(lambda x: change_box_height(1,1))
        return box
        
    def create_rounded_label(self, text, name="default", width=400):
        def decide_col():
            if name==self.self_name:
                # 32, 95, 212
                return Color(32/255, 95/255, 212/255, 1)
            elif name=="Server":
                # 201, 201, 18
                return Color(201/255, 201/255, 18/255)
            else:
                # 49, 57, 71
                return Color(49/255, 57/255, 71/255, 1)
        
        # Sender name label
        l_name = Label(
            text=str(name),
            size_hint=(None, None),
            width=width,
            font_size=20,
            font_name='comicbd',
            bold=True,
            text_size=(width, None),
            halign="left",
            valign="middle",
            padding=(7, 1),
        )
        
        # Message label
        l = Label(
            text=str(text),
            size_hint=(None, None),
            width=width,
            font_size=23,
            font_name='comic',    
            text_size=(width, None),
            halign="left",
            valign="middle",
            padding=(7, 7),
        )

        # Ensure labels resize based on text
        l.bind(texture_size=l.setter("size"))
        l_name.bind(texture_size=l_name.setter("size"))

        # Adjust box size dynamically based on labels
        def update_box_size(instance, value):
            box.height = l_name.height + l.height  # Total height of both labels

        with l_name.canvas.before:
            decide_col()  # name background
            l_name.rect = RoundedRectangle(pos=l_name.pos, size=l_name.size, radius=[10, 10, 0, 0])

        with l.canvas.before:
            decide_col() # msg background
            l.rect = RoundedRectangle(pos=l.pos, size=l.size, radius=[0, 0, 10, 10])

        # Update background positions dynamically
        def update_rect(instance, value):
            l.rect.pos = l.pos
            l.rect.size = l.size


        def update_rect_name(instance, value):
            l_name.rect.pos = l_name.pos
            l_name.rect.size = l_name.size
        
        def update_height_float(instance, value):
            f_lay.height = box.height
            
        def update_box_position(instance, height):
            if name==self.self_name:
                box.pos_hint = {'x':(Window.width-width)/Window.width, 'y':0}
            else:
                box.pos_hint = {'x':0, 'y':0}
            
        l.bind(size=update_box_size)
        l_name.bind(size=update_box_size)
        
        l.bind(pos=update_rect, size=update_rect)
        l_name.bind(pos=update_rect_name, size=update_rect_name)

        p_hint = {'x': (Window.width-width)/Window.width, 'y':0} if self.self_name==name else {'x': 0, 'y':0}
        box = BoxLayout(orientation='vertical', size_hint=(None, None), width=width, pos_hint=p_hint)

        # Add labels to the box
        box.add_widget(l_name)
        box.add_widget(l)
        
        f_lay = FloatLayout(size_hint=(1, None), height=box.height, width=Window.width)
        f_lay.add_widget(box)
        Window.bind(size=update_height_float)
        Clock.schedule_once(lambda x: update_height_float(1,1))
        Window.bind(size=update_box_position)
        return f_lay
    
    # This is the event to shut down threads
    thread_event = threading.Event()
    
    def msg_recv_thread(self, parent: Widget):
        while not self.thread_event.is_set():
            if self.msgs:
                message: str = self.msgs.pop(0)
                message = message.split(':')
                Clock.schedule_once(lambda x: parent.add_widget(self.create_rounded_label(message[1], name=message[0])))
    
    def close_window_forcefully(self, value, instance):
        global serverThread
        if server_event.is_set():
            server_event.clear()
            serverThread = None
        else:
            self.create_popup("Host has closed the server")
        self.manager.current = 'home'
        self.sm.remove_widget(self)
        self.s.close()
        
    
    def __init__(self, sm, s, self_name, **kwargs):
        super(MsgWindow, self).__init__(**kwargs)
        # This variables handles the runnning of all threads
        
        # Just a variable to refer to The ScreenManager of MainApp
        # This variable is only defined so i can remove the widget when leaving
        self.sm=sm
        self.s = s
        self.self_name = self_name
        
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Adding the leave tab
        self.upper_tab = self.create_upper_tab(self.grid)
        
        def update_upper_tab(instance, value):
            self.upper_tab.height = Window.height*0.1
            self.upper_tab.pos = (0, Window.height)
            
        self.grid.add_widget(self.upper_tab)
        update_upper_tab(None, None)
        Window.bind(size=update_upper_tab)
        
        self.msg_box = ScrollView(
            size_hint=(1, None),
            size=(Window.width, Window.height*0.9)
        )
        self.grid.add_widget(self.msg_box)
        
        self.msg_grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=6)
        self.msg_grid.bind(minimum_height=self.msg_grid.setter('height'))
        self.msg_box.add_widget(self.msg_grid)
        
        self.msgs = []
        
        # starting the message receving thread
        args = {
            's':self.s,
            'lst':self.msgs,
            'event':self.thread_event,
            'on_end': lambda : Clock.schedule_once(lambda x: self.close_window_forcefully(1,1))
        }
        
        self.recv_thread = threading.Thread(target=recieve, kwargs=args)
        self.recv_thread.start()
        
        # Starting the message display thread
        self.msg_thread = threading.Thread(target=self.msg_recv_thread, args=(self.msg_grid,))
        self.msg_thread.start()
            
        # Creating Inp_box
        self.inp_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=Window.height*0.1, spacing=5)
        self.inp = TextInput(size_hint=(0.7, 1), font_size='30sp')
        
        # Creating the button
        self.send_btn = Button(text="Send", font_size='50sp', size_hint=(0.3,1))
        def send_message(instance):
            msg = self.inp.text
            self.inp.text = ""
            send_msg(self.s, msg=msg)
        # Binding send_message onpress
        self.send_btn.bind(on_press=send_message)
        
        self.inp_box.add_widget(self.inp)
        self.inp_box.add_widget(self.send_btn)

        # Adding the inp_box to the main grid
        self.grid.add_widget(self.inp_box)

        # For updating layouts on load
        def update_layout(instance, value):
            self.inp_box.height = Window.height*0.1
            self.inp.font_size = self.inp_box.height - 25
            self.send_btn.font_size = self.inp_box.height
            self.msg_box.height = Window.height - self.inp_box.height-self.upper_tab.height
            self.inp_box.pos = (0, 0)

        Window.bind(size=update_layout)
        
        # This function stops all the thread and closes the socket when you close the window
        def closing_window(instance):
            global serverThread
            self.s.close()
            self.thread_event.set()
            server_event.clear()
            serverThread = None
            return False
        Window.bind(on_request_close=closing_window)
        
        Clock.schedule_once(lambda x: update_layout(1,1))
        Clock.schedule_once(lambda x: update_upper_tab(1,1))
        self.add_widget(self.grid)

server_event = threading.Event()

class ServerScreen(Screen):
    def create_popup(self, title, msg: str=None, dur=3):
        if msg:
            popup = Popup(title=title,
                content=Label(text=msg),
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        else:
            popup = Popup(title=title,
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        popup.open()
        Clock.schedule_interval(lambda x: popup.dismiss(), dur)

    
    
    def __init__(self,sm, **kwargs):
        super(ServerScreen, self).__init__(**kwargs)
        rlo = RelativeLayout()
        l2 = Label(
            text="Enter Port", size_hint=(.2, .1),
            pos_hint={'x': .2, 'y': .75},
            font_size='23sp',
        )
        rlo.add_widget(l2)
        t2 = TextInput(
            size_hint=(.4, .1),
            pos_hint={'x': .3, 'y': .65},
            font_size='23sp',
        )
        rlo.add_widget(t2)
        l3 = Label(
            text="Enter Your name", size_hint=(.2, .1),
            pos_hint={'x': .2, 'y': .55},
            font_size='23sp',
        )
        rlo.add_widget(l3)
        t3 = TextInput(
            size_hint=(.4, .1),
            pos_hint={'x': .3, 'y': .45},
            font_size='23sp',
        )
        rlo.add_widget(t3)
        b1 = Button(
            text='Create', size_hint=(.2, .1),
            pos_hint={'center_x': .5, 'center_y': .09},
            font_size='30sp',
        )
        
        def change_sizes(instance, value):
            b1.font_size = b1.height*0.5
            

        def get_details_and_redirect(instance):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.settimeout(1)
            try:
                ip = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
                port = int(t2.text)
                name = t3.text
                if name.lower()=="server":
                    self.create_popup("Name Cant be Server","The name server is not allowed", dur=3)
                    return
                serverThread = threading.Thread(target=receive, args=(ip, port, server_event))
                serverThread.start()
                server_event.wait()
                s.connect((ip, port))
                          
            except ValueError as e:
                self.create_popup("ValueError", "Enter Proper Values")
                print(e)
            except WindowsError as e:
                self.create_popup("WindowsError", "Host Not Found", dur=5)
                print(e)
            except Exception as e:
                self.create_popup("Error", e.__str__())
                print(e)
            else:
                s.send(name.encode())
                answer = s.recv(1024).decode()
                answer = answer.split(":")
                if answer[0]=="refused":
                    self.create_popup("Name already taken", "This name is already taken. Try again!", dur=5)
                else:
                    sm.add_widget(MsgWindow(sm,s, name='msgs', self_name=name))
                    self.manager.current='msgs'
      
        Window.bind(size=change_sizes)
        b1.bind(on_release=get_details_and_redirect)
        rlo.add_widget(b1)
        self.add_widget(rlo)

        
      

class MainScreen(Screen):
    def create_popup(self, title, msg: str=None, dur=3):
        if msg:
            popup = Popup(title=title,
                content=Label(text=msg),
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        else:
            popup = Popup(title=title,
                size_hint=(None, None), size=(400, 250),
                title_size='40sp',
                )
        popup.open()
        Clock.schedule_interval(lambda x: popup.dismiss(), dur)


    def __init__(self,sm, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        rlo = RelativeLayout()
        l1 = Label(
            text="Enter IP address", size_hint=(.2, .1),
            pos_hint={'x': .2, 'y': .75},
            font_size='23sp',
        )
        rlo.add_widget(l1)
        t1 = TextInput(
            size_hint=(.4, .1), pos_hint={'x': .3, 'y': .65},
            font_size='23sp',
        )
        rlo.add_widget(t1)
        l2 = Label(
            text="Enter Port", size_hint=(.2, .1),
            pos_hint={'x': .2, 'y': .55},
            font_size='23sp',
        )
        rlo.add_widget(l2)
        t2 = TextInput(
            size_hint=(.4, .1),
            pos_hint={'x': .3, 'y': .45},
            font_size='23sp',
        )
        rlo.add_widget(t2)
        l3 = Label(
            text="Enter Your name", size_hint=(.2, .1),
            pos_hint={'x': .2, 'y': .35},
            font_size='23sp',
        )
        rlo.add_widget(l3)
        t3 = TextInput(
            size_hint=(.4, .1),
            pos_hint={'x': .3, 'y': .25},
            font_size='23sp',
        )
        rlo.add_widget(t3)
        b1 = Button(
            text='Join', size_hint=(.2, .1),
            pos_hint={'center_x': .3, 'center_y': .09},
            font_size='30sp',
        )
        b2 = Button(
            text='Create Server', size_hint=(.3, .1),
            pos_hint={'center_x': .65, 'center_y': .09},
            font_size='30sp',
        )
        
        def change_sizes(instance, value):
            b2.font_size = b2.height*0.5
            b1.font_size = b1.height*0.5
        
        Window.bind(size=change_sizes)
        
        def get_details_and_redirect(instance):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            try:
                ip = t1.text
                port = int(t2.text)
                name = t3.text
                if name.lower()=="server":
                    self.create_popup("Name Cant be Server","The name server is not allowed", dur=3)
                    return

                s.connect((ip,port))
                          
            except ValueError as e:
                self.create_popup("ValueError", "Enter Proper Values")
                print(e)
            except WindowsError as e:
                self.create_popup("WindowsError", "Host Not Found", dur=6)
                print(e)
            except Exception as e:
                self.create_popup("Error", "An error occured")
                print(e)
            else:
                s.settimeout(None)
                s.send(name.encode())
                answer = s.recv(1024).decode()
                answer = answer.split(":")
                if answer[0]=="refused":
                    self.create_popup("Name already taken", "This name is already taken. Try again!", dur=5)
                else:
                    sm.add_widget(MsgWindow(sm,s, name='msgs', self_name=name))
                    self.manager.current='msgs'
                    
        def test_redirect(instance):
            self.manager.current='server_screen'
            
        b1.bind(on_release=get_details_and_redirect)
        b2.bind(on_release=test_redirect)
        rlo.add_widget(b1)
        rlo.add_widget(b2)
        self.add_widget(rlo)

class Main(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(sm=sm,name='home'))
        sm.add_widget(ServerScreen(sm, name="server_screen"))
        return sm
    
Main().run()