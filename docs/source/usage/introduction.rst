************
Introduction
************

ESBO-ETC aims on modelling the physical aspect of light coming from a target through optical components
(e.g. atmosphere, mirrors, lenses, ...) onto the detector. The set up of this so called optical pipeline can be
individually defined using a configuration file. Additionally, the thermal emission of optical components, the
obstruction of components as well as different PSFs including pointing jitter can be considered.

Finally, ESBO-ETC allows the computation of either the necessary exposure time for a desired SNR, the SNR for a given
exposure time or, in case of a BlackBodyTarget, the sensitivity as the minimum apparent magnitude for a given exposure
time and SNR. All computations support a batch-mode, allowing to compute multiple set ups at once.
