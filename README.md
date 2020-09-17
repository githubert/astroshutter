# astroshutter

Some scripts that I use in order to capture astrophotography pictures.

## Remote shutter

I built my own, simple remote shutter that can be used to control my camera.
The code for this is in the `arduino/` folder.

## camera-control.py

The script needs the guider module from https://github.com/agalasso/phd2client

This is a simple script that allows me to capture arbitrarily long exposures.
My camera can't capture for longer than 60 seconds, but if the bulb mode is
used, longer exposures can be done.

The script also supports asking PHD2 to dither the next exposure.
