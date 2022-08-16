IN_FOLDER="/home/zzzz/Projects/77347d5333c34d5ead4e8e28e8f0e142"
CON_FOLDER="/app/data"

ANNOTATION='{"0":{"annotation":{"rectangles":[],"polygons":[{"color":[23,253,153],"points":[4253,2021,4258,2429,694,2358,35,2313,80,1900]}],"lines":[]},"file_name":"img_211108_160016849755.JPG"}}' 

docker run -v $IN_FOLDER:$CON_FOLDER \
 -e model_name="model_211108_194622" \
 -e annotation=$ANNOTATION \
 -u $(id -u):$(id -g) \
 r20