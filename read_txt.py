#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 08:19:24 2021

@author: yw546
"""

import os
from numpy import *
import re
from PIL import Image


def get_re_scale(path):
    image_path = os.path.abspath(os.path.join(path, ".."))
    image_path = os.path.abspath(os.path.join(image_path, "..", ".."))
    image_path = os.path.abspath(os.path.join(image_path, "images_colmap"))

    with open(os.path.join(path, 'images.txt'),'r') as fp:
        lines = fp.readlines()   
    filename = lines[4].split()[9]

    image_name = os.path.abspath(os.path.join(image_path, filename))
    img = Image.open(image_name)
    img_size = asarray(img.size)

    with open(os.path.join(path,'cameras.txt')) as fp:
        lines = fp.readlines()
    re_img_size = array(lines[3].split()[2:4]).astype('int')
    re_scale = img_size[0]/re_img_size[0]

    return re_scale

#
# cameras.txt    Intrinsics
#
def colmap_read_intrinsics(path):
# Camera list with one line of data per camera:
#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]
# Number of cameras: 1
    
    re_scale = get_re_scale(path)
    
    with open(os.path.join(path,'cameras.txt')) as fp:
        lines = fp.readlines()
    del lines[0:3]

    cameras = []
    for line in lines:
        camera_id = int(line[0])
        camera_type = line[1]
        cparam = array(line.split()[2:]).astype('float')
#         intrinsics = {
#             'Fx':cparam[2],
#             'Fy':cparam[3],
#             'Cx':cparam[4],
#             'Cy':cparam[5],
#             'R1':cparam[6],
#             'R2':cparam[7],
#             'R3':None,
#             'T1':cparam[8],
#             'T2':cparam[9],
#             'K' :array([[cparam[2]*re_scale,0,cparam[4]*re_scale],
#                         [0,cparam[3]*re_scale,cparam[5]*re_scale],
#                         [0,        0,        1]]),
#                        }

        if camera_type == "SIMPLE_PINHOLE":
            intrinsics = {
                'Fx':cparam[2],
                'Fy':cparam[3],
                'Cx':cparam[4],
                'Cy':cparam[4],
                'K' :array([[cparam[2]*re_scale,0,cparam[4]*re_scale],
                            [0,cparam[3]*re_scale,cparam[4]*re_scale],
                            [0,        0,        1]]),
                           }
        else:
            intrinsics = {
                'Fx':cparam[2],
                'Fy':cparam[3],
                'Cx':cparam[4],
                'Cy':cparam[5],
                'K' :array([[cparam[2]*re_scale,0,cparam[4]*re_scale],
                            [0,cparam[3]*re_scale,cparam[5]*re_scale],
                            [0,        0,        1]]),
                           }


        cameras.append({'camera id':camera_id, 'camera type':camera_type, 'intrinsics':intrinsics})
    return cameras, intrinsics


#
# images.txt  camera extrinsics, feature detection/matching
#
def quaterion2rotation(q):
    return array([
        [1-2*(q[2]**2+q[3]**2), 2*(q[1]*q[2]-q[3]*q[0]), 2*(q[1]*q[3]+q[2]*q[0])],
        [2*(q[1]*q[2]+q[3]*q[0]), 1-2*(q[1]**2+q[3]**2), 2*(q[2]*q[3]-q[1]*q[0])],
        [2*(q[1]*q[3]-q[2]*q[0]), 2*(q[2]*q[3]+q[1]*q[0]), 1-2*(q[1]**2+q[2]**2)],
    ])


def colmap_read_views(path):
# For each image there are two lines as following
#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
#   POINTS2D[] as (X, Y, POINT3D_ID)
    cameras, intrinsics = colmap_read_intrinsics(path)
    with open(os.path.join(path, 'images.txt'),'r') as fp:
        lines = fp.readlines()
    nImages = int(re.search(":\s(\d+),",lines[3]).group(1))
    del lines[0:4]   
    
    # images=[{filename,P, keypoints, tiepoints_viewcounts}...]
    views = []
    for i in range(nImages):
        extrinsics = lines[2*i].split()
        keypoints = lines[2*i+1].split()
        image_id = int(extrinsics[0])
        q = array(extrinsics[1:5]).astype(float)
        t = array(extrinsics[5:8]).astype(float)
        camera_id = int(extrinsics[8])
        filename = extrinsics[9]

        R = quaterion2rotation(q)
        P = intrinsics['K'].dot(concatenate((R,array([t]).T),axis=1))
        point2d = array(keypoints).astype(float).reshape((-1,3))

        views.append({'filename':filename, 'P':P, 'x_y_tpid':point2d,'image id':image_id,'camera id':camera_id})
    return views


def colmap_get_tps(views):    
    x_y_tpid = zeros((0,3),dtype='float')
    for idx,view in enumerate(views):
        x_y_tpid = concatenate((x_y_tpid,view['x_y_tpid']),axis=0)
        views[idx]['tp_counts']=view['x_y_tpid'].shape[0]
    tpid_max = int(max(x_y_tpid[:,2]))

    tps = [{'viewcounts':0} for i in range(tpid_max+1)]
    for tp in x_y_tpid:
        tps[int(tp[2])]['viewcounts'] += 1
        
    return tps, views