#!/bin/sh

sudo rm rawframes/*
cd LeptonModule/software/raspberrypi_video
make
sudo cp ~/.Xauthority /r.oot
sudo ./raspberrypi_video -tl 3 -cm 2