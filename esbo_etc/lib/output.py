from rich.console import Console
from rich.table import Table
import astropy.units as u


def printSNR(exp_time: u.Quantity, snr: u.Quantity):
    """
    Print the results of the SNR calculation.

    Parameters
    ----------
    exp_time : Quantity
        The exposure times for which the SNR was calculated.
    snr : Quantity
        The corresponding SNR for the exposure times.

    Returns
    -------

    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("Exposure Time", justify="right")
    table.add_column("SNR", justify="right")
    for i, exp_time_, snr_ in zip(range(len(exp_time)), exp_time.value, snr.value):
        table.add_row(str(i), ("%1.4e " + exp_time.unit.to_string()) % exp_time_, "%1.4e" % snr_)
    console = Console()
    console.print(table)


def printExposureTime(exp_time: u.Quantity, snr: u.Quantity):
    """
    Print the results of the exposure time calculation.

    Parameters
    ----------
    exp_time : Quantity
        The corresponding exposure time for the SNRs.
    snr : Quantity
        The SNRs for which the exposure time was calculated.

    Returns
    -------

    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("SNR", justify="right")
    table.add_column("Exposure Time", justify="right")
    for i, exp_time_, snr_ in zip(range(len(exp_time)), exp_time.value, snr.value):
        table.add_row(str(i), "%1.4e" % snr_, ("%1.4e " + exp_time.unit.to_string()) % exp_time_)
    console = Console()
    console.print(table)


def printSensitivity(exp_time: u.Quantity, snr: u.Quantity, sensitivity: u.Quantity):
    """
    Print the results of the sensitivity calculation.

    Parameters
    ----------
    exp_time : Quantity
        The exposure times for which the sensitivity was calculated.
    snr : Quantity
        The SNRs for which the sensitivity was calculated.
    sensitivity : Quantity
        The corresponding sensitivity for the exposure times and SNRs.

    Returns
    -------

    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("Exposure Time", justify="right")
    table.add_column("SNR", justify="right")
    table.add_column("Sensitivity", justify="right")
    for i, exp_time_, snr_, sensitivity_ in zip(range(len(exp_time)), exp_time.value, snr.value, sensitivity.value):
        table.add_row(str(i), ("%1.4e " + exp_time.unit.to_string()) % exp_time_, "%1.4e" % snr_,
                      ("%1.4e " + sensitivity.unit.to_string()) % sensitivity_)
    console = Console()
    console.print(table)
