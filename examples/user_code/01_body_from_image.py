import sys
import cv2
import numpy as np
import argparse

sys.path.append('../../python')
from openpose import pyopenpose as op

# Flags
parser = argparse.ArgumentParser()
parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
args = parser.parse_known_args()

# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "../../../models/"
params["model_pose"] = "COCO"
params["net_resolution"] = "256x-1" #"128x-1" #"256x-1"

# Starting OpenPose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

# Process Image
cap = cv2.VideoCapture('../../../../media/raw_stream_2_processed.mp4')
#cap = cv2.VideoCapture(0)
datum = op.Datum()

i = 0
frameskip = 0

while(cap.isOpened()):
    ret, frame = cap.read()

    if not ret:
        break

    # when running on video files, skip 25 frames
    if frameskip<5:
        frameskip = frameskip+1
        continue
    else:
        frameskip = 0
    
    i=i+1

    #if i<600: #skip 500 frames for now
    #    continue
    
    datum.cvInputData = frame
    opWrapper.emplaceAndPop([datum])
    img = datum.cvOutputData

    noOfPeople = 0

    if (len(datum.poseKeypoints.shape) == 3):
        noOfPeople = datum.poseKeypoints.shape[0]
        print("People:", noOfPeople)

        # check whether person requires urgent help
        # criteria - right wrist above right elbow above right shoulder
        # or right wrist invisible and right elbow above right shoulder
        # and/or left wrist or left elbow above left shoulder
        # or left wrist invisible and left elbow above left shoulder

        for j in range(noOfPeople):
            right = datum.poseKeypoints[j][2:5]
            left = datum.poseKeypoints[j][5:8]

            flag = False
            if(right[0][2] > 0.2 and right[1][2] > 0.2 and right[2][2]):
                if (right[0][1] > right[1][1] and right[1][1] > right[2][1]):
                    flag = True
            elif(right[0][2] > 0.2 and right[1][2] > 0.2):
                if (right[0][1] > right[1][1]):
                    flag = True
            
            if(left[0][2] > 0.2 and left[1][2] > 0.2 and left[2][2]):
                if (left[0][1] > left[1][1] and left[1][1] > left[2][1]):
                    flag = True
            elif(left[0][2] > 0.2 and left[1][2] > 0.2):
                if (left[0][1] > left[1][1]):
                    flag = True
            
            if (flag):
                print("Person {} - Urgent help required".format(j+1))

            # draw box around person
            minx,maxx,miny,maxy = np.Infinity,-np.Infinity,np.Infinity,-np.Infinity

            for arr in datum.poseKeypoints[j]:
                if arr[2] > 0.2:
                    if (arr[0] < minx):
                        minx = arr[0]
                    
                    if (arr[0] > maxx):
                        maxx = arr[0]
                    
                    if (arr[1] < miny):
                        miny = arr[1]
                    
                    if (arr[1] > maxy):
                        maxy = arr[1]
            
            if (minx is not np.Infinity and miny is not np.Infinity and maxx is not -np.Infinity and maxy is not -np.Infinity):
                miny = int(miny-30)
                minx = int(minx-30)
                maxx = int(maxx+30)
                maxy = int(maxy+30)

                boxcolor = (0, 255, 255)
                boxtext = "Person {}".format(j+1)
                boxtextoffset = 50
                if (flag):
                    boxcolor = (0, 0, 255)
                    boxtext = "Person {} - Urgent help required".format(j+1)
                    boxtextoffset = 180
                
                img = cv2.rectangle(img, (minx, miny), (maxx, maxy), boxcolor, 2)
                img = cv2.putText(img, boxtext, (int((minx+maxx)/2)-boxtextoffset,miny-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,boxcolor,2,cv2.LINE_AA)
    else:
        # no people in the frame
        print("People:", noOfPeople)

    print()
    img = cv2.putText(img, 'Frame: {}'.format(i+1),(20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255),2,cv2.LINE_AA)
    img = cv2.putText(img, 'People: {}'.format(noOfPeople),(20,img.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255),2,cv2.LINE_AA)
    cv2.imshow('frame', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()