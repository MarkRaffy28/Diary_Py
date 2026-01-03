from kivymd.app import MDApp
from kivy.lang import Builder

from kivymd.uix.screen import MDScreen

class CalendarScreen(MDScreen):
    pass
    
Builder.load_string("""
<CalendarScreen>

    MDLabel:
        text: "Calendar "
        halign: "center"
""")
