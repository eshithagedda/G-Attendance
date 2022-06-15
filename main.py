import kivy
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.app import Builder

class Login(Screen):
    def callback(self):
        Scanner.build.kv.current = 'scanner'
        Scanner.build.kv.transition.direction = 'right'

class Scanner(Screen):
    def callback(self):
        Scanner.build.kv.current = 'login'
        Scanner.build.kv.transition.direction = 'right'

    def logout(self):
        Scanner.build.kv.current = 'logout'
        Scanner.build.kv.transition.direction = 'left'

class Logout(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class Scanner(MDApp):
    def __init__(self, **kwargs):
        self.title = "G-Attendance"
        super().__init__(**kwargs)

    def build(self):
        Scanner.build.kv = Builder.load_file("main.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        
        return Scanner.build.kv

if __name__ == "__main__":
    Scanner().run()