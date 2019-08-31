# coding: utf-8

# imports
import os
import shutil
import subprocess
import tempfile


import cv2 
import numpy as np


class TesseractWrapper():
    def __init__(self, tesseract_path="tesseract", lang="rus"):

        self._directory = tempfile.mkdtemp(prefix="tesseract_")
        self._tesseract_result = self._directory + os.sep + "tesseract_result.txt"
        self._tesseract_image = self._directory + os.sep + "tesseract_image.jpg"

        self._args=[
            tesseract_path,
            self._tesseract_image,
            self._tesseract_result[0:-4],
            '-l',
            lang
        ]
    
    def to_string(self, image: np.ndarray):
        cv2.imwrite(self._tesseract_image, image)

        process = subprocess.Popen(self._args, stderr=subprocess.PIPE, env=os.environ)
        process.wait()

        with open(self._tesseract_result, "r", encoding="utf-8") as file:
            return file.read()
    
    def __del__(self):
        shutil.rmtree(self._directory)
