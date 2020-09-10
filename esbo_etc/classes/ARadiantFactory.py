from .AFactory import AFactory
from .Entry import Entry
from .IRadiant import IRadiant
from abc import abstractmethod


class ARadiantFactory(AFactory):
    """
    A Factory creating objects of the type IRadiant
    """

    @abstractmethod
    def __init__(self, common_conf: Entry):
        """
        Instantiate a new factory object

        Parameters
        ----------
        common_conf : Entry
            The common configuration of the configuration file
        """
        super().__init__(common_conf)

    @abstractmethod
    def create(self, options: Entry, parent: IRadiant = None) -> IRadiant:
        """
        Create a new object of the type IRadiant

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        parent : IRadiant
            The optional parent element of the object (necessary for subclasses of AOpticalComponent).
        Returns
        -------
        obj : IRadiant
            The created object
        """
        pass
