# -*- coding: utf-8 -*-

import yaml
import numpy as np
import cv2
from datetime import datetime
import openpyxl

start_time = datetime.now()
last_time = datetime.now()

ct = 0
total_output = 0
fastest = 0
ppm = 0
ppm_average = 0

#record counting every a qty
rec_qty=8
qty = 0

#prepare for excel file
path = "../output/"
wb = openpyxl.Workbook()
ws = wb.active
ws.append(("datetime","total_output","minute","average ppm","ct","ppm"))

fn_yaml = r"C:\Users\your directory\area.yml"
fn_out = r"../datasets/output.avi"
config = {'save_video': False,
          'text_overlay': True,
          'object_overlay': True,
          'object_id_overlay': False,
          'object_detection': True,
          'min_area_motion_contour': 60,
          'park_sec_to_wait': 0.001,
          'start_frame': 0} #35000

# Set capture device 0 for builtcam, 1 for USB cam
cap = cv2.VideoCapture(0)

if config['save_video']:
	fourcc = cv2.VideoWriter_fourcc('D','I','V','X')# options: ('P','I','M','1'), ('D','I','V','X'), ('M','J','P','G'), ('X','V','I','D')
	out = cv2.VideoWriter(fn_out, -1, 25.0,(video_info['width'], video_info['height']))

# Read YAML data
with open(fn_yaml, 'r') as stream:
	object_area_data = yaml.safe_load(stream)
object_contours = []
object_bounding_rects = []
object_mask = []
for park in object_area_data:
	points = np.array(park['points'])
	rect = cv2.boundingRect(points)
	points_shifted = points.copy()
	points_shifted[:,0] = points[:,0] - rect[0] 
	#shift contour to roi
	points_shifted[:,1] = points[:,1] - rect[1]
	object_contours.append(points)
	object_bounding_rects.append(rect)
	mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint8), [points_shifted], contourIdx=-1,color=255, thickness=-1, lineType=cv2.LINE_8)
	mask = mask==255
	object_mask.append(mask)

object_status = [False]*len(object_area_data)
object_buffer = [None]*len(object_area_data)

print ("Program for counting objects that pass through lines\nLarge frame size 960x720")
while(cap.isOpened()): 
    try:
        # Read frame-by-frame    
        video_cur_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 # Current position of the video file in seconds
        ret, frame = cap.read()
        if ret == False:
            print("Capture Error")
            break

        frame_blur = cv2.GaussianBlur(frame.copy(), (5,5), 3)
        frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
        frame_out = frame.copy()
        

        if config['object_detection']:        
            for ind, park in enumerate(object_area_data):
                points = np.array(park['points'])
                rect = object_bounding_rects[ind]
                roi_gray = frame_gray[rect[1]:(rect[1]+rect[3]), rect[0]:(rect[0]+rect[2])] # crop roi for faster calculation   
                # print np.std(roi_gray)

                points[:,0] = points[:,0] - rect[0] # shift contour to roi
                points[:,1] = points[:,1] - rect[1]

                status = np.std(roi_gray) < 20 and np.mean(roi_gray) > 56

                if status != object_status[ind] and object_buffer[ind]==None:	
                    object_buffer[ind] = video_cur_pos

                # If status is still different than the one saved and counter is open
                elif status != object_status[ind] and object_buffer[ind]!=None:
                    if video_cur_pos - object_buffer[ind] > config['park_sec_to_wait']:
                        if status==False:
                            qty = qty+1
                            total_output = total_output+1
                            current_time = datetime.now()
                            diff = current_time-last_time
                            ct = diff.total_seconds()
                            ppm = round(60/ct,2)
                            last_time = current_time

                            diff = current_time-start_time
                            minutes = diff.total_seconds() / 60
                            ppm_average = round(total_output/minutes,2)

                            if (ppm>fastest):
                                fastest = ppm
                                data = (current_time,total_output,minutes,ppm_average,ct,ppm)
                                ws.append(data)

                            if (qty>rec_qty):
                                #record to excel
                                data = (current_time,total_output,minutes,ppm_average,ct,ppm)
                                ws.append(data)
                                qty=0
                                

                        object_status[ind] = status
                        object_buffer[ind] = None
                        # If status is still same and counter is open                    
                elif status == object_status[ind] and object_buffer[ind]!=None:
                        #if video_cur_pos - object_buffer[ind] > config['park_sec_to_wait']:
                    object_buffer[ind] = None                    
                        # print(object_status)
        
        if config['object_overlay']:    

            for ind, park in enumerate(object_area_data):
                points = np.array(park['points'])
                if object_status[ind]: 
                    color = (0,255,0)
                else: 
                    color = (0,0,255)
                cv2.drawContours(frame_out, [points], contourIdx=-1,color=color, thickness=2, lineType=cv2.LINE_8)            
                moments = cv2.moments(points)        
                centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
                cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)


            # Draw Overlay
        if config['text_overlay']:
            #cv2.rectangle(frame_out, (1, 5), (280, 70),(255,255,255), 85) 
            cv2.rectangle(frame_out, (1, 5), (350, 70),(0,255,0), 2)
            str_on_frame = "Object Counting:"
            cv2.putText(frame_out, str_on_frame, (5,20), cv2.FONT_HERSHEY_SIMPLEX ,0.5, (0,0,255), 2, cv2.LINE_AA)
            str_on_frame = "Total Counting = %d, Speed (PPM) = %d" % (total_output, ppm)
            cv2.putText(frame_out, str_on_frame, (5,40), cv2.FONT_HERSHEY_SIMPLEX ,0.5, (0,0,255), 2, cv2.LINE_AA)
            str_on_frame = "Fastest PPM: " + str(fastest) + ", Average: " + str(ppm_average)
            cv2.putText(frame_out, str_on_frame, (5,60), cv2.FONT_HERSHEY_SIMPLEX ,0.5, (255,255,0), 1, cv2.LINE_AA)
     
        
        # Display video
        imS = cv2.resize(frame_out, (960,720))
        cv2.imshow('Output Counting - by Yaser Ali Husen', imS)
        cv2.waitKey(1)
            # cv2.imshow('background mask', bw)
        k = cv2.waitKey(1)


            
    except KeyboardInterrupt:
        data = (current_time,total_output,minutes,ppm_average,ct,ppm)
        ws.append(data)
        wb.save(path + "output_" + start_time.strftime("%d-%m-%Y %H-%M-%S") + ".xlsx")
        print("Actual Speed (PPM):" + str(ppm_average))
        exit()
cap.release()
if config['save_video']: out.release()
cv2.destroyAllWindows()    
