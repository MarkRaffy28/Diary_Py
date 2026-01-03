from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget
from kivy.utils import hex_colormap
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText, 
    MDDialogButtonContainer
)
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


class DBasicList(MDBoxLayout):
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


class NotebookLabel(MDLabel):
    enable_lines = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            size=self.update_lines, 
            pos=self.update_lines,
            font_size=self.update_lines,
            enable_lines=self.update_lines,
        )
        
    def update_lines(self, *args):
        self.canvas.before.clear()
        
        # Stop if enable_lines is set to False
        if not self.enable_lines:
            return
        
        with self.canvas.before:
            app = MDApp.get_running_app()
            # Semi-transparent line color
            Color(
                app.theme_cls.onSurfaceColor[0],
                app.theme_cls.onSurfaceColor[1],
                app.theme_cls.onSurfaceColor[2],
                0.3
            )
            
            # Calculate line spacing based on font size
            line_spacing = self.font_size * self.line_height #@# + (self.font_size * 0.176)
            
            # Calculate how many lines based on texture height
            if line_spacing > 0:
                num_lines = int(self.texture_size[1] / line_spacing) + 1
                
                # Draw lines from bottom up, aligned with text baselines
                for i in range(num_lines):
                    y_pos = self.y + self.padding[1] + (i *  line_spacing) + (self.font_size * 0.4)
                    if y_pos < self.top:
                        Line(
                            points=[
                                self.x + self.padding[0], y_pos,
                                self.right - self.padding[2], y_pos
                            ],
                            width=1
                        )

class ThemeAndStyleScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, 
            select_path=self.select_path,
            ext=[".zip"]
        )
        
        
    def on_kv_post(self, *args):
        app = MDApp.get_running_app()
        self.ids.dark_switch.active = (
            app.theme_cls.theme_style == "Dark"
        )
        
        slider = self.ids.font_size_slider
        slider.bind(
            on_touch_up=lambda s, t: self.on_slider_touch_up(s, t)
        )        
        
        scroll_view = self.ids.scroll_view
        scroll_content = self.ids.scroll_content

        # Whenever either the content height or the scrollview size changes, update scrolling
        scroll_content.bind(height=self._update_scroll)
        scroll_view.bind(size=self._update_scroll)

        # run once to initialize correct state
        self._update_scroll()
          
             
    def enable_dark_mode(self, switch, value):
         app = MDApp.get_running_app()
        
         theme_style = "Dark" if value else "Light"
         app.settings_service.apply_theme(theme_style=theme_style)   

        
    # THEME
         
    # Adds drop-down items based on list of color names     
    def open_dropdown_colors(self, item):
        app = MDApp.get_running_app()
        
        # Get current font name from theme manager
        app.current_theme= app.theme_cls.primary_palette
        
        MDDropdownMenu(
            caller=item,
            items=[
                {
                    "text": color,
                     "trailing_icon": "check" if app.current_theme == color else "", #adds check icon for current theme
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
        
   
    # FONTS
    def open_dropdown_fonts(self, item):
        app = MDApp.get_running_app()
        
        # Get current font name from theme manager
        app.current_font = app.theme_cls.font_styles["Title"]["medium"]["font-name"].replace("_", " ")
    
        self.font_menu = MDDropdownMenu(
            caller=item,
            items=[
                {
                    "text": "Upload font",
                    "leading_icon": "file-upload",
                    "text_color": app.theme_cls.onSurfaceVariantColor,
                    "leading_icon_color": app.theme_cls.onSurfaceVariantColor,
                    "on_release": lambda: self.file_manager_open()
                },
                *[
                    {
                        "text": font_name,
                        "trailing_icon": "check" if app.current_font == font_name else "", #adds check icon for current font
                        "on_release": lambda x=font_name: self.set_font(x),
                    }
                    for font_name
                    in ["Roboto"] + app.settings_service.get_fonts() # adds Roboto as first item
                ],
                {
                    "text": "Delete all fonts",
                    "leading_icon": "trash-can",
                    "text_color": app.theme_cls.errorColor,
                    "leading_icon_color": app.theme_cls.errorColor,
                    "on_release": lambda: self._delete_all_fonts()
                },
            ]
        )
        self.font_menu.open()
    
    # Sets font to app theme
    def set_font(self, font_name):
        app = MDApp.get_running_app()    
        app.settings_service.apply_font(font_name=font_name)      
        
        # Change preview font
        self.ids.text_style_preview.font_name = font_name
       
       
    # Opens file manager 
    def file_manager_open(self):
        if platform == "android":
            default_file_path = "/storage/emulated/0"
        elif platform == "win":
            default_file_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        else:
            default_file_path = "/"
            
        self.file_manager.show(default_file_path)
        self.manager_open = True

    # Called when a file is selected 
    def select_path(self, path: str):
        app = MDApp.get_running_app()    
        
        self.exit_manager()
        MDSnackbar(
            MDSnackbarText(
                text=app.settings_service.extract_font_zip(zip_path=path)
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()

    # Called when the user reaches the root of the directory tree
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
       
    # Called when buttons are pressed on the mobile device         
    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
                return True
        return False       
        
    
    # Called when user stops dragging to font size slider                       
    def on_slider_touch_up(self, slider, touch):
        if touch.grab_current is slider:
            app = MDApp.get_running_app()
            
            app.settings_service.apply_font_size(font_size=slider.value)        
    
    
    # Deletes all uploaded fonts
    def _confirm_delete_all_fonts(self):
        app = MDApp.get_running_app()    

        MDSnackbar(
            MDSnackbarText(
                text=app.settings_service.delete_all_fonts()
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()
        
        self.ids.text_style_preview.font_name = "Roboto"
    
    # Prompts user to confirm deleting all uploaded fonts
    def _delete_all_fonts(self):
        dialog = MDDialog(
            MDDialogIcon(
                icon="trash-can",
            ),
            MDDialogHeadlineText(
                text="Delete All Fonts?",
            ),
            MDDialogSupportingText(
                text="This will delete all your uploaded fonts. This action cannot be undone.",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda *_: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Confirm"),
                    style="text",
                    on_release=lambda *_: (
                        dialog.dismiss(),
                        self._confirm_delete_all_fonts()
                    )
                ),
                spacing="8dp",
            ),
            size_hint=(0.9, None),
        )
        dialog.open()
  
                                                           
    # Enables scrolling if scroll content exceeds viewport
    def _update_scroll(self, *args):
        scroll_view = self.ids.scroll_view
        scroll_content = self.ids.scroll_content

        # Enable vertical scrolling only if content is taller than the ScrollView
        scroll_view.do_scroll_y = scroll_content.height > scroll_view.height
        scroll_view.do_scroll_x = False

        # if not scrollable, lock at top (prevents weird offsets)
        if not scroll_view.do_scroll_y:
            scroll_view.scroll_y = 1.0  
            
                                        
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
        id: box
        orientation: "vertical"
        
        MDTopAppBar:
            theme_bg_color: "Custom"
            md_bg_color: app.theme_cls.primaryContainerColor
            size_hint_y: None
            height: dp(56)
                
            MDTopAppBarLeadingButtonContainer:    
                    
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: app.router.on_back(reload_all=True)          
            
            MDTopAppBarTitle:
                text: "Theme & Style Settings"
                    
        ScrollView:     
            id: scroll_view
            size_hint_y: 1
            
            MDBoxLayout:
                id: scroll_content
                orientation: "vertical"
                adaptive_height: True
                                     
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
                            font_size: sp(16)                
          
              
                MDBoxLayout:
                    orientation: "vertical"        
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(15)
                            
                    MDLabel:
                        text: "Text Styling"
                        font_style: "Title"
                        size_hint_y: None
                        height: self.texture_size[1]
                        padding: dp(0), dp(0), dp(0), dp(5) 
                        
                    MDCard:
                        style: "outlined"
                        size_hint_y: None
                        height: text_style_preview.texture_size[1]
                        
                        NotebookLabel:
                            id: text_style_preview
                            text: f"Latin / {str(int(font_size_slider.value))} / 한국어 / 漢字 / カタカナ / [b]bold[/b] / [i]italic[/i] / [u]underline[/u] /  [s]strikethrough[/s] / [b][i]bolditalic[/b][/i]"
                            markup: True
                            multiline: True
                            size_hint_y: None
                            height: self.texture_size[1]
                            padding: dp(12)
                            theme_font_size: "Custom"
                            font_size: int(sp(font_size_slider.value))
                            
                                        
                    MDBoxLayout:
                        size_hint_y: None
                        height: self.minimum_height
                        
                        MDIcon:
                            icon: "format-size"
                            adaptive_height: True
                            pos_hint: {"center_y": 0.5}
                            theme_icon_color: "Custom"
                            icon_color: app.theme_cls.primaryColor 
                            
                        MDSlider:
                            id: font_size_slider
                            value: app.settings_service.get_current_font_size()
                            min: 10
                            max: 50
                            pos_hint: {"center_y": 0.5}
                            
                            MDSliderHandle:
                            MDSliderValueLabel:
                                #size: [dp(27), dp(27)]
                                                                         
                        MDIconButton:
                            icon: "format-font"
                            radius: [dp(3)]
                            on_release: root.open_dropdown_fonts(self)                            
                            
                    
                 
                
                                                                       
                                                                                                 
                
                                                
                
        
                MDButton:
                    style:"outlined"
                    on_release: root.set_theme_style("Blue")   
                    
                    MDButtonText:
                        text: "Reset default settings."
                MDButton:
                    style:"outlined"
                    on_release: root.set_theme_style("Blue")   
                    
                    MDButtonText:
                        text: "Reset default settings."
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
    
#test()