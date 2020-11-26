# Import Everything
import os
import zipfile
import time
from tensorflow import keras
from tensorflow.keras import optimizers
from tensorflow.keras.optimizers import schedules
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras import layers
from tensorflow.keras import Model
import numpy as np
import random
import io
import time
import picamera
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True



# Initalize Variables

# Camera
numCycles = 0
imageRatio = 480 / 640
imageWidth = 640
imageHeight = int(imageWidth * imageRatio)
capturesPerCycle = 40
cameraFramerate = 80

# Motor & Servo
motorMin = 300
motorMax = 400
speedOptions = [(x * 15 + 320) for x in range(0, 10)]
servoMin = 220
servoMax = 400
pulseFrequency = 50 # ESC takes 50 Hz
currentThrottle = 0
servoMiddle = (servoMax + servoMin) // 2
currentDirection = servoMiddle

# Load ML CNN Model
img_input = layers.Input(shape=(image_size, image_size, 3))
x = layers.Conv2D(16, 3, activation='relu')(img_input)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(32, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(64, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Flatten()(x)
x = layers.Dense(512, activation='relu')(x)
output = layers.Dense(1, activation='sigmoid')(x)
model = Model(img_input, output)
model.summary()
# Compile Model
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(lr=0.001),
              metrics=['acc'])
# Load Model
model.load_weights("weights")              
# Model is Ready

def setDirection(results):
    print("Setting Direction")

# Define Camera Function
def processImages():
    global numCycles
    stream = io.BytesIO()
    for i in range(capturesPerCycle):
        yield stream
        stream.seek(0)
        image = Image.open(stream)
        results = model.predict(image)
        print("Camera Results Frame "+ str(i) + ":", results)
        # Turn Wheels
        # pwm.set_pwm(0, 0, setDirection(results))
        stream.seek(0)
        stream.truncate()
    numCycles += 1

with picamera.PiCamera() as camera:
    print("Initialize Camera")
    camera.resolution = (imageWidth, imageHeight)
    camera.color_effects = (128, 128)
    camera.framerate = cameraFramerate
    print("Booting Camera...")
    time.sleep(2)
    print("Booted.")
    print("Starting Main Loop")
    try:
        while True:
            outputs = [io.BytesIO() for i in range(capturesPerCycle)]
            startTime = time.time()
            # Capture Image
            camera.capture_sequence(processImages(), 'jpeg', use_video_port=True)
            endTime = time.time()
            print("Time Taken: ", endTime - startTime)
            print(str(capturesPerCycle) + " images at ", capturesPerCycle / (endTime - startTime), "FPS")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Completed")