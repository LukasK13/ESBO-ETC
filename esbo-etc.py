import esbo_etc as eetc
import argparse
from esbo_etc.lib.logger import logger
import logging
from pyfiglet import Figlet
from rich import console, markdown

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(prog="esbo-etc.py", description='Exposure time calculator for ESBO-DS')
    parser.add_argument("-c", "--config", dest='config', default="esbo-etc_defaults.xml",
                        metavar="config.xml", help="Path to the configuration file. Default is esbo-etc_defaults.xml.")
    parser.add_argument("-l", "--logging", dest="logging", default="WARNING",
                        help="Log level for the application. Possible levels are DEBUG, INFO, WARNING, ERROR.")
    parser.add_argument("-v", "--version", action="version", version="ESBO-ETC version 1.0.0",
                        help="Show version information.")
    parser.add_argument("-m", "--manual", action="store_true", dest="manual",
                        help="Print the user manual from the readme.")
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
    print("")
    print(f.renderText('ESBO-ETC'))

    # Initialize the ETC
    etc = eetc.esbo_etc(args.config,
                        logging.WARNING if args.logging is None else getattr(logging, args.logging.upper()), True)
    # Run the computation
    res = etc.run()

    # Print the results
    if hasattr(etc.conf.common, "exposure_time") and hasattr(etc.conf.common, "snr"):
        eetc.printSensitivity(etc.conf.common.exposure_time(), etc.conf.common.snr(), res)
    elif hasattr(etc.conf.common, "exposure_time"):
        eetc.printSNR(etc.conf.common.exposure_time(), res)
    elif hasattr(etc.conf.common, "snr"):
        eetc.printExposureTime(res, etc.conf.common.snr())
    logger.info("Finished.", extra={"spinning": False})
