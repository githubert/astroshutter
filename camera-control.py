"""Capture and control exposures.

Usage:
    camera-control [--exposure=<exposure>] [--pause=<pause>] [--dither=<dither>]
                   [--phd2-host=<phd2-host>] [--serial-port=<serial-port>]
    camera-control --help


Options:
    -h --help                       Show this screen.
    -e --exposure=<exposure>        Exposure length in seconds [default: 300].
    -p --pause=<pause>              Pause between exposures in seconds [default: 5].
    -d --dither=<dither>            Use dithering [default: False].
    --phd2-host=<phd2-host>         PHD2 host name [default: localhost].
    --serial-port=<serialport>      Serial port [default: /dev/ttyUSB0].
"""

import serial
import time
import signal
import sys
from docopt import docopt
from guider import Guider

def main():
    arguments = docopt(__doc__)

    phd2_host = arguments['--phd2-host']
    serial_port = arguments['--serial-port']
    exposure = int(arguments['--exposure'])
    pause = int(arguments['--pause'])
    dither = arguments['--dither'] == 'True'

    print("Looping with %ds exposure, %ds pause, %susing dithering." %
            (exposure, pause, "not " if dither == False else ""))

    interrupted = False
    guider = False

    def handle_sigint(sig, frame):
        nonlocal interrupted
        nonlocal guider

        if interrupted:
            print("Aborting immediately.")

            if guider != False:
                guider.Disconnect()

            sys.exit()

        print("Abort requested after current exposure.")
        interrupted = True


    signal.signal(signal.SIGINT, handle_sigint)

    if dither:
        guider = Guider(phd2_host)
        guider.Connect()

    with serial.Serial(serial_port, 9600, timeout=1) as ser:
        while True:
            ser.write(b'r')

            print("", end='\r')
            for i in range(exposure, 0, -1):
                print(f"\x1b[2K{i}s left.", end='\r')
                time.sleep(1)

            ser.write(b'c')
            print("Exposure done.")

            if interrupted:
                print("Exiting.")
                break

            if dither:
                print("Dithering", end='')
                guider.Dither(1.0, 2.0, 10.0, 30.0)

                while True:
                    if guider.CheckSettling().Done:
                        print()
                        break
                    else:
                        print('.', end='', flush=True)

                    time.sleep(1)

            print("Next exposure in %ds." % (pause))
            time.sleep(pause)

    if guider != False:
        guider.Disconnect()

main()
