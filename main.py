#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import numpy as np
import matplotlib.image as mpimg
import matplotlib.path as mplPath
import open3d as o3d
from read_txt import *

# import argparse
# import jsonargparse


def points_in_polygons(pnts, polygons):
    
    polygons = append(polygons, polygons[0:2])
    polygons = np.array(polygons)
    polygons.shape = (int(len(polygons)/2), 2)
    
    codes = [mplPath.Path.LINETO] * polygons.shape[0]
    codes[0] = mplPath.Path.MOVETO
    codes[-1] = mplPath.Path.CLOSEPOLY
    bbPath = mplPath.Path(polygons, codes)    
    isIn = [bbPath.contains_point(pnt) or bbPath.contains_point(pnt) for pnt in pnts]
    return isIn


def points_in_rectangles(pnts, rectangles, r):
    rectangles = np.array(rectangles)
    rectangles = np.append(rectangles, rectangles[0:2])
    rectangles = np.resize(rectangles, (int(rectangles.shape[0]/2), 2))
    annotation_Points = np.zeros([5, 2])
    annotation_Points[0] = rectangles[0]
    annotation_Points[1] = [rectangles[0][0], rectangles[1][1]]
    annotation_Points[2] = rectangles[1]
    annotation_Points[3] = [rectangles[1][0], rectangles[0][1]]
    annotation_Points[4] = rectangles[0]
    rectangles = annotation_Points
    codes = [mplPath.Path.LINETO] * rectangles.shape[0]
    codes[0] = mplPath.Path.MOVETO
    codes[-1] = mplPath.Path.CLOSEPOLY
    crd = rectangles
    bbPath = mplPath.Path(crd, codes)
    isIn = [bbPath.contains_point(pnt, radius=r) or bbPath.contains_point(pnt, radius=-r) for pnt in pnts]
    return isIn     


def point_in_lines(pnt, lines, r):
    in_line = False
    for n in range(lines.shape[0]-1):
        if abs((pnt[1] - lines[n,1])/(lines[n+1,1] - lines[n,1]) - \
               (pnt[0] - lines[n,0])/(lines[n+1,0] - lines[n,0])) <= r and \
                min(lines[n,0], lines[n+1,0]) <=  pnt[0] and \
                max(lines[n,0], lines[n+1,0]) >=  pnt[0] and \
                min(lines[n,1], lines[n+1,1]) <=  pnt[1] and \
                max(lines[n,1], lines[n+1,1]) >=  pnt[1]:
                in_line = True
    return in_line


def points_in_lines(pnts, lines, r):
    lines = np.array(lines)
    lines = np.resize(lines, (np.int(lines.shape[0]/2),2))
    isIn = [point_in_lines(pnt, lines, r) for pnt in pnts]
    return isIn


def reprojection(pointcloud, P, I):
    location = pointcloud[:, [0, 1, 2]]
    location = np.c_[location, np.ones([len(location), 1])]
    location = np.dot(P, location.T)
    location = location.T
    
    data = np.zeros(np.shape(location))
    for i in range(np.shape(location)[1]):
        data[:, i] = location[:,i]/location[:,2]
    return data, pointcloud


def annotation_highlight(X, Y, data, Pointcloud):
    n = 0
    for y in Y:
        eDist = np.asarray([np.linalg.norm(x - y) for x in X])
        index_a = np.where(eDist == np.min(eDist))
        if n == 0: 
            data_a = data[index_a] 
            pointcloud_a = Pointcloud[index_a]
            isIn_a = index_a
        else:
            data_a = np.concatenate([data_a, data[index_a]], axis=0)
            pointcloud_a = np.concatenate([pointcloud_a, Pointcloud[index_a]], axis=0)
            isIn_a = np.append(isIn_a, index_a, axis=-1) 
        n = n+1
             
    isIn_A = np.ones((np.shape(Pointcloud)[0]), dtype=bool)
    isIn_A = np.logical_not(isIn_A)
    isIn_A[isIn_a] = True             
    return isIn_A


if os.environ['path_get_upload_model']:
    path_get_upload_model = os.environ['path_get_upload_model']
else:
    path_get_upload_model = './data'

if os.environ['model_name']:
    model_name = os.environ['model_name']
else:
    model_name = 'model_211108_194622'

if os.environ['annotation']:
    load_dict = os.environ['annotation']
else:
    load_dict = '{"0":{"annotation":{"rectangles":[],"polygons":[{"color":[23,253,153],"points":[4253,2021,4258,2429,694,2358,35,2313,80,1900]}],"lines":[]},"file_name":"img_211108_160016849755.JPG"}}'

load_dict = json.loads(load_dict)
print("\n load_dict", load_dict)

model_path = os.path.join(path_get_upload_model, 'colmap_output', model_name)
txt_path = os.path.join(model_path, 'txt')

print("\n txt_path", txt_path)

cameras, intrinsics = colmap_read_intrinsics(txt_path)
views = colmap_read_views(txt_path)

PC_name = 'model.ply'

pcd = o3d.io.read_point_cloud(os.path.join(model_path, PC_name))

