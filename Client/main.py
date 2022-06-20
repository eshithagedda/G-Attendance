from threading import Thread
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.app import Builder
import socket
import json
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.camera import Camera
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import time
from functools import partial
import weakref
import pickle


IP = '192.168.0.102'
PORT = 6666

details = []
codes = ['LOGIN']



class Login(Screen):
    def login_thread(self):
        t = Thread(target=Login.login, args = (self,))
        t.daemon = True
        t.start()

    def change_screen(self, screen, direction, dt):
        QRAttendance.build.kv.current = screen
        QRAttendance.build.kv.transition.direction = direction

    def login(self):        
        username = self.ids.username.text
        password = self.ids.password.text
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP,PORT))

        s.send(bytes(codes[0],'utf-8'))
        
        cred = s.recv(10000)
        cred = cred.decode('utf-8')

        cred = json.loads(cred)
        
        index = None
        for i in range(0,len(cred)):
            
            user = cred[i]["Username"]
            passw = cred[i]["Password"]

            if user == username and passw == password:
                self.ids.username.error = False
                self.ids.password.error = False
                s.send(bytes('SUCCESS','utf-8'))
                details.append(cred[i])
                index = 1

                Clock.schedule_once(partial(self.change_screen,'menu','left'),0.000001)                

                                

        if index == None:
            self.ids.username.error = True
            self.ids.password.error = True


class Menu(Screen):
    layout = StackLayout(size_hint=(1, None),orientation='rl-tb', spacing=20)
    layout.bind(minimum_height=layout.setter('height'))

    root = ScrollView(size_hint=(1, 0.7), effect_cls=ScrollEffect)
    root.add_widget(layout)
 
    def on_enter(self, *args):
        self.profile = Image(
            source = 'Images\\pfp.png',
            pos_hint = {'center_x':0.5,'center_y':0.9}
        )

        self.username = Label(
            text = details[0]["Name"],
            bold = True,
            pos_hint = {'center_x':0.5,'center_y':0.8}
        )

        self.email = Label(
            text = details[0]["Email"],
            font_size = 14,
            pos_hint = {'center_x':0.5,'center_y':0.77}
        )

        self.add_widget(self.profile)
        self.add_widget(self.username)
        self.add_widget(self.email)
        
        for i in range(0, len(details[0]["Classes"])):          
            Class = Label(text=details[0]["Classes"][i],
                        markup= True,
                        padding= [15,15],
                        size_hint=(1,None),
                        halign="left", 
                        valign="middle")

            Class.bind(size=Class.setter('text_size')) 
            Class._label.refresh()
            Class.height= (Class._label.texture.size[1] + 2*Class.padding[1])

            card = MDCard(
                style='elevated',
                size_hint=(1, None),
                height=Class.height,
                focus_behavior= True,
                ripple_behavior= True,
                on_release=lambda a:self.take_attendance()
            )


            self.layout.add_widget(card)
            card.add_widget(Class)
            
            #self.ids[f"a{i}"] = weakref.ref(Class)
            

        try:
            self.add_widget(self.root)
        except:
            print("[ERROR] Couldn't add root widget, reason: root widget already exists.")
 
        return super().on_enter(*args)

    def logout(self):
        self.remove_widget(self.profile)
        self.remove_widget(self.username)
        self.remove_widget(self.email)

        global details
        details = []

        for child in [child for child in self.layout.children]:
            self.layout.remove_widget(child)

        QRAttendance.build.kv.current = 'login'
        QRAttendance.build.kv.transition.direction = 'right'



    def take_attendance(self):
        self.remove_widget(self.profile)
        self.remove_widget(self.username)
        self.remove_widget(self.email)

        for child in [child for child in self.layout.children]:
            self.layout.remove_widget(child)


        QRAttendance.build.kv.current = 'att'
        QRAttendance.build.kv.transition.direction = 'left'





class Attendance(Screen):
    def initiate_capture(self):
        self.image = Image()
        self.add_widget(self.image)

        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.detector = cv2.QRCodeDetector()
        self.loader = Clock.schedule_interval(self.load_video, 1.0/30.0)

    def on_enter(self, *args):
        self.initiate_capture()

        return super().on_enter(*args)

    def load_video(self, *args):
        ret, frame = self.capture.read()
        self.image_frame = frame

        self.buffer = cv2.flip(self.image_frame, 0).tobytes()
        texture = Texture.create(size=(self.image_frame.shape[1], self.image_frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(self.buffer, colorfmt='bgr',bufferfmt = 'ubyte')

        self.image.texture = texture

        self.data, bbox, _  = self.detector.detectAndDecode(self.image_frame)

        if self.data: #qr detected
            pickledData = pickle.dumps(self.data)
            print(pickledData)

            self.clear_cam_cache()
            self.mark_attendance()

    def clear_cam_cache(self):
        self.remove_widget(self.image)
        cv2.destroyAllWindows()
        self.capture = None
        self.detector = None
        self.loader.cancel()
        self.buffer = None
        self.ids.scan_button.disabled = False


    def mark_attendance(self):
        self.scan_complete_dialog = MDDialog(
            text = f'Marked attendance for: {self.data}'
        )

        self.scan_complete_dialog.open()

    def back(self):
        #clearing cache memory
        self.remove_widget(self.image)
        cv2.destroyAllWindows()
        self.capture = None
        self.detector = None
        self.loader.cancel()
        self.buffer = None
        self.ids.scan_button.disabled = True

        QRAttendance.build.kv.current = 'menu'
        QRAttendance.build.kv.transition.direction = 'right'

class WindowManager(ScreenManager):
    pass

class QRAttendance(MDApp):
    def __init__(self, **kwargs):
        self.title = "G-Attendance"
        super().__init__(**kwargs)



    def build(self):
        QRAttendance.build.kv = Builder.load_file('app.kv')
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        return QRAttendance.build.kv


if __name__ == '__main__':
    QRAttendance().run()

