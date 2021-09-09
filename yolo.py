import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
import datetime
import MySQLdb
import requests
import base64
from yolo_utils import infer_image, show_image, convertToBinaryData
import pickle
import pafy
import threading 
import socket
import sys
import urllib.parse

FLAGS = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--model-path',
        type=str,
        default='./yolov3-coco/',
        help='The directory where the model weights and \
        configuration files are.')
        
    parser.add_argument('-w', '--weights',
        type=str,
        default='./yolov3-coco/yolov3-custom_140000.weights',
        help='Path to the file which contains the weights \
        for YOLOv3.')

    parser.add_argument('-cfg', '--config',
        type=str,
        default='./yolov3-coco/yolov3.cfg',
        help='Path to the configuration file for the YOLOv3 model.')

    parser.add_argument('-i', '--image-path',
        type=str,
        help='The path to the image file')

    parser.add_argument('-v', '--video-path',
        type=str,
        help='The path to the video file')

    parser.add_argument('-vo', '--video-output-path',
        type=str,
        help='The path of the output video file')

    parser.add_argument('-l', '--labels',
        type=str,
        default='./yolov3-coco/coco-labels',
        help='Path to the file having the \
        labels in a new-line seperated way.')

    parser.add_argument('-c', '--confidence',
        type=float,
        default=0.5,
        help='The model will reject boundaries which has a \
        probability less than the confidence value. \
        default: 0.5')

    parser.add_argument('-th', '--threshold',
        type=float,
        default=0.3,
        help='The threshold to use when applying the \
        Non-Max Suppression')

    parser.add_argument('--download-model',
        type=bool,
        default=False,
        help='Set to True if the model weights and configurations \
        are not present on your local machine.')

    parser.add_argument('-t', '--show-time',
        type=bool,
        default=False,
        help='Show the time taken to infer each image.')

    parser.add_argument("-u", "--use-gpu", type=bool, default=True,
        help="Boolean indicating if CUDA GPU should be used")

    FLAGS, unparsed = parser.parse_known_args()

    # Download the YOLOv3 models if needed
    if FLAGS.download_model:
        subprocess.call(['./yolov3-coco/get_model.sh'])

    # Get the labels
    labels = open(FLAGS.labels).read().strip().split('\n')

    # Initializing colors to represent each label uniquely
    colors = np.random.randint(100, 255, size=(len(labels), 3), dtype='uint8')

    # Load the weights and configuration to form the pretrained YOLOv3 model
    net = cv.dnn.readNetFromDarknet(FLAGS.config, FLAGS.weights)

    if FLAGS.use_gpu:
        # set CUDA as the preferable backend and target
        print("[INFO] setting preferable backend and target to CUDA...")
        net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        print("[INFO] successful")

    # Get the output layer names of the model
    layer_names = net.getLayerNames()
    layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # If both image and video files are given then raise error
    if FLAGS.image_path is None and FLAGS.video_path is None:
        print('Neither path to an image or path to video provided')
        print('Starting Inference on DJI Tello Cam')

    # Do inference with given image
    if FLAGS.image_path:
        # Read the image
        try:
            img = cv.imread(FLAGS.image_path)
            height, width = img.shape[:2]
        except:
            raise 'Image cannot be loaded!\n\
                    Please check the path provided!'
        finally:
            img, _, _, _, _ = infer_image(
            net, layer_names, height, width, img, colors, labels, FLAGS)
            show_image(img)

    elif FLAGS.video_path:
        
        # Read the video
        count = 0
        support = True

        if "https://www.youtube.com/" in FLAGS.video_path:
            url = FLAGS.video_path
            vPafy = pafy.new(url)
            play = vPafy.getbest(preftype="mp4")
            vid = cv.VideoCapture(play.url)
            print("[INFO] Opening Youtube Video...")
        else:
            vid = cv.VideoCapture(FLAGS.video_path)
            print("[INFO] Opening Local Video...")
        
        starting_time = time.time()
        frame_id = 0
        writer = None
        while True:
            ret, frame = vid.read()

            if frame is None:
                break
                writer.release()
            
            frame_id += 1
            height, width = frame.shape[:2]
            timestamp = datetime.datetime.now()
            cv.putText(frame, timestamp.strftime("%A, %d %B %Y %I:%M:%S %p"), (10, frame.shape[0] - 10),cv.FONT_HERSHEY_DUPLEX, 0.50, (200, 200, 0), 2)

            if count == 0:
                frame, boxes, confidences, classids, idxs = infer_image(net, layer_names,
                height, width, frame, colors, labels, FLAGS)
                count += 1
            else:
                frame, boxes, confidences, classids, idxs = infer_image(net, layer_names,
                height, width, frame, colors, labels, FLAGS, boxes, confidences, classids, idxs, infer=False)
                count = (count + 1) % 6
                
            if FLAGS.video_output_path is not None:
                if writer is None:
                    # Initialize the video writer
                    fourcc = cv.VideoWriter_fourcc(*"H264")
                    writer = cv.VideoWriter(FLAGS.video_output_path, 0x00000021, 20.0, (frame.shape[1], frame.shape[0]), True)
                writer.write(frame)

            elapsed_time = time.time() - starting_time
            fps = frame_id / elapsed_time
            print("Avg FPS: " + str(round(fps,2)))

            if not confidences:
                print(labels[0] + ": " + "not detected" + "\n")
                    
            elif confidences:
                print(labels[0] + ": " + "{:.2%}".format(max(confidences)) + "\n")
                if max(confidences) >= 0.80 and support == True:
                    
                    # Get latitude, longitude and city
                    
                    

                    address = '127.0.0.1'
                    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

                    response = requests.get(url).json()
                    print(response[0]["lat"])
                    print(response[0]["lon"])

                    #res = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=127.0.0.1')
                    #data = res.json()
                    #print(data['results'][0]['geometry']['location'])
                    #location = data['loc'].split(',')
                    #latitude = location[0]
                    #ongitude = location[1]
                        
                    directory = r'C:\Users\bruno\Downloads'
                    os.chdir(directory)
                    frame2 = cv.imwrite('temp.jpg', frame)

                    image = convertToBinaryData(r'C:\Users\bruno\Downloads\temp.jpg')
                    con = MySQLdb.connect(host="localhost", user="root", passwd="Lab_Proj_7", db="projeto")
                    cursor = con.cursor()

                    sql = "INSERT INTO detections (frame, latitude, longitude, datadadetecao, percentagemdadetecao, fps, createdAt, updatedAt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    val = (image, latitude, longitude, timestamp, float(round(max(confidences) * 100, 2)), float(round(fps, 2)), timestamp, timestamp)
                    cursor.execute(sql, val)
                    con.commit()
                    support = False
                    
            cv.imshow('video', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
                writer.release()

        print("[INFO] Cleaning up...")
        
        vid.release()
        
    else:
        # Infer real-time on DJI Tello

        host = ''
        port = 9000
        locaddr = (host,port) 

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tello_address = ('192.168.10.1', 8889)
        sock.bind(locaddr)
        data, server = sock.recvfrom(1518)
        recvThread = threading.Thread(target=recv)
        recvThread.start()
        msg1 = "command"
        msg2 = "streamon"
        msg1 = msg1.encode(encoding="utf-8")
        msg2 = msg2.encode(encoding="utf-8") 
        sent = sock.sendto(msg1, tello_address)
        sent = sock.sendto(msg2, tello_address)

        count = 0
        support = True
        vid = cv.VideoCapture("udp://0.0.0.0:11111")
        starting_time = time.time()
        frame_id = 0
        writer = None
        
        while True:
            ret, frame = vid.read()
            print("[INFO] Opening DJI Tello Camera...")
            if ret:
                frame_id += 1
                height, width = frame.shape[:2]
                timestamp = datetime.datetime.now()
                cv.putText(frame, timestamp.strftime("%A, %d %B %Y %I:%M:%S %p"), (10, frame.shape[0] - 10),cv.FONT_HERSHEY_DUPLEX, 0.50, (200, 200, 0), 2)
                if count == 0:
                    frame, boxes, confidences, classids, idxs = infer_image(net, layer_names,
                    height, width, frame, colors, labels, FLAGS)
                    count += 1
                else:
                    frame, boxes, confidences, classids, idxs = infer_image(net, layer_names,
                    height, width, frame, colors, labels, FLAGS, boxes, confidences, classids, idxs, infer=False)
                    count = (count + 1) % 6
                    
                if FLAGS.video_output_path is not None:
                    if writer is None:

                        # Initialize the video writer
                        fourcc = cv.VideoWriter_fourcc(*"H264")
                        writer = cv.VideoWriter(FLAGS.video_output_path, 0x00000021, 20.0, (frame.shape[1], frame.shape[0]), True)
                    writer.write(frame)

                elapsed_time = time.time() - starting_time
                fps = frame_id / elapsed_time
                print("Avg FPS: " + str(round(fps,2)))

                if not confidences:
                    print(labels[0] + ": " + "not detected" + "\n")
                    
                elif confidences:
                    print(labels[0] + ": " + "{:.2%}".format(max(confidences)) + "\n")
                    if max(confidences) >= 0.80 and support == True:
                        
                        # Get latitude, longitude and city
                        res = requests.get('https://ipinfo.io/')
                        data = res.json()
                        location = data['loc'].split(',')
                        latitude = location[0]
                        longitude = location[1]
                        
                        directory = r'C:\Users\bruno\Downloads'
                        os.chdir(directory)
                        frame2 = cv.imwrite('temp.jpg', frame)

                        image = convertToBinaryData(r'C:\Users\bruno\Downloads\temp.jpg')
                        con = MySQLdb.connect(host="localhost", user="root", passwd="Lab_Proj_7", db="projeto")
                        cursor = con.cursor()

                        sql = "INSERT INTO detections (frame, latitude, longitude, datadadetecao, percentagemdadetecao, fps, createdAt, updatedAt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                        val = (image, latitude, longitude, timestamp, float(round(max(confidences) * 100, 2)), float(round(fps, 2)), timestamp, timestamp)
                        cursor.execute(sql, val)
                        con.commit()
                        support = False
                cv.imshow('video', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
                writer.release()
        print("[INFO] Cleaning up...")
        
        vid.release()
        cv.destroyAllWindows()
