#!/bin/sh

# Start adb then photobooth on boot
sudo rm /tmp/5037
sudo adb start-server
sudo chmod 777 /tmp/5037

cd drumminhands_photobooth


echo 'Waiting for 60 seconds to breakout'
sleep 60

sudo python headless.py