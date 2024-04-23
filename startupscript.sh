#!/bin/sh

sudo rm rawframes/*
cd LeptonModule/software/raspberrypi_video
make
sudo cp ~/.Xauthority /root
sudo ./raspberrypi_video -tl 3 -cm 2
cd /home/remote/FireDetection