class Timer:
    def __init__(self, name, keys, window, duration):
        self.name = name
        self.keys = keys  # 例如 ['a', 'b', 'c']
        self.window = window
        self.duration = duration
        self.index = 0
        self.last_time = None
        self.active = True

    def check_key(self, key):
        if not self.active or self.index >= len(self.keys):
            return False

        expected = self.keys[self.index]
        if key == expected:
            self.index += 1
            self.last_time = time.time()

            if self.index == len(self.keys):
                self.trigger_countdown()
            return True
        else:
            # 若不符合，是否要重置 index？視需求而定
            self.index = 0
            return False

    def trigger_countdown(self):
        print(f"✅ {self.name} 成功觸發倒數 {self.duration} 秒")
        # 這裡可以啟動 CountdownWindow 或其他視覺效果