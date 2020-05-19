import esbo_etc as eetc
import argparse
import logging
import sys
from logging_spinner import SpinnerHandler
from pyspin.spin import Spin1
from pyfiglet import Figlet
from rich import console, markdown

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(prog="esbo_etc/esbo-etc.py", description='Exposure time calculator for ESBO-DS')
    parser.add_argument("-c", "--config", dest='config', default="esbo-etc_defaults.xml",
                        metavar="config.xml", help="path to the configuration file")
    parser.add_argument("-l", "--logging", dest="logging", default="WARNING", help="print debug information")
    parser.add_argument("-o", "--output-dir", dest="output_dir", help="path to the output directory",
                        default="output")
    parser.add_argument("-v", "--version", action="version", version="ESBO-ETC version 1.0.0",
                        help="show version information")
    parser.add_argument("-m", "--manual", action="store_true", dest="manual",
                        help="print the user manual from the readme")
    args, _ = parser.parse_known_args()  # fix for PyCharm python console

    # Print manual from README.md
    if args.manual:
        console = console.Console()
        with open("README.md") as readme:
            markdown = markdown.Markdown(readme.read())
        console.print(markdown)
        exit(0)

    # Print title
    f = Figlet(font='slant')
    print(f.renderText('ESBO-ETC'))

    # Set up logging
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING if args.logging is None else getattr(
        logging, args.logging.upper()), stream=sys.stdout)
    logger = logging.getLogger('root')
    logger.addHandler(SpinnerHandler(spin_style=Spin1))

    # Parse Configuration
    logging.getLogger("root").info("Parsing configuration...", extra={"user_waiting": True})
    conf = eetc.Configuration(args.config).conf

    # Set up components
    logging.getLogger("root").info("Setting up components...", extra={"user_waiting": True})
    oc_factory = eetc.classes.RadiantFactory(conf.common.wl_bins())
    parent = oc_factory.fromConfigBatch(conf)
    sensor_factory = eetc.SensorFactory(parent, conf.common)
    imager = sensor_factory.create(conf.instrument.sensor)

    # Calculate results
    if hasattr(conf.common, "exposure_time") and hasattr(conf.common, "snr"):
        sensitivity = imager.getSensitivity(conf.common.exposure_time(), conf.common.snr(), conf.astroscene.target.mag)
        eetc.printSensitivity(conf.common.exposure_time(), conf.common.snr(), sensitivity)
    elif hasattr(conf.common, "exposure_time"):
        snr = imager.getSNR(conf.common.exposure_time())
        eetc.printSNR(conf.common.exposure_time(), snr)
    elif hasattr(conf.common, "snr"):
        exp_time = imager.getExpTime(conf.common.snr())
        eetc.printExposureTime(exp_time, conf.common.snr())
    logging.getLogger("root").info("Finished.", extra={"user_waiting": False})
