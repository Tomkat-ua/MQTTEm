
container=EMQTTEm
img=tomkat/emqttem

docker build -t $img .


docker container stop $container
docker container rm $container

#ports - host:container
docker run -d  -p 8084:80 \
    --net net_18  --ip 172.18.0.9 \
    --restart always \
    --name $container \
    -e TZ=Europe/Kiev \
    -e SERVER_PORT=80 \
    -e GET_DELAY=10 \
    -e BROKER_IP='172.18.0.2' \
    -e BROKER_PORT=1883 \
    -e SENSOR_REAL_COUTNER_NAME='em1_1_energy_meter'  \
    -e SENSOR_REAL_COUTNER_VALUE=5678 \
    -e TOPIC_PATTERN='monitors/+/#'  \
    -e USERNAME='mqtt' \
    -e PASSWORD='mqtt001' \
       $img