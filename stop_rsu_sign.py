import threading
import time

class StopRsuSign:
    def __init__(self, stop_callback = None, resume_callback = None):
        self.stop_callback = stop_callback
        self.resume_callback = resume_callback
        self.rsu_value = 'G'  # 初始化為綠燈
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._read_rsu_file_periodically)
        self._thread.daemon = True
        self._thread.start()

    def _read_rsu_file_periodically(self):
        while not self._stop_event.is_set():
            try:
                with open('/tmp/rsu.txt', 'r') as file:
                    content = file.read().strip()
                self.rsu_value = content
            except FileNotFoundError:
                # 處理檔案不存在的情況
                self.rsu_value = 'G'  # 預設為綠燈
            time.sleep(1)

    def run(self):
        # 獲取目前的 RSU 內容
        if self.rsu_value == "R":
            self.stop_callback()
        else:
            self.resume_callback()
        # print(f"rsu_value:{self.rsu_value}")
        # time.sleep(1)
        return self.rsu_value

    def stop(self):
        self._stop_event.set()
        self._thread.join()


# import time

# class StopRsuSign:
#     def __init__(self, stop_callback = None):
#         self.stop_callback = stop_callback
#         # pass

#     def read_file(self, file_path):
#         try:
#             with open(file_path, 'r') as file:
#                 content = file.read()
#                 return content
#         except FileNotFoundError:
#             return None
#         except IOError:
#             return None
    
#     def run(self):
#         file_path = '/tmp/rsu.txt'
#         while True:
#             time.sleep(1)
#             file_content = self.read_file(file_path)
#             print(f"現在號誌:{file_content}")
#             if file_content == "R":
#                 self.stop_callback()
#                 return True
#             else:
#                 return False
#         return False