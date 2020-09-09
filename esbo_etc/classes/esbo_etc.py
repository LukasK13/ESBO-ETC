import esbo_etc as eetc
from esbo_etc.lib.logger import logger
import logging as log
import astropy.units as u


class esbo_etc:
    """
    Top level class of the exposure time calculator
    """

    def __init__(self, config: str = "esbo-etc_defaults.xml", logging: int = log.WARNING, spin: bool = False):
        """
        Initialize a new exposure time calculator (ETC)

        Parameters
        ----------
        config : str
            Path to the configuration file
        logging : int
            Loglevel from package logging
        spin : bool
            Show a spinner during computations
        """
        self.__config = config
        self.__logging = logging
        self.__spin = spin
        self.conf = None

    def run(self) -> u.Quantity:
        """

        Returns
        -------
        res: Quantity
            The result of the computation. Depending on the input parameters, this will be either a dimensionless
            signal-to-noise ratio (SNR), an exposure time in seconds or a sensitivity in apparent magnitues.
        """
        # Set up logging
        logger.setLevel(log.WARNING if self.__logging is None else self.__logging)
        if self.__spin:
            logger.addHandler(eetc.SpinnerHandler())

        # Parse Configuration
        logger.info("Parsing configuration...", extra={"spinning": True})
        self.conf = eetc.Configuration(self.__config).conf

        # Set up components
        logger.info("Setting up components...", extra={"spinning": True})
        oc_factory = eetc.classes.RadiantFactory(self.conf.common.wl_bins())
        parent = oc_factory.fromConfigBatch(self.conf)
        sensor_factory = eetc.SensorFactory(parent, self.conf.common)
        detector = sensor_factory.create(self.conf.instrument.sensor)

        # Calculate results
        res = None
        if hasattr(self.conf.common, "exposure_time") and hasattr(self.conf.common, "snr"):
            res = detector.getSensitivity(self.conf.common.exposure_time(), self.conf.common.snr(),
                                          self.conf.astroscene.target.mag)
        elif hasattr(self.conf.common, "exposure_time"):
            res = detector.getSNR(self.conf.common.exposure_time())
        elif hasattr(self.conf.common, "snr"):
            res = detector.getExpTime(self.conf.common.snr())
        return res
