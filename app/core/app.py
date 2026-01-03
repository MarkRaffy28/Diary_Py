from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp

from app.core.router import AppRouter
from app.services.settings_service import SettingsService

class DiaryApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize
        self.sm = ScreenManager()
        self.router = AppRouter(self.sm)
        self.settings_service = SettingsService()
               

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        #Binds keyboard to on_back
        Window.bind(on_keyboard=self._on_back)
        Window.fullscreen = True
        
        self.router.register_screens()
        return self.sm
        
    def on_start(self):
        pass
        
    # Listens to back or esc fires
    def _on_back(self, window, key, *args):
        # Android back
        if key == 27:  
            return self.router.on_back()
        return False        