import esbo_etc as eetc
import argparse
import logging
import sys
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="esbo_etc/esbo-etc.py", description='Exposure time calculator for ESBO-DS')
    parser.add_argument("-c", "--config", dest='config', default="esbo-etc_defaults.xml",
                        metavar="config.xml", help="path to the configuration file")
    parser.add_argument("-l", "--logging", dest="logging", default="WARNING", help="print debug information")
    parser.add_argument("-o", "--output-dir", dest="output_dir", help="path to the output directory",
                        default="output")
    parser.add_argument("-v", "--version", action="version", version="ESBO-ETC version 1.0.0",
                        help="show version information")
    args, _ = parser.parse_known_args()  # fix for PyCharm python console

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING if args.logging is None else getattr(
        logging, args.logging.upper()), stream=sys.stdout)

    conf = eetc.Configuration(args.config).conf

    oc_factory = eetc.classes.RadiantFactory(conf.common.wl_bins())
    parent = oc_factory.fromConfigBatch(conf)
    sensor_factory = eetc.SensorFactory(parent, conf.common)
    imager = sensor_factory.create(conf.instrument.sensor)

    if hasattr(conf.common, "exposure_time") and hasattr(conf.common, "snr"):
        sensitivity = imager.getSensitivity(conf.common.exposure_time(), conf.common.snr(), conf.astroscene.target.mag)
        print("The limiting apparent magnitude is: " + str(np.array2string(sensitivity.value, precision=2)) + " mag.")
    elif hasattr(conf.common, "exposure_time"):
        snr = imager.getSNR(conf.common.exposure_time())
        print("The SNR is: " + str(np.array2string(snr.value, precision=2)) + ".")
    elif hasattr(conf.common, "snr"):
        exp_time = imager.getExpTime(conf.common.snr())
        print("The necessary exposure time is: " + str(np.array2string(exp_time.value, precision=2)) + " s.")
