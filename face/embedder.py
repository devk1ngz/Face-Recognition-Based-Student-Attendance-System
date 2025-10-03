import torch
import numpy as np
from torchvision import transforms
from PIL import Image

# giả sử bạn đã load model ArcFace
# model_arcface = load_arcface_model()

def get_embedding(face_img, model_arcface):
    transform = transforms.Compose([
        transforms.Resize((112, 112)),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5])
    ])
    img = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
    tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        emb = model_arcface(tensor).cpu().numpy()
    return emb[0]
