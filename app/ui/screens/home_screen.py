from kivymd.app import MDApp
from kivy.lang import Builder

from kivymd.uix.screen import MDScreen

class HomeScreen(MDScreen):
    pass
    
Builder.load_string("""
<HomeScreen>
    md_bg_color: app.theme_cls.backgroundColor

    MDLabel:
        theme_text_color: "Primary"
        text: f"{self.font_size / sp(1)} {self.font_name} {self.line_height} "
        halign: "center"
        
    MDButton:
        MDButtonText:
            text: "I am a button!"        
""")

"""
class App(MDApp):  
    def build(self):  
        return HomeScreen()  
  
App().run()
"""