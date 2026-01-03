import os
import json
import zipfile
import shutil

from kivy.core.text import LabelBase
from kivy.metrics import sp
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

        self._register_fonts()
        self.apply_theme()
        self.apply_font()
        self.apply_font_size()


    # Helper to safely load a JSON file
    def _load_json(self, path: str) -> dict[str, str]:
        if os.path.exists(path):
            try: 
                with open(path, "r") as file:
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
    
    # Apply font to app's theme manager      
    def apply_font(self, font_name: str=None) -> None:
        app = MDApp.get_running_app()
        if not app:
            return
    
        # Use font from settings if not provided
        font_name = (font_name.replace(" ", "_") if font_name else None) or self.settings.get("font_name", None)
        if not font_name:
            return  # no font to apply
    
        # Save font name to settings
        self.settings["font_name"] = font_name
       
        # Apply font to all font styles
        for style_name, style_def in app.theme_cls.font_styles.items():
            # Skip icons
            if style_name == "Icon":
                continue
            
            # Update top-level font_name
            style_def["font_name"] = font_name
    
            # Update sub-level sizes if they exist
            for size_key in ("large", "medium", "small"):
                if size_key in style_def and isinstance(style_def[size_key], dict):
                    style_def[size_key]["font-name"] = font_name           
    
        # Save updated settings
        self._save_user_settings()                     
    
    
    # Apply font size to app's theme manager    
    def apply_font_size(self, font_size: float=None) -> None:
        app = MDApp.get_running_app()
        if not app:
            return
                
        # Use font size  from settings if not provided
        font_size = font_size or self.settings.get("font_size", None)
        if not font_size:
            return  # no font size to apply
    
        # Save font size to settings
        self.settings["font_size"] = font_size
       
        # Apply font to all "Body" -> "large" style
        app.theme_cls.font_styles["Body"]["large"]["font-size"] = int(sp(font_size))
    
        # Save updated settings
        self._save_user_settings()         
                 
    
    # Deletes all uploaded fonts from fonts_path
    def delete_all_fonts(self) -> str:
        if not os.path.isdir(self.fonts_path):
            return "Font directory not found."
    
        deleted = 0
        errors = []
    
        for name in os.listdir(self.fonts_path):
            font_dir = os.path.join(self.fonts_path, name)
    
            # Only delete folders (fonts are stored as folders)
            if not os.path.isdir(font_dir):
                continue
    
            try:
                shutil.rmtree(font_dir)
                deleted += 1
            except Exception:
                errors.append(name)
    
        # Clear cached font list if you keep one
        if hasattr(self, "fonts_fonts"):
            self.fonts_fonts.clear()
    
        if deleted == 0:
            return "No fonts to delete."
    
        if errors:
            return f"Deleted {deleted} fonts. Failed: {', '.join(errors)}"
        
        self.apply_font(font_name="Roboto") 
        self._register_fonts()
        return f"Deleted {deleted} fonts successfully."
    
    
    # Extracts a user-provided font ZIP into fonts_path    
    def extract_font_zip(self, zip_path: str) -> str:
        if not zipfile.is_zipfile(zip_path):
            return "Invalid ZIP file"
    
        font_name = os.path.splitext(os.path.basename(zip_path))[0]
        target_dir = os.path.join(self.fonts_path, font_name)
        tmp_dir = target_dir + "_tmp"
        
        shutil.rmtree(tmp_dir, ignore_errors=True)
        os.makedirs(tmp_dir, exist_ok=True)
    
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmp_dir)
    
            # Find the actual font folder (might be nested)
            font_folder = self._find_font_folder(tmp_dir, font_name)
            if not font_folder:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return "No font files found in ZIP"
    
            # Find required regular font file
            found_regular = self._find_file_by_style(font_folder, "regular")
            if not found_regular:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return "Missing required file: *-Regular.ttf"
    
            # Find all style variants
            styles = ["regular", "bold", "italic", "bolditalic"]
            font_files = []
            
            for style in styles:
                found_file = self._find_file_by_style(font_folder, style)
                if found_file:
                    font_files.append(found_file)
    
            # Create target directory and copy only font files
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)
    
            for font_file in font_files:
                filename = os.path.basename(font_file)
                shutil.copy2(font_file, os.path.join(target_dir, filename))
    
            # Cleanup temp directory
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
            self._register_fonts()
            return f"Font successfully added: {font_name}"
    
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return f"Font extraction failed: {e}"    
                                  
        
    # Returns the current font size
    def get_current_font_size(self) -> float:
        app = MDApp.get_running_app() 
        return int(app.theme_cls.font_styles["Body"]["large"]["font-size"] / sp(1))
                                                                   
    # -----------------------------
    # INTERNAL
    # -----------------------------
    
    # Case-insensitive search for filename in dirpath
    def _ci_exists(self, dirpath: str, filename: str) -> str | None:
        target_lower = filename.lower()
        for root, _, files in os.walk(dirpath):
            for f in files:
                if f.lower() == target_lower:
                    return os.path.join(root, f)
        return None
        
        
    # Returns a list of available font names (folders containing font files)
    def get_fonts(self) -> list[str]:
        if not os.path.exists(self.fonts_path):
            return []
    
        font_names = []
        for item in os.listdir(self.fonts_path):
            item_path = os.path.join(self.fonts_path, item)
            
            if os.path.isdir(item_path):
                # Include folder only if it contains at least one .ttf or .otf file
                if any(f.lower().endswith((".ttf", ".otf")) for f in os.listdir(item_path)):
                    display_name = item.replace("_", " ")
                    font_names.append(display_name)
        
        # Sort the font names alphabetically (case-insensitive)
        font_names.sort(key=str.lower)
    
        return font_names                

        
    # Find .ttf file matching style (e.g., 'regular', 'bold', 'italic'). Searches for common naming patterns without requiring font name.
    def _find_file_by_style(self, dirpath: str, style: str) -> str | None:
        style_lower = style.lower()
        
        # Common style naming patterns
        patterns = [
            f"-{style}.ttf",
            f"_{style}.ttf", 
            f" {style}.ttf"
        ]
        
        for root, _, files in os.walk(dirpath):
            for f in files:
                lf = f.lower()
                if not lf.endswith('.ttf'):
                    continue
                
                # Check exact patterns only
                for pattern in patterns:
                    if lf.endswith(pattern):
                        return os.path.join(root, f)
        
        return None
    
    
        # Find the actual font folder inside extracted ZIP.
    def _find_font_folder(self, tmp_dir: str, font_name: str) -> str | None:
        font_name_lower = font_name.lower()
        
        # Check if fonts are directly in tmp_dir
        ttf_files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.ttf')]
        if ttf_files:
            return tmp_dir
   
             
        # Search for subfolder matching font name
        for item in os.listdir(tmp_dir):
            item_path = os.path.join(tmp_dir, item)
            if os.path.isdir(item_path) and font_name_lower in item.lower():
                return item_path
        
        # Fallback: find first folder containing .ttf files
        for root, dirs, files in os.walk(tmp_dir):
            if any(f.lower().endswith('.ttf') for f in files):
                return root
        
        return None    
  
                      
    # Registers all fonts in fonts_path to Kivy's LabelBase.
    def _register_fonts(self) -> None:
        if not os.path.exists(self.fonts_path):
            return
    
        for folder in os.listdir(self.fonts_path):
            folder_path = os.path.join(self.fonts_path, folder)
            if not os.path.isdir(folder_path):
                continue
    
            # Prepare dict for LabelBase registration
            font_files = {
                "fn_regular": None,
                "fn_bold": None,
                "fn_italic": None,
                "fn_bolditalic": None
            }
    
            for file in os.listdir(folder_path):
                if not file.lower().endswith((".ttf", ".otf")):
                    continue
    
                file_path = os.path.join(folder_path, file)
                lower_file = file.lower()
    
                if "-regular" in lower_file:
                    font_files["fn_regular"] = file_path
                elif "-bolditalic" in lower_file:
                    font_files["fn_bolditalic"] = file_path
                elif "-bold" in lower_file:
                    font_files["fn_bold"] = file_path
                elif "-italic" in lower_file:
                    font_files["fn_italic"] = file_path
    
            # Only register if at least one font file is found
            if any(font_files.values()):
                LabelBase.register(
                    name=folder,  # folder name as font name
                    **{k: v for k, v in font_files.items() if v is not None}
                )
    
    
    # Save current settings to user file.
    def _save_user_settings(self) -> None:
        os.makedirs(os.path.dirname(self.user_path), exist_ok=True)
        with open(self.user_path, "w") as file:
            json.dump(self.settings, file, indent=2)
