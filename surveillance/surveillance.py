from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
from time import time, sleep

from comms.ctc_client import ClientInterface

cooldown_time = 1.5 # seconds

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

ble_interface = ClientInterface()
ble_interface.start()
time_last = 0

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
        time_this = time()
        if time_this > (time_last + cooldown_time):
            ble_interface.write_ble(True)
            time_last = time_this
        
    
    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
        
    sleep(0.1)

ble_interface.stop()
picam2.stop()
cv2.destroyAllWindows()