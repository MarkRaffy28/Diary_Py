import os
import json

from kivymd.app import MDApp


class SettingsService:
    def __init__(self):
        self.default_path = "app/data/default_settings.json"
        self.user_path = "app/data/user_settings.json"
        self.fonts_path = "assets/fonts/"
        self.settings = {}
        
        self.load()
    
    
    #-----------------------------
    # LOAD SETTINGS  
    #-----------------------------
    
    # Load default and user settings 
    def load(self) -> None:
        self.settings = self._load_json(self.default_path)
        user_settings = self._load_json(self.user_path)
        if user_settings:
            self.settings.update(user_settings)

        self.apply_theme()
        self.apply_font()

    # Helper to safely load a JSON file
    def _load_json(self, path: str) -> dict[str, str]:
        if os.path.exists(path):
            try: 
                with open(self.path, "r") as file:
                    return json.load(file)
            except:
                print(f"Warning: Failed to parse JSON file:  {path}")
        return {}
                
    
    #-----------------------------
    # THEME  
    #-----------------------------
     
    # Apply theme to current running app
    def apply_theme(
        self, 
        theme_style: str = None,
        primary_palette: str = None
    ) -> None:
        
        app = MDApp.get_running_app()
        if not app:
            return
            
        if theme_style:
            self.settings["theme_style"] = theme_style
        if primary_palette:
            self.settings["primary_palette"] = primary_palette
                        
        app.theme_cls.theme_style = self.settings.get("theme_style", "Light")
        app.theme_cls.primary_palette = self.settings.get("primary_palette", "Blue")
      
        self._save_user_settings()     
            

    # -----------------------------
    # FONTS
    # -----------------------------
    
    # Return available fonts from fonts_path
    def get_fonts(self) -> dict[str, str]:
        if not os.path.exists(self.fonts_path):
            return {}
    
        fonts_dict = {}
        for f in os.listdir(self.fonts_path):
            if f.lower().endswith((".ttf", ".otf")):
                display_name = os.path.splitext(f)[0].replace("_", " ").title()
                fonts_dict[display_name] = f
    
        return fonts_dict                      
     
    # Apply font to app theme manager                        
    def apply_font(self, font_name: str=None) -> None:
        app = MDApp.get_running_app()
        if not app:
            return
    
        # Use font from settings if not provided
        font_name = font_name or self.settings.get("font_name", None)
        if not font_name:
            return  # no font to apply
    
        font_file = os.path.join(self.fonts_path, font_name)
    
        if not os.path.exists(font_file):
            print(f"Font file not found: {font_file}")
            return
    
        # Save font name to settings
        self.settings["font_name"] = font_name
    
        # Apply font to all font styles in KivyMD2
        for style_name, style_def in app.theme_cls.font_styles.items():
            # Skip icons
            if style_name == "Icon":
                continue
            
            # Update top-level font_name
            style_def["font_name"] = font_file
    
            # Update sub-level sizes if they exist
            for size_key in ("large", "medium", "small"):
                if size_key in style_def and isinstance(style_def[size_key], dict):
                    style_def[size_key]["font-name"] = font_file
    
        # Save updated settings
        self._save_user_settings()
                                
    # -----------------------------
    # INTERNAL
    # -----------------------------
    
    # Save current settings to user file.
    def _save_user_settings(self) -> None:
        os.makedirs(os.path.dirname(self.user_path), exist_ok=True)
        with open(self.user_path, "w") as file:
            json.dump(self.settings, file, indent=2)
