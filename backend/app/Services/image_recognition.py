
import tensorflow as tf
from ultralytics import YOLO
from pathlib import Path
from PIL import Image
import io

MODEL_PATH = Path(__file__).parent / "yolov8n.pt"
try:
    MODEL = YOLO(str(MODEL_PATH))
except FileNotFoundError:
    print(f"Aviso: O arquivo do modelo não foi encontrado em {MODEL_PATH}.")
    MODEL = None

CLASS_TRANSLATIONS = {
    "laptop": "notebook",
    "keyboard": "teclado",
    "mouse": "mouse",
    "monitor": "monitor",
    "tv": "Monitor",
    "remote": "controle remoto",
    "cell phone": "celular",
    "camera": "câmera",
}


def get_model():
    return MODEL

def predict_image(image_data: bytes):
    if not MODEL:
        return {"error": "O modelo de IA não está disponível."}
    image = Image.open(io.BytesIO(image_data))
    results = MODEL(image)
    processed_results = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            #x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
            cls = int(box.cls[0].tolist())
            conf = round(box.conf[0].tolist(), 2)
            class_name = MODEL.names[cls]
            if class_name in CLASS_TRANSLATIONS:
                translated_class = CLASS_TRANSLATIONS.get(class_name, class_name)
                processed_results.append({
                    "class": translated_class,
                    "confidence": conf,
                })

    return processed_results

