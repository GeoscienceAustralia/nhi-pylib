"""
A collection of data formats for BoM weather station data, including the
observation files and the station detail files.

One place to store these, so they can be imported quickly into any code.

Current collection includes one-minute observation data and daily maximum wind
gust data.

These only define the names and dtypes of the attributes, leaving any parsing
of dates, NA values, etc. to the user.


Use case:
---------

Loading 1-minute observation data from `obsfile`:

.. code::

    >>> from stndata import ONEMINUTENAMES, ONEMINUTEDTYPE
    >>> df = pd.read_csv(obsfile, sep=',', index_col=False,
                         dtype=ONEMINUTEDTYPE,
                         names=ONEMINUTENAMES, header=0,
                         parse_dates={'datetime':[7, 8, 9, 10, 11]},
                         na_values=['####'], skipinitialspace=True)


Loading stations that have daily maximum wind speed data:

.. code::

    >>> from stndata import DAILYSTNDTYPE, DAILYSTNNAMES
    >>> stndf = pd.read_csv(stnfile, sep=',', index_col='stnNum',
                            dtype=DAILYSTNDTYPE,
                            names=DAILYSTNNAMES)
"""

# One minute observations data type:
# This data includes two versions of the time: local time and
# local __standard__ time, the latter does not include daylight savings changes

ONEMINUTESTNDTYPE = {
    "id": str,
    "stnNum": int,
    "rainfalldist": str,
    "stnName": str,
    "stnOpen": str,
    "stnClose": str,
    "stnLat": float,
    "stnLon": float,
    "stnLoc": str,
    "stnState": str,
    "stnElev": float,
    "stnBarometerElev": float,
    "stnWMOIndex": int,
    "stnDataStartYear": str,
    "stnDataEndYear": str,
    "pctComplete": float,
    "pctY": float,
    "pctN": float,
    "pctW": float,
    "pctS": float,
    "pctI": float,
    "end": str,
}

ONEMINUTESTNNAMES = list(ONEMINUTESTNDTYPE.keys())

ONEMINUTEDTYPE = {
    "id": str,
    "stnNum": int,
    "YYYY": int,
    "MM": int,
    "DD": int,
    "HH": int,
    "MI": int,
    "YYYYl": int,
    "MMl": int,
    "DDl": int,
    "HHl": int,
    "MIl": int,
    "rainfall": float,
    "rainq": str,
    "rain_duration": float,
    "temp": float,
    "tempq": str,
    "temp1max": float,
    "temp1maxq": str,
    "temp1min": float,
    "temp1minq": str,
    "dewpoint": float,
    "dewpointq": str,
    "windspd": float,
    "windspdq": str,
    "windmin": float,
    "windminq": str,
    "winddir": float,
    "winddirq": str,
    "windgust": float,
    "windgustq": str,
    "mslp": float,
    "mslpq": str,
    "stnp": float,
    "stnpq": str,
    "end": str,
}

ONEMINUTENAMES = list(ONEMINUTEDTYPE.keys())

ONEMINUTEDTYPE2022 = {
    "id": str,
    "stnNum": int,
    "YYYY": int,
    "MM": int,
    "DD": int,
    "HH": int,
    "MI": int,
    "YYYYl": int,
    "MMl": int,
    "DDl": int,
    "HHl": int,
    "MIl": int,
    "rainfall": float,
    "rainq": str,
    "rain_duration": float,
    "temp": float,
    "tempq": str,
    "temp1max": float,
    "temp1maxq": str,
    "temp1min": float,
    "temp1minq": str,
    "wbtemp": float,
    "wbtempq": str,
    "dewpoint": float,
    "dewpointq": str,
    "rh": float,
    "rhq": str,
    "windspd": float,
    "windspdq": str,
    "windmin": float,
    "windminq": str,
    "winddir": float,
    "winddirq": str,
    "windsd": float,
    "windsdq": str,
    "windgust": float,
    "windgustq": str,
    "mslp": float,
    "mslpq": str,
    "stnp": float,
    "stnpq": str,
    "end": str,
}

ONEMINUTENAMES2022 = list(ONEMINUTEDTYPE2022.keys())


# 2021 version:
ONEMINUTEDTYPE2021 = {
    "id": str,
    "stnNum": int,
    "YYYY": int,
    "MM": int,
    "DD": int,
    "HH": int,
    "MI": int,
    "YYYYl": int,
    "MMl": int,
    "DDl": int,
    "HHl": int,
    "MIl": int,
    "rainfall": float,
    "rainq": str,
    "rain_duration": float,
    "temp": float,
    "tempq": str,
    "dewpoint": float,
    "dewpointq": str,
    "rh": float,
    "rhq": str,
    "windspd": float,
    "windspdq": str,
    "winddir": float,
    "winddirq": str,
    "windsd": float,
    "windsdq": str,
    "windgust": float,
    "windgustq": str,
    "mslp": float,
    "mslpq": str,
    "stnp": float,
    "stnpq": str,
    "end": str,
}

ONEMINUTENAMES2021 = list(ONEMINUTEDTYPE2021.keys())

# Daily maximum wind gust data type:
# Station open/close dates are stored as MM/YYYY (strings)

DAILYSTNDTYPE = {
    "id": str,
    "stnNum": int,
    "rainfalldist": str,
    "stnName": str,
    "stnOpen": str,
    "stnClose": str,
    "stnLat": float,
    "stnLon": float,
    "stnLoc": str,
    "stnState": str,
    "stnElev": float,
    "stnBarmoeterElev": float,
    "stnWMOIndex": int,
    "stnDataStartYear": str,
    "stnDataEndYear": str,
    "pctComplete": float,
    "pctY": float,
    "pctN": float,
    "pctW": float,
    "pctS": float,
    "pctI": float,
    "end": str,
}

DAILYSTNNAMES = list(DAILYSTNDTYPE.keys())

DAILYDTYPE = {
    "id": str,
    "stnNum": int,
    "YYYY": int,
    "MM": int,
    "DD": int,
    "windgust": float,
    "windgustq": str,
    "winddir": float,
    "winddirq": str,
    "HHMM": int,
    "timeq": str,
    "PresentWx00": int,
    "PresentWx00Q": str,
    "PresentWx03": int,
    "PresentWx03Q": str,
    "PresentWx06": int,
    "PresentWx06Q": str,
    "PresentWx09": int,
    "PresentWx09Q": str,
    "PresentWx12": int,
    "PresentWx12Q": str,
    "PresentWx15": int,
    "PresentWx15Q": str,
    "PresentWx18": int,
    "PresentWx18Q": str,
    "PresentWx21": int,
    "PresentWx21Q": str,
    "PastWx00": int,
    "PastWx00Q": str,
    "PastWx03": int,
    "PastWx03Q": str,
    "PastWx06": int,
    "PastWx06Q": str,
    "PastWx09": int,
    "PastWx09Q": str,
    "PastWx12": int,
    "PastWx12Q": str,
    "PastWx15": int,
    "PastWx15Q": str,
    "PastWx18": int,
    "PastWx18Q": str,
    "PastWx21": int,
    "PastWx21Q": str,
    "end": str,
}

DAILYNAMES = list(DAILYDTYPE.keys())
