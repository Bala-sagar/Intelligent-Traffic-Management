from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import*
import utils

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"]

def coordinate_checker(limits, cx, cy):
    x1 = limits[0]
    x2 = limits[2]
    y1 = limits[1]
    y2 = limits[3]

    slope = (y2 - y1)/ (x2 - x1)
    if(cy - y1 == (cx- x1)*slope):
        return True
    else:
        return False

def detect_signal_violation(video_path, data):

    save_dir = './images/'
    cap = cv2.VideoCapture(video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' for .mp4
    out = cv2.VideoWriter('./static/assets/result.mp4', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))


    cap.set(3,1280)
    cap.set(4,720)
    tracker = Sort(max_age= 20, min_hits=3, iou_threshold=0.3)
    limits = [300, 275-40, 850, 277-40]
    totalCount = []
    model = YOLO('./models/yolov8n.pt')
    while True:
        success, img = cap.read()
        if not success:
            break
        
        results = model(img,stream = True)

        detections = np.empty((0,5))
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1,y1,x2,y2 = box.xyxy[0]
                x1,y1,x2,y2 = int(x1) , int(y1) , int(x2), int(y2)

                w,h = x2-x1, y2-y1
                

                conf = math.ceil((box.conf[0]*100))/100
                cls = int(box.cls[0])
                currentclass = classNames[cls]
                if currentclass == "car" or currentclass == "truck" or currentclass == "bus" or currentclass == "motorbike" and conf > 0.4:
                    currentarray = np.array([x1,y1,x2,y2,conf])
                    detections = np.vstack((detections, currentarray))


        resultstracker = tracker.update(detections)
        
        cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), 5)
        for result in resultstracker:
            x1, y1, x2, y2, id = result
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255), colorC=(0,0,255))
            cx, cy = x1 + w // 2, y1 + h // 2
            cv2.circle(img, (cx, cy), 1, (255, 0, 255), cv2.FILLED)

            if limits[0] < cx < limits[2] and limits[1] - 10 < cy < limits[1] + 15:
                if totalCount.count(id) == 0:
                    totalCount.append(id)
                    cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)
                    cv2.imwrite(save_dir+'violation.jpg', img)
                    # file_path = "traffic_jam.txt"  # Replace with the actual file path
                    # with open(file_path, "a") as file:
                    #     file.write(f"{id}\n")

        cv2.putText(img,str(len(totalCount)),(50,50),cv2.FONT_HERSHEY_COMPLEX_SMALL,5,(50,50,255),8)

        
        cv2.imshow("Image",img)
        out.write(img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        

    img_list = os.listdir(save_dir)
    #if img_list is not None:
        #utils.send_email(data["contact"], "Violated the Red Signal")


# detect_signal_violation("./test/signal-test1.mp4")