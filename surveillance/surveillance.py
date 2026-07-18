from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
#from tqdm import tqdm
#import psutil

fac = 1 ## resolution factor

# Load model
model = YOLO("yolo26n.pt")

target_imgs = []

targets = ["cat", "dog", "person" , "bear"]
targets = [t.lower() for t in targets]
target_classes = [k for k,v in model.names.items() if v.lower() in targets]

# Camera setup
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (640*fac, 480*fac), "format": "RGB888"}
    )
)
picam2.start()

while True:
    # Grab a frame
    frame = picam2.capture_array()

    # Run YOLO
    result = model(
        frame,
        imgsz=640*fac,
        classes = target_classes,
        verbose=False,
        conf=0.4, 
        #stream = True
    )[0]

    # Draw detections
    annotated = result.plot()

    # Display
    cv2.imshow("YOLO", annotated)

    if any([(result.boxes.cls == c).any() for c in target_classes]):
        print("target class detected")
        target_imgs.append(annotated.copy())
    
    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


picam2.stop()
cv2.destroyAllWindows()