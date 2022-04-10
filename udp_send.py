# This is server code to send video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64
import threading 

BUFF_SIZE = 65536 
host_ip = '192.168.1.74'
port = 4000

class MonThread (threading.Thread):
    def __init__(self, vid, socket):      # jusqua = donnée supplémentaire
        threading.Thread.__init__(self)  # ne pas oublier cette ligne
        # (appel au constructeur de la classe mère)
        self.vid = vid
        self.server_socket = socket

    def run(self):  
        FPS_DESIRED = 5
        start_time = time.time()
        fps,st,frames_to_count,cnt = (0,0,20,0)
        WIDTH = 400
       	while(True):
            _,frame = self.vid.read()
            frame = imutils.resize(frame,WIDTH)
            encoded,buffer = cv2.imencode('.jpeg',frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            message = base64.b64encode(buffer)
            self.server_socket.sendto(message,client_addr)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.server_socket.close()
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            while(time.time() - start_time < 1/FPS_DESIRED):
                None
            start_time = time.time()
        cnt+=1


server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

host_name = socket.gethostname()
socket_address = (host_ip,port)
server_socket.bind(socket_address)

print('Listening at:',socket_address)

vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam

while True:
    msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    print('GOT connection from ',client_addr)
    #WIDTH=800
    m = MonThread(vid, server_socket)
    m.run()
