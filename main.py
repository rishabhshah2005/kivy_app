from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

class MyAppApp(App):
        
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
            # pos_hint=p_hint,
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
            # pos_hint=p_hint,
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
        self.grid = GridLayout(cols=1)
        self.msg_box = ScrollView(
         size_hint=(1, None),
         size=(Window.width, Window.height-100)
      )
        self.grid.add_widget(self.msg_box)
        
        self.msg_grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=6)
        self.msg_grid.bind(minimum_height=self.msg_grid.setter('height'))
        self.msg_box.add_widget(self.msg_grid)
        for i in range(20):
            a = i%2==1
            msg = self.create_rounded_label(f"Rishabh adasd dasd {i}\n"*10, self_send=a)
            self.msg_grid.add_widget(msg)
            
        
        
        
        self.inp_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=5)
        self.inp = TextInput(size_hint=(0.7, 1), font_size='30sp')
        self.send_btn = Button(text="Send", font_size=50, size_hint=(0.3,1))
        self.inp_box.add_widget(self.inp)
        self.inp_box.add_widget(self.send_btn)
        
        self.grid.add_widget(self.inp_box)

        return self.grid
        

MyAppApp().run()