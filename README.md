[![Build Status](https://jenkins.lklass.de/buildStatus/icon?job=esbo_ds%2FESBO-ETC%2Fmaster)](https://jenkins.lklass.de/job/esbo_ds/job/ESBO-ETC/job/master/)

# ESBO-ETC
A modular exposure time calculator for the ESBO telescope.

## Introduction
This repository contains the source code of the ESBO-ETC, a highly modular exposure time calculator.

ESBO-ETC aims on modelling the physical aspect of light coming from a target through optical components
(e.g. atmosphere, mirrors, lenses, ...) on the detector. The set up of this so called optical pipeline can be
individually defined using a configuration file. Additionally, the thermal emission of optical components, the
obstruction of components as well as different PSFs including pointing jitter can be considered.

Finally, ESBO-ETC allows the computation of either the necessary exposure time for a desired SNR, the SNR for a given
exposure time or, in case of a BlackBodyTarget, the sensitivity as the minimum apparent magnitude for a given exposure
time and SNR. All computations support a batch-mode, allowing to compute multiple scenarios at once.

## Full Documentation
The full documentation is available as source [here](docs) and can be build using
[sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html) by the command
```bash
sphinx-build -b html
```

for the HTML-documentation or

```bash
sphinx-build -M latexpdf
```

for the PDF version.