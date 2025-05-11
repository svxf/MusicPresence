import threading
import os
from pystray import Icon, Menu, MenuItem
from PIL import Image

class TrayIcon:
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.icon = Icon("musice presence")
        self.playing = True
        self.current_song = "Not Playing"

        self.icon.menu = Menu(
            MenuItem(lambda item: self.current_song, lambda: None, enabled=False),
            MenuItem(lambda item: "Pause" if self.playing else "Unpause", self.toggle_playing),
            MenuItem("Exit", self.stop_app)
        )
        self.icon.icon = self.create_image()

    def create_image(self):
        path = os.path.join(os.path.dirname(__file__), 'icon.png')
        return Image.open(path)

    def toggle_playing(self, icon, item):
        self.playing = not self.playing
        self.app_manager.running = self.playing

    def stop_app(self, icon, item):
        self.app_manager.stop()
        self.icon.stop()

    def update_song(self, text):
        self.current_song = text
        self.icon.update_menu()

    def run(self):
        threading.Thread(target=self.icon.run, daemon=True).start()
