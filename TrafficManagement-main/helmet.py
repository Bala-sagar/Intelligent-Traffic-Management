import cv2
import numpy as np
import os
import imutils
from tensorflow.keras.models import load_model
import easyocr
import os 

ROOT_DIR = "./"

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

net = cv2.dnn.readNet("./models/yolov5-tiny.weights", "./models/yolov5-cfg.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

img_dir = './images'
model = load_model('./models/model_v2.h5')
print('model loaded!!!')
COLORS = [(0,255,0),(0,0,255)]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
 

fourcc = cv2.VideoWriter_fourcc(*"XVID")
writer = cv2.VideoWriter('./videos/output.avi', fourcc, 5,(888,500))


def helmet_or_nohelmet(helmet_roi):
	try:
		helmet_roi = cv2.resize(helmet_roi, (224, 224))
		helmet_roi = np.array(helmet_roi,dtype='float32')
		helmet_roi = helmet_roi.reshape(1, 224, 224, 3)
		helmet_roi = helmet_roi/255.0
		return int(model.predict(helmet_roi)[0][0])
	except:
			pass


def detect_plates(mode):
    cap = cv2.VideoCapture(mode)
    # ret = True
    g = 0
    while cap.isOpened():
        g += 1
        ret, img = cap.read()
        if not ret:
            break
        img = imutils.resize(img,height=500)
        
        height, width = img.shape[:2]

        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        confidences = []
        boxes = []
        classIds = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)

                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    classIds.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        for i in range(len(boxes)):
            if i in indexes:
                x,y,w,h = boxes[i]
                color = [int(c) for c in COLORS[classIds[i]]]
                # green --> bike
                # red --> number plate
                if classIds[i]==0: #bike
                    helmet_roi = img[max(0,y):max(0,y)+max(0,h)//4,max(0,x):max(0,x)+max(0,w)]
                else: #number plate
                    x_h = x-60
                    y_h = y-350
                    w_h = w+100
                    h_h = h+100
                    crop_img = img[y:y+h, x:x+w]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 7)
                    # h_r = img[max(0,(y-330)):max(0,(y-330 + h+100)) , max(0,(x-80)):max(0,(x-80 + w+130))]
                    if y_h>0 and x_h>0:
                        h_r = img[y_h:y_h+h_h , x_h:x_h +w_h]
                        c = helmet_or_nohelmet(h_r)
                        cat = ['helmet','no-helmet'][c]
                        cv2.putText(img, cat,(x,y-100),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),2)
                        person_crop = img[y_h: y_h+h_h, x_h:x_h+w_h]                
                        cv2.rectangle(img, (x_h, y_h), (x_h + w_h, y_h + h_h),(255,0,0), 10)
                        if cat=='no-helmet': print('yes')
                            
                            
                        if c!=0:
                            cv2.imwrite(os.path.join('./person', 'crop_{}.png'.format(g)), person_crop)
                            cv2.imwrite(os.path.join(img_dir, 'crop_{}.png'.format(g)), crop_img)
                            


        writer.write(img)
        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    writer.release()
    cap.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return True


# detect_plates('test_helmet_red.mp4')
