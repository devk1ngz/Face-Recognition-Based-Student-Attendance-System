import cv2
import time
import unicodedata
import re
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from app.core.face_engine import FaceEngine

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    attendance_signal = pyqtSignal(str, str) 

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.face_engine = None

    def remove_accents(self, input_str):
        if not input_str:
            return ""
        s = unicodedata.normalize('NFD', input_str)
        s = s.encode('ascii', 'ignore').decode('utf-8')
        return str(s)

    def run(self):
        if not self.face_engine:
            self.face_engine = FaceEngine()

        cap = cv2.VideoCapture(0)
        last_attendance_time = {} 

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                results = self.face_engine.recognize_face(frame)
                
                for (bbox, identity, score) in results:
                    x1, y1, x2, y2 = bbox
                    
                    top_text = "Unknown"
                    bottom_text = f"{score:.2f}"
                    color = (0, 0, 255) 
                    
                    if identity != "Unknown":
                        color = (0, 255, 0)
                        mssv = identity 
                        
                        top_text = mssv  
                        bottom_text = f"MSSV: {mssv} ({score:.2f})"

                        current_time = time.time()
                        if mssv not in last_attendance_time or (current_time - last_attendance_time[mssv] > 5):
                            self.attendance_signal.emit(mssv, f"{mssv}")
                            last_attendance_time[mssv] = current_time
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, top_text, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                    if identity != "Unknown":
                        cv2.putText(frame, bottom_text, (x1, y2 + 25), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(800, 600, 1) 
                self.change_pixmap_signal.emit(p)
            
            time.sleep(0.01) 

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()