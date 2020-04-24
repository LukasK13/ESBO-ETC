import esbo_etc as etc
import argparse
import logging
import sys


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

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING if args.logging is None else
                        getattr(logging, args.logging.upper()), stream=sys.stdout)

    conf = etc.Configuration(args.config).conf

    factory = etc.classes.RadiantFactory(conf.common.wl_bins())
    parent = factory.fromConfig(conf)
