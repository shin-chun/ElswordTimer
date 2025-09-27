import tkinter as tk
import os
import threading
import time
import keyboard
import json
import platform
import winsound
from hotkey_listener import HotkeyListener
from collections import deque
from tkinter import messagebox, filedialog



### 主視窗架構 ###
class TimerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ElswordTimer")
        self.root.geometry("600x500")
        self.timers = []
        self.master_switch = tk.BooleanVar(value=True)
        # 啟用監聽快捷
        self.listener = HotkeyListener(self.reset_all_timers)
        self.listener.start()

        # 控制區按鈕
        button = tk.Button(self.root, text="新增計時器",font=("Microsoft JhengHei", 13), command=self.open_add_window)
        button.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        button1 = tk.Button(self.root, text="時間重置",font=("Microsoft JhengHei", 13), command=self.reset_all_timers)
        button1.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        button2 = tk.Button(self.root, text="編輯選取計時器",font=("Microsoft JhengHei", 13), command=self.edit_timer)
        button2.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        button3 = tk.Button(self.root, text="刪除選取計時器",font=("Microsoft JhengHei", 13), command=self.delete_timer)
        button3.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        button4 = tk.Button(self.root, text="儲存設定",font=("Microsoft JhengHei", 13), command=self.save_config)
        button4.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        button5 = tk.Button(self.root, text="匯入設定",font=("Microsoft JhengHei", 13), command=self.load_config)
        button5.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        # 總開關狀態與切換
        self.status_label = tk.Label(self.root, text="計時器已啟用", fg="green", font=("Microsoft JhengHei", 13))
        self.status_label.grid(row=4, column=1, sticky="nsew", padx=5, pady=5)

        self.toggle_button = tk.Button(self.root, text="停用所有計時器",font=("Microsoft JhengHei", 13), command=self.toggle_master_switch)
        self.toggle_button.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

        self.timer_listbox = tk.Listbox(self.root, font=("Microsoft JhengHei", 13))
        self.timer_listbox.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        threading.Thread(target=self.listen_keys, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<F8>", self.handle_reset_shortcut)
        self.root.mainloop()

    def handle_reset_shortcut(self, event=None):
        self.reset_all_timers()

    def toggle_master_switch(self):
        current = self.master_switch.get()
        self.master_switch.set(not current)

        if self.master_switch.get():
            self.status_label.config(text="計時器已啟用", fg="green")
            self.toggle_button.config(text="停用所有計時器")

            # ✅ 啟用時：重新啟動所有計時器視窗
            for timer in self.timers:
                timer.active = True
                timer.trigger()

        else:
            self.status_label.config(text="計時器已停用", fg="red")
            self.toggle_button.config(text="啟用所有計時器")
            # ✅ 停用時：關閉所有倒數視窗
            for timer in self.timers:
                timer.reset()  # reset() 內部會呼叫 close_window()

    def open_add_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("新增計時器")
        add_win.geometry("300x400")

        tk.Label(add_win, text="計時器名稱").pack()
        name_entry = tk.Entry(add_win)
        name_entry.pack()

        tk.Label(add_win, text="多組按鍵序列（每組用逗號，組與組用分號）").pack()
        seq_entry = tk.Entry(add_win)
        seq_entry.insert(0, "a,b,c;x,y,z")
        seq_entry.pack()

        tk.Label(add_win, text="秒數內完成每組").pack()
        window_entry = tk.Entry(add_win)
        window_entry.insert(0, "3")
        window_entry.pack()

        tk.Label(add_win, text="倒數秒數").pack()
        duration_entry = tk.Entry(add_win)
        duration_entry.insert(0, "7")
        duration_entry.pack()

        def confirm_add():
            try:
                name = name_entry.get().strip()
                sequences = [[k.strip() for k in group.split(",")] for group in seq_entry.get().split(";")]
                window = float(window_entry.get())
                duration = int(duration_entry.get())

                timer = AdvancedTimer(name, sequences, window, duration)
                self.timers.append(timer)
                self.timer_listbox.insert(tk.END, f"{name}：{sequences}（{window}s）→ 倒數 {duration}s")
                add_win.destroy()
            except Exception as e:
                messagebox.showerror("錯誤", f"新增失敗：{e}")

        tk.Button(add_win, text="確認新增", command=confirm_add).pack(pady=10)

    def edit_timer(self):
        selected = self.timer_listbox.curselection()
        if not selected:
            messagebox.showwarning("未選取", "請先選取要編輯的計時器")
            return
        index = selected[0]
        timer = self.timers[index]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("編輯計時器")
        edit_win.geometry("300x400")

        tk.Label(edit_win, text="計時器名稱").pack()
        name_entry = tk.Entry(edit_win)
        name_entry.insert(0, timer.name)
        name_entry.pack()

        tk.Label(edit_win, text="多組按鍵序列（每組用逗號，組與組用分號）").pack()
        seq_entry = tk.Entry(edit_win)
        seq_entry.insert(0, ";".join([",".join(seq) for seq in timer.sequences]))
        seq_entry.pack()

        tk.Label(edit_win, text="秒數內完成每組").pack()
        window_entry = tk.Entry(edit_win)
        window_entry.insert(0, str(timer.window))
        window_entry.pack()

        tk.Label(edit_win, text="倒數秒數").pack()
        duration_entry = tk.Entry(edit_win)
        duration_entry.insert(0, str(timer.duration))
        duration_entry.pack()

        def confirm_edit():
            try:
                timer.name = name_entry.get().strip()
                timer.sequences = [[k.strip() for k in group.split(",")] for group in seq_entry.get().split(";")]
                timer.window = float(window_entry.get())
                timer.duration = int(duration_entry.get())

                self.timer_listbox.delete(index)
                self.timer_listbox.insert(index,
                                          f"{timer.name}：{timer.sequences}（{timer.window}s）→ 倒數 {timer.duration}s")
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("錯誤", f"編輯失敗：{e}")

        tk.Button(edit_win, text="確認修改", command=confirm_edit).pack(pady=10)
    def delete_timer(self):
        selected = self.timer_listbox.curselection()
        if not selected:
            messagebox.showwarning("未選取", "請先選取要刪除的計時器")
            return
        index = selected[0]
        self.timers[index].active = False

        del self.timers[index]
        self.timer_listbox.delete(index)

    def reset_all_timers(self):
        for timer in self.timers:
            timer.active = True
            timer.reset_sequence()  # ✅ 只重置階段，不觸發倒數
            timer.last_trigger_time = None  # ✅ 清除冷卻時間

    def save_config(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON 檔案", "*.json")])
        if not path:
            return
        try:
            data = [t.to_dict() for t in self.timers]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "設定已儲存")
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存失敗：{e}")

    def load_config(self):
        for timer in self.timers:
            timer.reset()
        path = filedialog.askopenfilename(filetypes=[("JSON 檔案", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.timers.clear()
            self.timer_listbox.delete(0, tk.END)
            for item in data:
                timer = AdvancedTimer(
                    item["name"],
                    item["sequences"],
                    item["window"],
                    item["duration"]
                )
                self.timers.append(timer)
                self.timer_listbox.insert(
                    tk.END,
                    f"{timer.name}：{timer.sequences}（{timer.window}s）→ 倒數 {timer.duration}s"
                )
            messagebox.showinfo("成功", "設定已匯入")
        except Exception as e:
            messagebox.showerror("錯誤", f"匯入失敗：{e}")
    def listen_keys(self):
        while True:
            if not self.master_switch.get():
                time.sleep(0.1)
                continue

            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                key = event.name
                # print(f"按下鍵：{key}")
                for timer in self.timers:
                    timer.check_key(key)
            time.sleep(0.01)

    def on_close(self):
        for timer in self.timers:
            timer.active = False
        self.master_switch.set(False)
        self.root.destroy()

## 倒數窗設置 ##
class CountdownWindow:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.remaining = duration
        self.running = False

        self.win = tk.Toplevel()
        self.win.overrideredirect(True)  # 無邊框
        self.win.geometry("300x50")
        self.load_position()
        self.win.attributes("-topmost", True)

        self.win.config(bg="yellow")
        self.win.wm_attributes("-transparentcolor", "yellow")

        self.label = tk.Label(
            self.win,
            text=f"{name}:{duration}秒",
            font=("Segoe UI", 16, "bold"),
            fg="black",
            bg="white"
        )
        self.label.pack(expand=True, padx=10, pady=10)

        # 拖曳移動
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)
        # 右鍵選單
        self.menu = tk.Menu(self.win, tearoff=0)
        self.menu.add_command(label="關閉視窗", command=self.stop)
        self.win.bind("<Button-3>", self.show_context_menu)

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

    def restart(self, force=False):
        if self.running and not force:
            return
        self.remaining = self.duration
        self.running = True
        self.win.config(bg="yellow")
        self.label.config(bg="#123456")
        self.update_countdown()

    def update_countdown(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self.label.config(text=f"{self.name} ✅ 完成")
            self.play_sound()
            self.win.config(bg="yellow")
            self.label.config(bg="lightgreen")
            self.running = False
            return

        self.label.config(text=f"{self.name} 倒數中... {self.remaining} 秒")
        self.remaining -= 1
        self.win.after(1000, self.update_countdown)

    # 只顯示視窗不倒數
    def show_only(self):
        self.running = False
        self.remaining = self.duration
        self.win.config(bg="yellow")
        self.label.config(bg="white")
        self.label.config(text=f"{self.name} 等待觸發")

    def play_sound(self):
        try:
            if platform.system() == "Windows":
                winsound.Beep(1000, 500)
            else:
                print("\a")
        except Exception as e:
            print(f"提示音錯誤：{e}")

    def stop(self):
        self.save_position()
        self.win.destroy()
        self.running = False
        if self.win.winfo_exists():
            self.win.destroy()

    def start_move(self, event):
        self._x = event.x_root
        self._y = event.y_root

    def do_move(self, event):
        dx = event.x_root - self._x
        dy = event.y_root - self._y

        geom = self.win.geometry()
        geom_parts = geom.split('+')
        x = int(geom_parts[1]) + dx
        y = int(geom_parts[2]) + dy

        self.win.geometry(f"+{x}+{y}")
        self._x = event.x_root
        self._y = event.y_root


    def show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def save_position(self):
        try:
            if os.path.exists("window_positions.json"):
                with open("window_positions.json", "r") as f:
                    all_positions = json.load(f)
            else:
                all_positions = {}

            geom = self.win.geometry().split('+')
            x = int(geom[1])
            y = int(geom[2])
            all_positions[self.name] = {'x': x, 'y': y}

            with open("window_positions.json", "w") as f:
                json.dump(all_positions, f)
        except Exception as e:
            print(f"儲存位置失敗：{e}")

    def load_position(self):
        try:
            if os.path.exists("window_positions.json"):
                with open("window_positions.json", "r") as f:
                    all_positions = json.load(f)

                if self.name in all_positions:
                    pos = all_positions[self.name]
                    self.win.geometry(f"300x50+{pos['x']}+{pos['y']}")
        except Exception as e:
            print(f"載入位置失敗：{e}")

## 程式運行邏輯 ##
class AdvancedTimer:
    def __init__(self, name, sequences, window, duration):
        self.name = name
        self.sequences = sequences  # 多組鍵序列，例如 [['a','b','c'], ['x','y','z']]
        self.window = window        # 每階段最大容忍時間（秒）
        self.duration = duration    # 倒數視窗時間
        self.active = True
        self.stage = 0
        self.last_time = None
        self.last_trigger_time = None
        self.current_sequence = None
        self.countdown_window = CountdownWindow(name, duration)

    def check_key(self, key):
        if not self.active:
            return
        now = time.time()

        # 冷卻中 → 不觸發
        if self.last_trigger_time and now - self.last_trigger_time < self.duration:
            return

        # 尚未啟動任何序列 → 嘗試啟動
        if self.current_sequence is None:
            for seq in self.sequences:
                if key == seq[0]:
                    self.current_sequence = seq
                    self.stage = 1
                    self.last_time = now
                    return
            return

        # 超時 → 重置
        if now - self.last_time > self.window:
            self.reset_sequence()
            return

        expected_key = self.current_sequence[self.stage]
        if key == expected_key:
            self.stage += 1
            self.last_time = now
            if self.stage == len(self.current_sequence):
                self.trigger()
                # self.reset_sequence()
        else:
            # 容錯：錯誤鍵不重置，只要時間內補正即可
            pass

    def trigger(self):
        self.last_trigger_time = time.time()
        if not self.countdown_window or not self.countdown_window.win.winfo_exists():
            self.countdown_window = CountdownWindow(self.name, self.duration)
        self.countdown_window.restart(force=True)

    def reset_sequence(self):
        self.stage = 0
        self.last_time = None
        self.current_sequence = None

        if self.countdown_window:
            self.countdown_window.show_only()  # ✅ 顯示視窗但不倒數

    def reset(self):
        self.active = False
        self.reset_sequence()
        self.close_window()

    def close_window(self):
        if self.countdown_window:
            self.countdown_window.stop()
            self.countdown_window = None

    def to_dict(self):
        return {
            "name": self.name,
            "sequences": self.sequences,
            "window": self.window,
            "duration": self.duration,
        }
if __name__ == "__main__":
    TimerApp()
