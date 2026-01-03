from kivy.lang import Builder  
from kivy.properties import StringProperty, BooleanProperty  

from kivy.uix.screenmanager import SlideTransition  
from kivy.uix.boxlayout import BoxLayout  
from kivymd.uix.behaviors import RectangularRippleBehavior  
from kivy.uix.behaviors import ButtonBehavior  
from kivymd.uix.screen import MDScreen  
from kivymd.uix.navigationbar import MDNavigationBar  
from kivymd.uix.label import MDLabel  
from kivymd.uix.button import MDIconButton  
from kivymd.app import MDApp  
from kivy.metrics import dp  

def ti():
    import os
    import sys
    
    # Add the project root to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

ti()

from app.ui.screens.home_screen import HomeScreen
from app.ui.screens.calendar_screen import CalendarScreen
from app.ui.screens.settings_screen import SettingsScreen   
      
# Custom navigation item  
class CustomNavItem(RectangularRippleBehavior, ButtonBehavior, BoxLayout):  
    text = StringProperty("")  
    filled_icon = StringProperty("")  
    outlined_icon = StringProperty("")  
    active = BooleanProperty(False)  

class MainScreen(MDScreen):  
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        self.last_index = 0  
        self.tab_order = ["Home", "Calendar", "Settings"]  
  
    def on_switch_tabs(self, item: CustomNavItem):  
        sm = self.ids.screen_manager  
        new_index = self.tab_order.index(item.text)  
      
        # Determine slide direction  
        direction = "left" if new_index > self.last_index else "right"  
        sm.transition = SlideTransition(direction=direction, duration=0.3)  
      
        # Switch screen  
        sm.current = item.text  
        self.last_index = new_index  
      
        # Update active states  
        nav_bar = item.parent  
        for child in nav_bar.children:  
            if isinstance(child, CustomNavItem):  
                child.active = child == item  
      
      
Builder.load_string('''  
<CustomNavItem>:  
    orientation: "vertical"  
    size_hint_y: None  
    height: self.parent.height 
    padding: 0  
    spacing: 2  
    
    MDIcon:  
        id: icon  
        icon: root.filled_icon if root.active else root.outlined_icon  
        # icon_color: self.theme_cls.primaryColor
        md_bg_color: self.theme_cls.primaryColor
        pos_hint: {"center_x": 0.5}  
        user_font_size: "24sp"  
  
    MDLabel:  
        id: label  
        text: root.text
        text_color:  self.theme_cls.primaryColor
        bold: root.active
        halign: "center"  
        size_hint_y: None  
        height: self.texture_size[1] if root.active else self.texture_size[1] * 0.75
        opacity: 1 if root.active else 0  
        padding: 0, 0, 0, dp(8)
  
<MainScreen>:  
    MDBoxLayout:  
        orientation: "vertical"  
        md_bg_color: self.theme_cls.backgroundColor  
  
        MDScreenManager:  
            id: screen_manager  
  
            HomeScreen:  
                name: "Home"  
  
            CalendarScreen:  
                name: "Calendar"  
  
            SettingsScreen:  
                name: "Settings"  
  
        MDNavigationBar:  
            size_hint_y: None  
            height: dp(56)   
  
            CustomNavItem:  
                filled_icon: "home"  
                outlined_icon: "home-outline"  
                text: "Home"  
                on_release: root.on_switch_tabs(self)  
                active: True  
  
            CustomNavItem:  
                filled_icon: "calendar-month"  
                outlined_icon: "calendar-month-outline"  
                text: "Calendar"  
                on_release: root.on_switch_tabs(self)  
  
            CustomNavItem:  
                filled_icon: "cog"  
                outlined_icon: "cog-outline"  
                text: "Settings"  
                on_release: root.on_switch_tabs(self)  
''')  

def test():
    class App(MDApp):          
        def build(self):   
            return MainScreen()  
       
    App().run()
    
test()    