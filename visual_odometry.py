import os
import numpy as np
import cv2
import time

import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix

from bokeh.models.widgets import Panel, Tabs
from bokeh.io import output_file, show
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import column, layout, gridplot
from bokeh.models import Div, WheelZoomTool
from bokeh.models.widgets import Panel, Tabs

from tqdm import tqdm


class VisualOdometry():
    def __init__(self): 
        self.orb            = cv2.ORB_create(3000)
        self.dist           = np.matrix([[0.1874, -0.5038, -0.0043, 0.0061, 0.1470]])
        self.K_pre          = np.matrix([[2704, 0, 1611], [0, 2704, 1239], [0, 0 , 1]])
        self.K              = np.matrix([[2704, 0, 1611], [0, 2704, 1239], [0, 0 , 1]])
        self.R              = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0 , 1]])
        self.old_image      = None
        self.current_image  = None
        FLANN_INDEX_LSH     = 6
        index_params        = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
        search_params       = dict(checks=50)
        self.flann          = cv2.FlannBasedMatcher(indexParams=index_params, searchParams=search_params)

  

    @staticmethod
    def _form_transf(R, t):

        T = np.eye(4, dtype=np.float64)
        T[:3, :3] = R
        T[:3, 3] = t
        return T

    def get_matches(self): 

        kp1, des1 = self.orb.detectAndCompute(self.old_image, None)
        kp2, des2 = self.orb.detectAndCompute(self.current_image, None)
        matches = self.flann.knnMatch(des1, des2, k=2) 

        good = []
        for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append(m)

        #draw_params = dict(matchColor = -1,
        #         singlePointColor = None,
        #         matchesMask = None, 
        #        flags = 2)

        #img3 = cv2.drawMatches(self.current_image, kp1, self.old_image,kp2, good ,None,**draw_params)
        #cv2.imshow("image", img3)
        #cv2.waitKey(100)

        q1 = np.float32([kp1[m.queryIdx].pt for m in good])
        q2 = np.float32([kp2[m.trainIdx].pt for m in good])
        return q1, q2


    def get_pose(self, q1, q2):

        E, _ = cv2.findEssentialMat(q1, q2, self.K)

        [_,R, t,p] = cv2.recoverPose(E, q1, q2)
        t = np.matrix([[1, 1, 0]]).T
        R = np.round(R,2)
        t = np.round(t,2)
        transformation_matrix = self._form_transf(R, np.squeeze(t))
        return transformation_matrix
    






