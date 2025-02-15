/home/pi/waitnetwork.sh
sudo mount -t cifs //Synology.local/Public /mnt/synology/public -o username=guest,password=,vers=3.0
sudo rpicam-jpeg --output /mnt/synology/public/greenhouse/boot.jpg --immediate --nopreview --verbose=0
cd /home/pi
sudo /home/pi/take_photos.sh &
sudo /usr/bin/python3 -m mqtt_io /home/pi/mqttconfig.yaml & #for GPIO control via HA
sudo /usr/bin/python3 /home/pi/main.py & # for sending sensors to HA
wait
