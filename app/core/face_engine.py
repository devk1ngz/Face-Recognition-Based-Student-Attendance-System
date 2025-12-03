import os
import cv2
import numpy as np
import insightface
import pickle 
from insightface.app import FaceAnalysis


DATA_PATH = "data/raw_faces"        
CACHE_FILE = "data/face_cache.pkl" 
SIMILARITY_THRESHOLD = 0.5


class FaceEngine:
    def __init__(self):
        self.known_embeddings = []
        self.known_names = [] 

        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        self.load_data()

    def load_data(self):

        if os.path.exists(CACHE_FILE):
            try:
                print(f"Đang tải dữ liệu từ cache: {CACHE_FILE}...")
                with open(CACHE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.known_embeddings = data['embeddings']
                    self.known_names = data['names']
                print(f"Đã tải xong! ({len(self.known_names)} khuôn mặt)")
                return
            except Exception as e:
                print(f"File cache lỗi, sẽ quét lại ảnh: {e}")

        self.scan_images_and_train()

    def scan_images_and_train(self):
        print("Đang quét thư mục ảnh để học khuôn mặt mới...")
        
        temp_embeddings = []
        temp_names = []

        if not os.path.exists(DATA_PATH):
            print(f"Thư mục {DATA_PATH} không tồn tại!")
            return

        
        for mssv_folder in os.listdir(DATA_PATH):
            folder_path = os.path.join(DATA_PATH, mssv_folder)
            
            if os.path.isdir(folder_path):
                mssv = mssv_folder
                
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                        img_path = os.path.join(folder_path, filename)
                        img = cv2.imread(img_path)
                        if img is None: continue
                        
                        faces = self.app.get(img)
                        if len(faces) > 0:
                            temp_embeddings.append(faces[0].normed_embedding)
                            temp_names.append(mssv)
                            print(f"  + Đã học: {mssv} ({filename})")
        

        self.known_embeddings = temp_embeddings
        self.known_names = temp_names

 
        self.save_cache()

    def save_cache(self):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump({
                'embeddings': self.known_embeddings,
                'names': self.known_names
            }, f)
        print(f"Đã lưu dữ liệu vào {CACHE_FILE}")

    def refresh_data(self):
        self.scan_images_and_train()

    def recognize_face(self, frame):
        results = []
        faces = self.app.get(frame)
        
        for face in faces:
            bbox = face.bbox.astype(int)
            embedding = face.normed_embedding
            
            max_score = 0
            identity = "Unknown"
            
            if len(self.known_embeddings) > 0:
                sims = np.dot(self.known_embeddings, embedding)
                max_idx = np.argmax(sims)
                max_score = sims[max_idx]
                
                if max_score >= SIMILARITY_THRESHOLD:
                    identity = self.known_names[max_idx]
            
            results.append((bbox, identity, max_score))
            
        return results