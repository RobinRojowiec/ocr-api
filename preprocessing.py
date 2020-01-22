"""

IDE: PyCharm
Project: ocr-api
Author: Robin
Filename: preprocessing.py
Date: 21.01.2020

"""
import cv2


def preprocess_image(image_path):
    # load the example image and convert it to grayscale
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    cv2.imwrite(image_path, gray)
