from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.list import MDListItem
from kivymd.uix.screen import MDScreen

class DListItem(MDListItem):
    icon = StringProperty()
    text = StringProperty()

class SettingsScreen(MDScreen):
    pass     
        
               
Builder.load_string("""
<DListItem>
    divider: True
    
    MDListItemLeadingIcon: 
        icon: root.icon
        icon_color: app.theme_cls.primaryColor
        padding: 15, 0, 0, 0
        theme_font_size: "Custom"
        font_size: "28sp"
                
    MDListItemHeadlineText:
        text: root.text
        padding: 15, 0, 0, 0

<SettingsScreen>
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        pos_hint: {"center_y": 1}
        
        MDIcon:
            icon: "cog"
            theme_font_size: "Custom"
            font_size: root.width * 0.35
            padding: 0, 75, 0, 100
            pos_hint: {"center_x": 0.5}
            disabled: True
            
        DListItem:
            icon: "lock"
            text: "App Lock"
            
        DListItem:
            icon: "palette"      
            text: "Theme & Style"
            on_release: app.router.go_to("theme_and_style_screen")       
            
        DListItem:
            icon: "file-export"
            text: "Export Entries"   
""")


def test():
    class App(MDApp):          
        def build(self):   
            return SettingsScreen()  
       
    App().run()
    
#test()    