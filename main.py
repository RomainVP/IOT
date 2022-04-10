# This is client code to receive video frames over UDP
import cv2, imutils, socket
import matplotlib as plt
import numpy as np
import time
import base64
from visual_odometry import *
import threading
import queue

BUFF_SIZE = 65536
queue = queue.Queue()

class UseVisualOdometry(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
                
    def run(self):
        vo = VisualOdometry()
        vo.K, _ = cv2.getOptimalNewCameraMatrix(vo.K, vo.dist, (3280,2464), 1, (300,400))
        print(vo.K)
        cur_pose = np.matrix([[0, 0, 0, 1]]).T;        
        plt.axis([0,50,0,50])
        plt.title("Real time Visual Odometry")
        plt.xlabel("x")
        plt.ylabel("y")
        x = []
        y = []
        vo.old_image = queue.get()

        while(True):
            vo.current_image = queue.get()
            q1, q2 = vo.get_matches()
            transf = vo.get_pose(q1, q2)
            print(transf)
            print(cur_pose)
            cur_pose = transf.dot(cur_pose)

            x.append(cur_pose.tolist()[0])
            y.append(cur_pose.tolist()[1])
    
            plt.plot(x,y)

            plt.pause(.001) 
            
            vo.old_image = vo.current_image

        
        
        
        

class ReadCamera(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.current_image = None
        self.old_image = None
        self.client_socket = None
    def run(self):
        client_ip = '192.168.1.17'
        client_port = 9000
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        self.client_socket.bind((client_ip, client_port))
                
        host_ip = '192.168.1.74'
        host_port = 4000
        print("Debut de communication")
        message = b'Hello'

        self.client_socket.sendto(message,(host_ip,host_port))
        fps,st,frames_to_count,cnt = (0,0,20,0)
        
        while(True):
            packet,_ = self.client_socket.recvfrom(BUFF_SIZE)
            data = base64.b64decode(packet,' /')
            npdata = np.fromstring(data,dtype=np.uint8)
            frame = cv2.imdecode(npdata,1)
            queue.put(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.imshow("RECEIVING VIDEO",frame)
            key = cv2.waitKey(1) & 0xFF
            if (key == ord('q')):
                self.client_socket.close()
                cv2.destroyAllWindows()
                exit(-1)
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            cnt+=1         
            

r = ReadCamera()
r.start()
queue.get()
queue.get()
v = UseVisualOdometry()
v.start()

    

