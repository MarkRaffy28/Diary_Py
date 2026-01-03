from kivy.lang import Builder  
from kivy.properties import BooleanProperty, NumericProperty, StringProperty

from kivy.uix.screenmanager import SlideTransition   
from kivymd.uix.screen import MDScreen  
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
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
class CustomNavItem(MDNavigationItem):  
    text = StringProperty("")  
    filled_icon = StringProperty("")  
    outlined_icon = StringProperty("")  

class MainScreen(MDScreen):         
    _swipe_threshold = NumericProperty(dp(50))
    _touch_start_x = NumericProperty(0)
    
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        self.last_index = 0  
        self.tab_order = ["Home", "Calendar", "Settings"]  
      
    
    # Returns the name of the active tab
    def get_active_tab(self):
        tab = next((child for child in self.ids.bottom_nav.children if child.active), None)
        return tab.text
    
    
    # Switches tabs and determines transition direction
    def on_switch_tabs(self, item: CustomNavItem):  
        sm = self.ids.screen_manager  
        new_index = self.tab_order.index(item.text)  
      
        # Determine slide direction  
        direction = "left" if new_index > self.last_index else "right"  
        sm.transition = SlideTransition(direction=direction, duration=0.3)  
      
        # Switch screen  
        sm.current = item.text  
        self.last_index = new_index  
        
        
    # Sets the current active tab
    def set_active_tab(self, tab_name):
        for tab in self.ids.bottom_nav.children:
            if getattr(tab, "text", None) == tab_name:
                tab.dispatch('on_release')
                break
      

    # Swipe navigation methods
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start_x = touch.x
        return super().on_touch_down(touch)
    
  
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            swipe_distance = touch.x - self._touch_start_x
            
            # Check if swipe distance exceeds threshold
            if abs(swipe_distance) > self._swipe_threshold:
                current_index = self.last_index
                
                # Swipe right -> go to previous tab
                if swipe_distance > 0 and current_index > 0:
                    new_tab = self.tab_order[current_index - 1]
                    self.set_active_tab(new_tab)
                
                # Swipe left -> go to next tab
                elif swipe_distance < 0 and current_index < len(self.tab_order) - 1:
                    new_tab = self.tab_order[current_index + 1]
                    self.set_active_tab(new_tab)
        
        return super().on_touch_up(touch)      
        
         
Builder.load_string('''  
<CustomNavItem>:  
    orientation: "vertical"  
    size_hint_y: None  
    height: self.parent.height 
    padding: 0  
    #spacing: 29
    
    MDNavigationItemIcon:  
        id: icon  
        icon: root.filled_icon if root.active else root.outlined_icon  
        pos_hint: {"center_x": 0.5, "center_y": 0.8}  if root.active else {"center_x": 0.5, "center_y": 0.5}
        user_font_size: "24sp"  
  
    MDNavigationItemLabel:  
        id: label  
        text: root.text
        bold: root.active
        # halign: "center"  
        pos_hint: {"center_y": -0.2}
        opacity: 1 if root.active else 0 
  
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
            id: bottom_nav
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
    
#test()    