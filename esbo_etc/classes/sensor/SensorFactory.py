from ..IRadiant import IRadiant
from ..Entry import Entry
from .ASensor import ASensor
from .Imager import Imager
from ...lib.logger import logger


class SensorFactory:
    """
    A Factory creating objects of the type ASensor
    """
    def __init__(self, parent: IRadiant, common_conf: Entry):
        """
        Instantiate a new factory object
        """
        self.__common_conf = common_conf
        self.__parent = parent

    def create(self, options: Entry) -> ASensor:
        """
        Create a new object of the type ASensor

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        Returns
        -------
        obj : ASensor
            The created sensor object
        """
        if options.type == "Imager":
            args = dict(parent=self.__parent, quantum_efficiency=options.pixel.quantum_efficiency(),
                        pixel_geometry=options.pixel_geometry(), pixel_size=options.pixel.pixel_size(),
                        read_noise=options.pixel.sigma_read_out(), dark_current=options.pixel.dark_current(),
                        well_capacity=options.pixel.well_capacity(), f_number=options.f_number(),
                        common_conf=self.__common_conf)
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
                if hasattr(options.photometric_aperture, "contained_pixels") and isinstance(
                        options.photometric_aperture.contained_pixels, Entry):
                    args["contained_pixels"] = options.photometric_aperture.contained_pixels()
            return Imager(**args)
        else:
            logger.error("Wrong sensor type: " + options.type)
