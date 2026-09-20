from ultralytics import YOLO

# Load pretrained YOLOv8 Nano
model = YOLO("yolov8n.pt")

# Train the model
model.train(
    data="moduls/dataset/data.yaml",
    epochs=30,
    imgsz=640,
    batch=8,
    workers=2,
    cache=True,
    device="cpu",
    name="FaceMaskDetection"
)