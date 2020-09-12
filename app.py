from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import maps

config = maps.getconfig()

class StartScreen(Screen):
    pass

class SelectTypeScreen(Screen):
    pass

class SelectPlaceScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my.kv")


class MyMainApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MyMainApp().run()