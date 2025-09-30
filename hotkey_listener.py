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



class HotkeyController:
    def __init__(self, manager):
        self.manager = manager
        self.stage = 0
        self.selected = None

    def on_press(self, key):
        try:
            k = key.char.lower()
        except AttributeError:
            k = str(key).lower()

        if self.stage == 0:
            if k in self.manager.timers:
                self.selected = k
                self.stage = 1
                print(f"選擇：{k}")
        elif self.stage == 1:
            if k == 'shift':  # 第二鍵：鎖定
                self.stage = 2
                print(f"鎖定：{self.selected}")
        elif self.stage == 2:
            if k == 'enter':  # 第三鍵：觸發
                print(f"觸發：{self.selected}")
                self.manager.timers[self.selected].start()
                self.stage = 0  # 重置流程

    def start(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
