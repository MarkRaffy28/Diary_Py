from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import hex_colormap

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from kivymd.uix.selectioncontrol import MDSwitch

class DBasicList(MDBoxLayout):
    pass
    
class DBorderedBox(MDBoxLayout):
    pass   

class DSwitch(MDSwitch):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self._try_disable_thumb, 0)

    # Disable switch thumb button interaction
    def _try_disable_thumb(self, dt):
        # Thumb is created lazily in KivyMD
        if hasattr(self, "thumb") and self.thumb:
            self.thumb.disabled = True
            return False  # stop scheduling
    
    # Use switch track to change state
    def on_touch_up(self, touch):
        if self.disabled:
            return False
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return super().on_touch_up(touch)

class ThemeAndStyleScreen(MDScreen):
    def on_kv_post(self, *args):
        app = MDApp.get_running_app()
        self.ids.dark_switch.active = (
            app.theme_cls.theme_style == "Dark"
        )
        
        self.display_font_list()
             
    def enable_dark_mode(self, switch, value):
         app = MDApp.get_running_app()
        
         theme_style = "Dark" if value else "Light"
         app.settings_service.apply_theme(theme_style=theme_style)   

        
    # THEME
         
    # Adds drop-down items based on list of color names     
    def open_dropdown_colors(self, item):
        MDDropdownMenu(
            caller=item,
            items=[
                {
                    "text": color,
                    "on_release": lambda x=color: self.set_color_theme(x),
                }
                for color in [c.capitalize() for c in hex_colormap.keys()]
            ],
            hor_growth="left",
        ).open()

    # Called when an item in drop-down is clicked
    def set_color_theme(self, color_name):
        self.ids.color_text.text = color_name
        
        app = MDApp.get_running_app()
        app.settings_service.apply_theme(primary_palette=color_name)  
        
    def display_font_list(self):
        app = MDApp.get_running_app()
        list = app.settings_service.get_fonts()  
        self.ids.font_list.text = str(list)
    
    # FONTS
    def open_dropdown_fonts(self, item):
        app = MDApp.get_running_app()
    
        self.font_menu = MDDropdownMenu(
            caller=item,
            items=[
                {
                    "text": display_name,
                    "on_release": lambda x=font_name, d=display_name: self.set_font(d, x),
                }
                for display_name, font_name
                in app.settings_service.get_fonts().items()
            ]
        )
        self.font_menu.open()
    
    # Sets font to app theme
    def set_font(self, display_name, font_name):
        app = MDApp.get_running_app()    
        app.settings_service.apply_font(font_name=font_name)      
        
        # Change preview font
        self.ids.text_style_preview.font_name = font_name
                      
        
Builder.load_string("""
<DBasicList@MDBoxLayout>
    padding: dp(15), dp(15), dp(15) ,dp(15)
    size_hint_y: None
    height: self.minimum_height    

<DSwitch>
    icon_active: "check"

<ThemeAndStyleScreen>
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            theme_bg_color: "Custom"
            md_bg_color: app.theme_cls.primaryContainerColor
            size_hint_y: None
            height: dp(56)
            
            MDTopAppBarLeadingButtonContainer:    
                
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    #on_release: app.router.on_back()          
        
            MDTopAppBarTitle:
                text: "Theme & Style Settings"
  
        DBasicList:             
            MDLabel:
                text: "Dark Theme"
                font_style: "Title"
                                      
            DSwitch:
                id: dark_switch
                on_active: root.enable_dark_mode(self, self.active)      
                                
            
        DBasicList:
            MDLabel:
                text: "Theme"         
                font_style: "Title"        
                     
            MDDropDownItem:
                on_release: root.open_dropdown_colors(self)
                    
                MDDropDownItemText:
                    id: color_text
                    text: app.theme_cls.primary_palette    
                    theme_font_size: "Custom" 
                    font_size: dp(18)                
  
      
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(25)
            size_hint_y: None
            height: self.minimum_height
            padding: dp(15), dp(30), dp(15) ,dp(15)
                    
            MDLabel:
                text: "Text Styling"
                font_style: "Title"
                
            MDCard:
                style: "outlined"
                size_hint_y: None
                height: text_style_preview.texture_size[1] 
                
                MDLabel:
                    id: text_style_preview
                    text: "Latin / 한국어 / カタカナ / [b]bold[/b] / [i]italic[/i] /  [u]underline[/u] /  [s]strikethrough[/s] /  [b][i]bolditalic[/b]"
                    markup: True
                    multiline: True
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding: dp(12)
                            
                    


         
                                
                                                               
                                                                                              
                                                                                                                                                            
        MDDropDownItem:
            id: dropdown_font
            on_release: root.open_dropdown_fonts(self)
                
            MDDropDownItemText:
                id: font_text
                text: "Select Font"
                theme_font_size: "Custom" 
                font_size: dp(40)       
        
        MDLabel:
            id: font_list
            halign: "center"
            
        ScrollView:
            
            MDLabel:
                text: str(app.theme_cls.font_styles)
                halign: "center"
                allow_copy: True
            
        MDLabel:
            text: "#{:02X}{:02X}{:02X}{:02X}".format(*(int(c*255) for c in self.theme_cls.surfaceContainerColor))
            halign: "center"       
            allow_copy: True     
            
        MDLabel:
            text: "Primary Color" + "#{:02X}{:02X}{:02X}{:02X}".format(*(int(c*255) for c in self.theme_cls.primaryColor))
            halign: "center"       
            allow_selection: True                 

        MDLabel:
            text: "BG" + "#{:02X}{:02X}{:02X}{:02X}".format(*(int(c*255) for c in self.theme_cls.backgroundColor))
            halign: "center"       
            allow_selection: True       
            bold: True          
            

        MDButton:
            style:"outlined"
            on_release: root.set_theme_style("Blue")   
            
            MDButtonText:
                text: "Reset default settings."

""")    

def test():
    import sys
    import os
    
    # Add the project root to sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    
    # Now import the service
    from app.services.settings_service import SettingsService

    class App(MDApp):          
        def build(self):   
            app = self
            
            app.settings_service = SettingsService()
        
            return ThemeAndStyleScreen()  
       
    App().run()
    
test()