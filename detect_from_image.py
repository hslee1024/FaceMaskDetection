# Face Mask Detection - detect_from_image.py
# 2020. 09. 01. by Hyunseo Lee

# Usage
# python detect_from_image.py --image <Image Path>

# Import necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os

# Argument Parser
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Image Path")
ap.add_argument("-f", "--face", type=str, default="CAFFE_DNN", help="Face Detector Model Path")
ap.add_argument("-m", "--model", type=str, default="face_mask_detection.model", help="Face Mask Detector Model Path")
ap.add_argument("-c", "--confidence", type=float, default=0.5, help="Minimum probability to filter weak detections")
args = vars(ap.parse_args())

# FMD info
print("\n==========================================")
print("\nFace Mask Detection - detect_from_image.py")
print("\n2020. 09. 01. by Hyunseo Lee")
print("\n==========================================\n")

# Load face detection model
print("[FMD] [INFO] Loading face detector model...")
prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
weightsPath = os.path.sep.join([args["face"], "face_detection.caffemodel"])
net = cv2.dnn.readNet(prototxtPath, weightsPath)

# Load face mask detection model
print("[FMD] [INFO] Loading face mask detector model...")
model = load_model(args["model"])

# Load the input image from disk, clone it, and grab the image spatial dimensions
image = cv2.imread(args["image"])
orig = image.copy()
(h, w) = image.shape[:2]

# Construct a blob from the image
blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))

# Pass the blob through the network and obtain the face detections
print("[FMD] [INFO] Computing face detections...")
net.setInput(blob)
detections = net.forward()

# Loop over the detections
for i in range(0, detections.shape[2]):
	confidence = detections[0, 0, i, 2]
	if confidence > args["confidence"]:
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")
		(startX, startY) = (max(0, startX), max(0, startY))
		(endX, endY) = (min(w - 1, endX), min(h - 1, endY))
		face = image[startY:endY, startX:endX]
		face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
		face = cv2.resize(face, (224, 224))
		face = img_to_array(face)
		face = preprocess_input(face)
		face = np.expand_dims(face, axis=0)
		(mask, withoutMask) = model.predict(face)[0]
		label = "Mask" if mask > withoutMask else "No Mask"
		color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
		label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
		cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

# Help info to quit cv2 image window
print("\n=======================================")
print("\nTo quit cv2 image window, Press key [0]")
print("\n=======================================")

cv2.imshow("Output", image)
cv2.waitKey(0)

# Detection done
print("\n==========================================")
print("\nFace Mask Detection - detect_from_image.py")
print("\nDetection complete.")
print("\n==========================================")