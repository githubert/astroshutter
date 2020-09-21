"""Capture and control exposures.

Usage:
    camera-control [--exposure=<exposure>] [--count=<count>] [--pause=<pause>] [--dither]
                   [--phd2-host=<phd2-host>] [--serial-port=<serial-port>] [--dark-every=<exposures>]
    camera-control --help


Options:
    -h --help                       Show this screen.
    -e --exposure=<exposure>        Exposure length in seconds [default: 300].
    -n --count=<count>              Number of exposures to make [default: -1].
    -p --pause=<pause>              Pause between exposures in seconds [default: 5].
    -d --dither                     Use dithering [default: False].
    --dark-every=<exposures>        Interactively ask for creating a dark every n exposures [default: 0].
    --phd2-host=<phd2-host>         PHD2 host name [default: localhost].
    --serial-port=<serial-port>      Serial port [default: /dev/ttyUSB0].
"""

import serial
import time
import signal
import sys
from docopt import docopt
from guider import Guider


def main():
    arguments = docopt(__doc__)

    phd2_host: str = arguments['--phd2-host']
    serial_port: str = arguments['--serial-port']
    exposure: int = int(arguments['--exposure'])
    count: int = int(arguments['--count'])
    pause: int = int(arguments['--pause'])
    dither: bool = arguments['--dither']
    dark_every: int = int(arguments['--dark-every'])

    current_exposure = 0
    dark: bool = False

    print("Looping with %ds exposure, %ds pause, %susing dithering." %
          (exposure, pause, "" if dither else "not "))

    interrupted = False
    guider = None
    ser = None

    def handle_sigint(sig, frame):
        """
        Allow the script to quit gracefully. Hit Ctrl-C twice in order to exit immediately.
        """
        nonlocal interrupted
        nonlocal guider

        if interrupted:
            print("Aborting immediately.")

            if guider is not None:
                guider.Disconnect()

            if ser is not None:
                ser.write(b'c')
                ser.flush()
                ser.close()

            sys.exit()

        print("Abort requested after current exposure.")
        interrupted = True

    signal.signal(signal.SIGINT, handle_sigint)

    # Initialize PHD2 connection only when dithering is in use
    if dither:
        guider = Guider(phd2_host)
        guider.Connect()

    with serial.Serial(serial_port, 9600, timeout=1) as ser:
        # Wait magical two seconds for the serial interface to settle
        print("Waiting for serial interface.")
        time.sleep(2)
        print("Begin first exposure.")

        while True:
            current_exposure += 1

            if dark_every != 0 and (current_exposure % dark_every) == 0:
                dark = True
                input("Dark frame requested, please put on cap and press enter to continue.")

            do_exposure(exposure, ser)

            if dark:
                input("Dark frame done, please remove cap and press enter to continue.")
                dark = False

            if count == -1:
                print(f"Exposure {current_exposure} done.")
            else:
                print(f"Exposure {current_exposure} of {count} done.")

            if count != -1 and current_exposure >= count:
                print("All exposures done. Exiting.")
                break

            if interrupted:
                print("Exiting.")
                break

            if dither:
                do_dither(guider)

            print(f"Next exposure in {pause:d}s.")
            time.sleep(pause)

    if guider is not None:
        guider.Disconnect()


def do_exposure(exposure, ser):
    """
    Perform one exposure.

    :param exposure: Exposure time in seconds.
    :param ser: Serial interface to use for controlling the remote shutter.
    """
    ser.write(b'r')
    print("", end='\r')
    for i in range(exposure, 0, -1):
        print(f"\x1b[2K{i}s left.", end='\r')
        time.sleep(1)
    ser.write(b'c')


def do_dither(guider):
    """
    Instruct PHD2 to dither, waiting a moment for to settle before being ready for the next exposure.

    :param guider: Connection to PHD2 to use.
    """
    print("Dithering", end='')
    guider.Dither(1.0, 2.0, 10.0, 30.0)
    while True:
        if guider.CheckSettling().Done:
            print()
            break
        else:
            print('.', end='', flush=True)

        time.sleep(1)


if __name__ == "__main__":
    # execute only if run as a script
    main()
