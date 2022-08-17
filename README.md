**3D annotation Docker Image**


Description
Building docker image for implementing bijection from 2D image onto 3D model in accordance with colmap file architecture.

**File-architecture:**
```
path_get_upload_model/
+--images_colmap/
+--colmap_output/
   +--model_name/
      +--model.ply
      +--database.db
      +--bin/
      +--txt/
         +--project.ini
	 +--cameras.txt
	 +--images.txt
         +--points3D.json
         +--points3D.txt
+--images/
+--images_segmentation/
+--log/
+--vis/
```



`path_get_upload_model/` - the path where we get all data for 3D image annotation from. Into this path generated `output_model.ply` would be uploaded.

`images_colmap/` - images without noise and downscaled. The experiments showed that these images can be used instead of original images for image annotation as they have smaller image size which leads to reducing time consumption of evaluating the final 3D model.

`colmap_output/` - comprises all essential data for 3D model generating process including:   
`model.ply` - model without annotation;    
`cameras.txt` - camera list with one line of data per camera;   
`images.txt` - image list with two lines of data per image.   

`images/` - original images.
  
`images_segmentation/` - the masks of the slopes.   

**How to run:**

`./path_get_upload_model` - main path with input data for 3D generation process.

`./path/data` - the path where to copy input data for running

```
docker run -v ./path_get_upload_model: ./path/data \
 -e path_get_upload_model="./77347d5333c34d5ead4e8e28e8f0e142" \
 -e model_name="model_211108_194622" \
 -e annotation= "annotation_string" \
 zvyozdo4ka/csms4
```

**How to build without Docker**

python main.py --load_dict '{"0":{"annotation":{"rectangles":[],"polygons":[{"color":[23,253,153],"points":[4439,3258,1083,3175,1111,2386,5451,2506]}],"lines":[]},"file_name":"img_211108_160622977760.JPG"},"1":{"annotation":{"rectangles":[{"color":[233,53,68],"points":[2188,2630,5439,3104]}],"polygons":[],"lines":[]},"file_name":"img_211108_160016849755.JPG"}}'
