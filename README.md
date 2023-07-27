**3D annotation Docker Image**


Description
Building docker image for implementing bijection from 2D image onto 3D model in accordance with colmap file architecture.

**File-architecture:**
```
root_path/
	+-- annotation.json
	+-- images/
	+-- models/	
		+-- model.ply
		+-- txt/
			+-- cameras.txt
			+-- images.txt
```

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
