from ..AFactory import AFactory
from ..IRadiant import IRadiant
from ..Entry import Entry
from .ASensor import ASensor
from .Imager import Imager
from .Heterodyne import Heterodyne
from ...lib.logger import logger


class SensorFactory(AFactory):
    """
    A Factory creating objects of the type ASensor
    """

    def __init__(self, common_conf: Entry):
        """
        Instantiate a new factory object

        Parameters
        ----------
        common_conf : Entry
            The common configuration of the configuration file
        """
        super().__init__(common_conf)

    def create(self, options: Entry, parent: IRadiant = None):
        """
        Create a new sensor object

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        parent : IRadiant
            The parent element of the object.
        Returns
        -------
        obj : ASensor
            The created sensor object
        """
        opts = self.collectOptions(options)

        if options.type == "Imager":
            args = dict(parent=parent, **opts, common_conf=self._common_conf)
            if hasattr(options, "center_offset"):
                # noinspection PyCallingNonCallable
                args["center_offset"] = options.center_offset()
            if hasattr(options, "photometric_aperture"):
                if hasattr(options.photometric_aperture, "shape") and isinstance(
                        options.photometric_aperture.shape, Entry):
                    args["shape"] = options.photometric_aperture.shape()
                if hasattr(options.photometric_aperture, "contained_energy") and isinstance(
                        options.photometric_aperture.contained_energy, Entry):
                    args["contained_energy"] = options.photometric_aperture.contained_energy()
                if hasattr(options.photometric_aperture, "aperture_size") and isinstance(
                        options.photometric_aperture.aperture_size, Entry):
                    args["aperture_size"] = options.photometric_aperture.aperture_size()
            return Imager(**args)
        elif options.type == "Heterodyne":
            args = dict(parent=parent, **opts, common_conf=self._common_conf)
            if hasattr(options, "n_on"):
                # noinspection PyCallingNonCallable
                args["n_on"] = options.n_on()
            return Heterodyne(**args)
        else:
            logger.error("Wrong sensor type: " + options.type)
