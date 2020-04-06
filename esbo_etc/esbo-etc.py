import esbo_etc
import argparse
import logging
import sys
import os


def run_exosim(opt=None):
    pass
    # star, planet = exosim.modules.astroscene.run(opt)
    #
    # exosim_msg(' Stellar SED: {:s}\n'.format(os.path.basename(star.ph_filename)))
    # exosim_msg(' Star luminosity {:f}\n'.format(star.luminosity))
    #
    # # Instanciate Zodi
    # zodi = exosim.classes.zodiacal_light(opt.common.common_wl, level=1.0)
    #
    # exosim.exolib.sed_propagation(star.sed, zodi.transmission)
    # # Run Instrument Model
    # channel = exosim.modules.instrument.run(opt, star, planet, zodi)
    # # Create Signal timelines
    # frame_time, total_observing_time, exposure_time = exosim.modules.timeline_generator.run(opt, channel, planet)
    # # Generate noise timelines
    # exosim.modules.noise.run(opt, channel, frame_time, total_observing_time, exposure_time)
    # # Save
    # exosim.modules.output.run(opt, channel, planet)
    #
    # return star, planet, zodi, channel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="esbo_etc/esbo-etc.py", description='Exposure time calculator for ESBO-DS')
    parser.add_argument("-c", "--config", dest='config', default="esbo-etc_defaults.xml",
                        metavar="config.xml", help="path to the configuration file")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="print debug information")
    parser.add_argument("-o", "--output-dir", dest="output_dir", help="path to the output directory",
                        default="output")
    parser.add_argument("-v", "--version", action="version", version="ESBO-ETC version 1.0.0",
                        help="show version information")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.debug else logging.WARNING,
                        stream=sys.stdout)

    conf = esbo_etc.Configuration(filename=args.config).conf

    # run_exosim(opt)
