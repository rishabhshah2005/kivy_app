from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.config import Config

Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '300')
Config.set('graphics', 'resizable', '1')

class MyAppApp(App):
    
    def create_upper_tab(self):
        box = BoxLayout(orientation='horizontal', size_hint=(1, None), pos=(0, Window.height), height=Window.height*0.1)
        leave_button = Button(
            text="Leave Server",
            size_hint=(0.3,1),
            background_color=[1,0,0,1],
            color=[0,0,0,1],
        )
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
        
    def create_rounded_label(self, text, name="default", width=400, self_send=False):
        
        def decide_col():
            if self_send:
                # 32, 95, 212
                return Color(32/255, 95/255, 212/255, 1)
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
            decide_col()  # Lime green background
            l_name.rect = RoundedRectangle(pos=l_name.pos, size=l_name.size, radius=[10, 10, 0, 0])

        with l.canvas.before:
            decide_col() # Lime green background
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
            if self_send:
                box.pos_hint = {'x':(Window.width-width)/Window.width, 'y':0}
            else:
                box.pos_hint = {'x':0, 'y':0}
            
        l.bind(size=update_box_size)
        l_name.bind(size=update_box_size)
        
        l.bind(pos=update_rect, size=update_rect)
        l_name.bind(pos=update_rect_name, size=update_rect_name)

        p_hint = {'x': (Window.width-width)/Window.width, 'y':0} if self_send else {'x': 0, 'y':0}
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
           
    
    def build(self):
        self.grid = GridLayout(cols=1, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Adding the leave tab
        self.upper_tab = self.create_upper_tab()
        
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
        for i in range(20):
            a = i%2==1
            msg = self.create_rounded_label(f"Rishabh adasd dasd {i}\n"*10, self_send=a)
            self.msg_grid.add_widget(msg)
            
        # Creating Inp_box
        self.inp_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=Window.height*0.1, spacing=5)
        self.inp = TextInput(size_hint=(0.7, 1), font_size='30sp')
        self.send_btn = Button(text="Send", font_size='50sp', size_hint=(0.3,1))
        self.inp_box.add_widget(self.inp)
        self.inp_box.add_widget(self.send_btn)

        # Adding the inp_box to the main grid
        self.grid.add_widget(self.inp_box)

        def update_layout(instance, value):
            self.inp_box.height = Window.height*0.1
            self.inp.font_size = self.inp_box.height - (self.inp_box.width)
            self.send_btn.font_size = self.inp_box.height
            self.msg_box.height = Window.height - self.inp_box.height-self.upper_tab.height
            self.inp_box.pos = (0, 0)

        Window.bind(size=update_layout)
        Clock.schedule_once(lambda x: update_layout(1,1))
        Clock.schedule_once(lambda x: update_upper_tab(1,1))
        return self.grid
        

MyAppApp().run()