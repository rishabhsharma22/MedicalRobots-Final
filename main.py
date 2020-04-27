
import os
import moviepy.editor as mp
import cv2
import Detector
import tovid
import time
import math

gif_path = os.path.join(os.getcwd(), "Data", "Source_Images", "insertion.gif")
if not os.path.exists(gif_path):
    print('You need a gif')
    exit(0)

mp4_path = os.path.join(os.getcwd(), "Data", "Source_Images", "insertion.mp4")
test_path = os.path.join(os.getcwd(), "Data", "Source_Images", "Test_Images")
clip = mp.VideoFileClip(gif_path)

if not os.path.exists(mp4_path):
    clip.write_videofile(mp4_path)
    cap = cv2.VideoCapture(mp4_path)
    framen = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        cv2.imwrite(os.path.join(test_path, str(framen) + ".jpg"), frame)
        framen += 1
    cap.release()
    cv2.destroyAllWindows()

results = os.path.join(os.getcwd(), "Data", "Source_Images", "Test_Image_Detection_Results")
if len(os.listdir(results)) == 0:
    Detector.detect()

nFrames = len(os.listdir(results))
duration = clip.duration
fps = nFrames / duration

resultVid = os.path.join(os.getcwd(), "results.mp4")
tovid.conv(results, resultVid, fps)

import csv
with open(os.path.join(os.getcwd(), "Detection_Results.csv")) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')

    rows = []
    skip = True #skip the header row
    for row in readCSV:
        if skip:
            skip = False
            continue
        rows.append(row)
    
    rows.sort(key = lambda x: int((x[0])[0:x[0].index('.')] ))
    startFrame = rows[0]
    endFrame = rows[len(rows)-1]
    startFrameN = (startFrame[0])[0:(startFrame[0]).index('.')]
    endFrameN = (endFrame[0])[0:(endFrame[0]).index('.')]
    framesElapsed = float(endFrameN) - float(startFrameN)
    timeElapsed = framesElapsed / fps
    
    startx = float(startFrame[2])
    starty = float(startFrame[3])
    startboxwidth = float(startFrame[len(startFrame)-2])
    startboxheight = float(startFrame[len(startFrame)-1])
    startx += startboxwidth / 2
    starty += startboxheight / 2

    stopx = float(endFrame[2])
    stopy = float(endFrame[3])
    stopboxwidth = float(endFrame[len(endFrame)-2])
    stopboxheight = float(endFrame[len(endFrame)-1])
    stopx += stopboxwidth / 2
    stopy += stopboxheight / 2

    abVec = [stopx - startx, stopy - starty]
    magnitude = math.sqrt(abVec[0] ** 2 + abVec[1] ** 2)
    speedInCm = magnitude * .0264
    answer = speedInCm / timeElapsed
    print('THE SPEED IS', answer, 'cm/s!!!')

cap = cv2.VideoCapture("results.mp4")
while (cap.isOpened()):
    ret, frame = cap.read()

    now = time.time()

    if ret:
        cv2.imshow("Image", frame)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    timeDiff = time.time() - now
    if (timeDiff < 1.0 / fps):
        time.sleep(1.0 / fps)

cap.release()
cv2.destroyAllWindows()

