
container=EMQTTEx
img=tomkat/emqttex

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
    -e TOPIC='esphome/meteo1/sensor/#' \
    -e USERNAME='mqtt' \
    -e PASSWORD='mqtt001' \
       $img