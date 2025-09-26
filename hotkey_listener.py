# hotkey_listener.py
from pynput import keyboard

class HotkeyListener:
    def __init__(self, on_key_callback):
        self.on_key_callback = on_key_callback

    def start(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f8:
                    self.on_key_callback()
            except Exception:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()