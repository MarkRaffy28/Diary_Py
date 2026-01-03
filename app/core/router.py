from kivy.clock import Clock

from app.ui.screens.main_screen import MainScreen

#Settings
from app.ui.screens.theme_and_style import ThemeAndStyleScreen

class AppRouter:
    def __init__(self, screen_manager):
        self.sm = screen_manager
        self.backstack = []
        self.ui_state = {}


    def register_screens(self):
        # Delay adding screens by 1 second to avoid FBO issues
        Clock.schedule_once(self._add_screens, 1)


    # Navigate to another screen.
    # :param replace: if True, does not push current screen to back stack
    def go_to(self, screen_name, *, replace=False):
        current = self.sm.current

        if not replace and current != screen_name:
            self.backstack.append({
                "screen": current,
                "state": self._capture_screen_state(current)
            })

        self.sm.transition.direction = "left"
        self.sm.current = screen_name


    # Handles back navigation.
    # :param reload_all: If True, reload all screens before restoring previous
    def on_back(self, reload_all=False):
        # If drawer / modal is open → close first
        if self._close_overlays():
            return True

        if self.backstack:
            previous_state = self.backstack.pop()
            previous_screen = previous_state["screen"]
            state = previous_state.get("state", {})

            # Restore UI state before transition
            self._restore_screen_state(previous_screen, state)
            self.sm.transition.direction = "right"
            
            # Navigate to previous screen   
           # self.sm.current = previous_screen
            Clock.schedule_once(lambda dt: setattr(self.sm, "current", previous_screen), 0.26)
            
              # Save the currently active tab name into ui_state
            if self.sm.has_screen("main_screen"):
                main_screen = self.sm.get_screen("main_screen")
                self.ui_state["main_screen_tab"] = main_screen.get_active_tab()
            
            # Reload all screens if flag is set
            if reload_all:
                Clock.schedule_once(self._add_screens, 0.3)
            return True

        # Nothing to go back to → allow app exit
        return False


    # Returns a dictionary with current UI state for the screen
    def _capture_screen_state(self, screen_name):
        screen = self.sm.get_screen(screen_name)
        if screen_name == "main_screen":
            return {"tab_name": screen.get_active_tab()}

        return {}


    # Restores previously captured UI state.
    def _restore_screen_state(self, screen_name, state):
        screen = self.sm.get_screen(screen_name)
        if screen_name == "main_screen" and state:
            tab_name = state.get("tab_name")
            if tab_name:
                screen.set_active_tab(tab_name)


    # Adds all screens to screen manager
    def _add_screens(self, dt=0):
        screens = {
            "main_screen": MainScreen,
            "theme_and_style_screen": ThemeAndStyleScreen,
        }
    
        # Remove old screens
        for name in screens:
            if self.sm.has_screen(name):
                self.sm.remove_widget(self.sm.get_screen(name))
    
        # Add new instances dynamically
        for name, cls in screens.items():
            self.sm.add_widget(cls(name=name))
            
        # Restore main screen tab if available
        tab_name = self.ui_state.get("main_screen_tab")
        if tab_name and self.sm.has_screen("main_screen"):
            main = self.sm.get_screen("main_screen")
            Clock.schedule_once(lambda dt: main.set_active_tab(tab_name), 0)            
                         
        # initial screen
        self.sm.current = "main_screen"            
            
        
    def _close_overlays(self):
        # hook for dialogs, bottom sheets, drawers
        return False        
        
        