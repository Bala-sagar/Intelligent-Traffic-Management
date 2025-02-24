import cv2
from ultralytics import YOLO
import os
import utils

def detect_mobile_phone(video_path, data):

    save_dir = './images/'
    model = YOLO('yolov8m.pt')
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' for .mp4
    out = cv2.VideoWriter('./static/assets/result.mp4', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    frame_counter = 0

    while True:
        success, frame = cap.read()
        frame_counter += 1

        if not success:
            break

        if success:
            results = model(frame, conf=0.5, classes=[67])
            annotated_frame = results[0].plot()
            cv2.imshow("YOLOv8 Inference", annotated_frame)
            out.write(annotated_frame)

            # Check if there are any detections
            if len(results) > 0:
                cv2.imwrite(save_dir+'violation.jpg', frame)  # Save the frame as an image

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    # img_list = os.listdir(save_dir)
    # if img_list is not None:
    #     utils.send_email(data["contact"], "Usage of cell phone while driving")

    return True

# detect_mobile_phone("./test/mobile_test.mp4")