point = np.asarray(pcd.points) 
color = np.asarray(pcd.colors) * 255
PointCloud = np.concatenate([point, color], axis=-1)

Data = {}
N = 0

image_path = os.path.join(path_get_upload_model, 'images_colmap')

for image_index in load_dict:
    file_name = load_dict[image_index]['file_name']
    for image_key in load_dict[image_index]:
        if image_key == 'annotation':
            for annotation_name in load_dict[image_index][image_key]:
                I = mpimg.imread(os.path.join(image_path, file_name))
                for view in views:
                    if view['filename'] == file_name:
                        P = view['P']
                data, Pointcloud = reprojection(PointCloud, P, I)
                
                pnts = data[:,[0,1]]
                if annotation_name == 'lines':
                    for annotation_inform in load_dict[image_index][image_key][annotation_name]:
                        isIn = points_in_lines(pnts, annotation_inform['points'], r = 0)
                        pointcloud = Pointcloud[isIn]
                        background = Pointcloud[np.logical_not(isIn)]  
                    
                        Y = annotation_inform['points']
                        Y = np.array(Y)
                        Y = np.resize(Y, (np.int(Y.shape[0]/2), 2))
                        X = data[:, [0, 1]]
                        isIn_A = annotation_highlight(X, Y, data, Pointcloud)
                    
                    
                        Data.update({str(N): {'file_name': file_name, 
                                      'annotation': annotation_name,    
                                      'color': annotation_inform['color'], 
                                      'P': P,
                                      'pointcloud': pointcloud,
                                      'pointcloud_a': isIn_A,
                                      'background': background,
                                      'isIn': isIn}})
                        N = N + 1

                elif annotation_name == 'rectangles':

                    for annotation_inform in load_dict[image_index][image_key][annotation_name]:
                        isIn = points_in_rectangles(pnts, annotation_inform['points'], r = 0)
                        pointcloud = Pointcloud[isIn]
                        background = Pointcloud[np.logical_not(isIn)]
        
                        Y = annotation_inform['points']
                        Y = np.array(Y)
                        # Y = np.append(Y, Y[[0,3,1,2]])
                        Y = np.resize(Y, (int(Y.shape[0]/2),2))
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                        Y_m = np.zeros([4,2])
                        Y_m[0] = Y[0]
                        Y_m[1] = [Y[0][0], Y[1][1]]
                        Y_m[2] = Y[1]
                        Y_m[3] = [Y[1][0], Y[0][1]]
                        # Y_m[4] = Y[0]
                        Y = Y_m
                    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                                               
                        X = data[:, [0, 1]]
                        isIn_A = annotation_highlight(X, Y, data, Pointcloud)

                        Data.update({str(N): {'file_name': file_name, 
                                      'annotation': annotation_name,
                                      'color': annotation_inform['color'],
                                      'P': P,
                                      'pointcloud': pointcloud,
                                      'pointcloud_a': isIn_A,
                                      'background': background,
                                      'isIn': isIn}})      
                        N = N + 1

                elif annotation_name == 'polygons':
                    for annotation_inform in load_dict[image_index][image_key][annotation_name]:
                        isIn = points_in_polygons(pnts, annotation_inform['points'])
                        # isIn = points_in_polygons(pnts, annotation_inform['points'], r = 0)

                        pointcloud = Pointcloud[isIn]
                        background = Pointcloud[np.logical_not(isIn)]
  
                        Y = annotation_inform['points']
                        Y = np.array(Y)
                        Y = np.resize(Y, (int(Y.shape[0]/2), 2))

                        X = data[:, [0, 1]]
                        isIn_A = annotation_highlight(X, Y, data, Pointcloud)
                        
                        Data.update({str(N): {'file_name': file_name,
                                      'annotation': annotation_name,
                                      'color': annotation_inform['color'],
                                      'P': P,
                                      'pointcloud': pointcloud,
                                      'pointcloud_a': isIn_A,
                                      'background': background,
                                      'isIn': isIn}})
                        N = N + 1

for annotation_No in Data:

    A = Data[annotation_No]['pointcloud']
    A[:, 3:6] = Data[annotation_No]['color']
    a = Data[annotation_No]['pointcloud_a']

    if annotation_No == '0':
        PCA = A
        isInx = np.logical_not(Data[annotation_No]['isIn']) * np.logical_not(a)
        index_a = a
    else:
        PCA = np.concatenate([PCA, A], axis=0)
        isInx = isInx * np.logical_not(Data[annotation_No]['isIn']) * np.logical_not(a)
        index_a = np.logical_or(index_a, a)

PCB = Pointcloud[isInx]
PC = np.concatenate([PCB, PCA], axis=0)
PC_a = Pointcloud[index_a]

print("index_a", index_a)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(PC[:, 0:3])
pcd.colors = o3d.utility.Vector3dVector(PC[:, 3:6]/255)
o3d.io.write_point_cloud(os.path.join(path_get_upload_model, 'output_model.ply'), pcd)

print("pcd.points", pcd.points)
print("len(pcd.points)", len(pcd.points))