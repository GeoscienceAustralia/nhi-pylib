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
    "tmax": float,
    "tmaxq": str,
    "tmaxdays": int,
    "tmin": float,
    "tminq": str,
    "tmindays": str,
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
    "duststorm": str,
    "duststormq": str,
    "snow": str,
    "snowq": str,
    "haze": str,
    "hazeq": str,
    "hail": str,
    "hailq": str,
    "fog": str,
    "fogq": str,
    "thunder": str,
    "thunderq": str,
    "frost": str,
    "frostq": str,
    "end": str,
}

DAILYNAMES = list(DAILYDTYPE.keys())

DAILYDTYPE2021 = {
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

DAILYNAMES2021 = list(DAILYDTYPE2021.keys())

WXCODES = {
    0: "Fine", 1: "Fine", 2: "Fine", 3: "Fine",
    4: "Smoke", 5: "Haze", 6: "Dust", 7: "Dust",
    8: "Dust whirls", 9: "Dust storm",
    10: "Mist", 11: "Fog patches", 12: "Shallow fog",
    13: "Lightning", 14: "Distant/nearby virga",
    15: "Distant precipitation", 16: "Distant precipitation",
    17: "Thunder", 18: "Squall", 19: "Funnel cloud",
    20: "Recent drizzle", 21: "Recent rain", 22: "Recent snow",
    23: "Recent rain and snow", 24: "Recent precipitation",
    25: "Recent shower", 26: "Recent snow", 27: "Recent hail",
    28: "Recent fog", 29: "Recent thunderstorm", 30: "Dust storm",
    31: "Dust storm", 32: "Dust storm", 33: "Severe dust storm",
    34: "Severe dust storm", 35: "Severe dust storm",
    36: "Drifting snow", 37: "Drifting snow", 38: "Blowing snow",
    39: "Blowing snow", 40: "Distant fog", 41: "Fog patches",
    42: "Fog", 43: "Fog", 44: "Fog", 45: "Fog", 46: "Fog",
    47: "Fog", 48: "Fog", 49: "Fog", 50: "Drizzle",
    51: "Drizzle", 52: "Drizzle", 53: "Drizzle", 54: "Drizzle",
    55: "Drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle",
    58: "Drizzle", 59: "Drizzle", 60: "Rain", 61: "Rain",
    62: "Rain", 63: "Rain", 64: "Rain", 65: "Rain",
    66: "Freezing rain", 67: "Freezing rain", 68: "Sleet",
    69: "Sleet", 70: "Snow", 71: "Snow", 72: "Snow",
    73: "Snow", 74: "Snow", 75: "Snow", 76: "Ice prisms",
    77: "Snow grains", 78: "Starlike crystals", 79: "Ice pellets",
    80: "Shower", 81: "Shower", 82: "Violent shower", 83: "Sleet",
    84: "Sleet", 85: "Snow shower", 86: "Snow shower",
    87: "Soft hail shower", 88: "Soft hail shower",
    89: "Hail shower", 90: "Hail shower", 91: "Thunderstorm",
    92: "Thunderstorm", 93: "Thunderstorm", 94: "Thunderstorm",
    95: "Thunderstorm", 96: "Thunderstorm and hail",
    97: "Heavy thunderstorm", 98: "Thunderstorm and dust",
    99: "Thunderstorm and hail"
}
