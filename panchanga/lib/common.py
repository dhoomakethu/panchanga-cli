# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import os
from datetime import datetime
from collections import namedtuple as struct
import difflib
import time
from dateutil import parser as dateparser
import geocoder
from pytz import timezone
import errno

Date = struct('Date', ['year', 'month', 'day'])
Place = struct('Location', ['latitude', 'longitude', 'timezone', 'timezone_hr'])
TODAY = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
CONFIG_FILE = os.path.expanduser("~/.panchanga/config.json")

CURFILE_PATH = os.path.abspath(__file__)
CUR_DIR = os.path.abspath(os.path.join(CURFILE_PATH, os.pardir))
PARENT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.pardir))

DATA_DIR = os.path.join(PARENT_DIR, "data")


class PlaceNotFound(object):
    def __init__(self, msg):
        self.msg = msg


class DB(object):
    sktnames = None
    cities = None
    defaults = None

    def __init__(self, config_dir, offline=False, load_cities=False):
        if not self.defaults:
            self.load_config()

        self.sktnames, self.cities = self.init_db(config_dir, offline,
                                                  load_cities)

    def init_db(self, config_dir, offline=False, load_cities=False):
        """
        Initialize city and sanskrit name databases

        :return:
        cities and sanskrit names
        """
        files = ["sanskrit_names.json"]
        if offline and load_cities:
            files.append("cities.json")
        p_data = []
        for f in files:
            f = os.path.join(config_dir, f)
            with open(f) as fp:
                p_data.append(json.load(fp))
        p_data[0] = SanskritNameSpace(p_data[0])
        if len(p_data) == 1:
            p_data.append(None)
        return p_data

    def get_place(self, lat, long, timezone, tzname):
        """
        Returns Place object from a given lat, long and timzone
        :param lat:
        :param long:
        :param timzone:
        :return: Place Object
        """
        lat = float(lat)
        lon = float(long)
        tz = float(timezone)
        return Place(lat, lon, tz, tzname)

    def find_nearest_city(self, city):
        nearest = difflib.get_close_matches(city, self.cities, 5)
        all_matches = ""
        for m in nearest:
            all_matches += m + '\n'
        return all_matches

    def search_location(self, place, date):
        date = parse_date(date)
        if self.cities:
            if not place in self.cities.keys():
                all_matches = self.find_nearest_city(place)
                extra = "Did you mean any of these?\n" + all_matches if all_matches else ""
                msg = ("Supplied place '{}' not found!\n".format(place) + extra)
                return PlaceNotFound(msg), date
            else:
                place = self.cities[place]
        else:
            place = self.defaults

        lat = place['latitude']
        lon = place['longitude']
        tzname = place['timezone']
        tzone = timezone(tzname)
        tz_offset = compute_timezone_offset(date, tzone)
        place = Place(lat, lon, tz_offset, place['timezone'])
        return place, date

    def resolve_location(self, place, date, strict=False, offline=False):
        """
        Resolves a provided place/address with google maps api and returns
        latitude, longitude and timezone
        :param place: Address/Place name/ [latitude, longitude]
        :param date: Date time stamp
        :param strict: Matches exact place name otherwise returns approximate place
        :param offline: Resolve offline
        :return: (city, latitude, longitude, timezone)

        """
        if offline:
            place, date = self.search_location(place, date)

        else:
            info = geocoder.google(place, method="timezone")
            lat, lng = info.location.split(",")
            tzone = timezone(info.timeZoneId)
            tzone = compute_timezone_offset(date, tzone)
            place = self.get_place(lat, lng, tzone, info.timeZoneId)
            date = parse_date(date)
        return place, date

    @classmethod
    def load_config(cls):
        """
        Loads default config from ~/.panchanga/config.json file
        if the file does not exists, it will be created
        :return:
        """

        if not os.path.exists(CONFIG_FILE):
            cls.defaults = {
                "place": "Bangalore",
                "latitude": 12.971600,
                "longitude": 77.594597,
                "timezone": "Asia/Kolkata"
            }
            try:
                os.makedirs(os.path.dirname(CONFIG_FILE))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

            with open(CONFIG_FILE, "w+") as f:
                json.dump(cls.defaults, f, indent=4)
        else:
            with open(CONFIG_FILE) as f:
                cls.defaults = json.load(f)
        return cls.defaults

    def save_config(self, place, place_info):
        p = {
            "place": place,
            "latitude": place_info.latitude,
            "longitude": place_info.longitude,
            "timezone": place_info.timezone_hr
        }
        with open(CONFIG_FILE, "w+") as f:
            json.dump(p, f, indent=4)


class SanskritNameSpace(object):

    def __init__(self, name_dict):
        self._sktnames = name_dict

    @property
    def tithis(self):
        return self._sktnames["tithis"]

    @property
    def nakshatras(self):
        return self._sktnames["nakshatras"]

    @property
    def vaaras(self):
        return self._sktnames["varas"]

    @property
    def yogas(self):
        return self._sktnames["yogas"]

    @property
    def karanas(self):
        return self._sktnames["karanas"]

    @property
    def masas(self):
        return self._sktnames["masas"]

    @property
    def samvats(self):
        return self._sktnames["samvats"]

    @property
    def ritus(self):
        return self._sktnames["ritus"]

    @property
    def rashis(self):
        return self._sktnames["raashi"]

    @property
    def ayanas(self):
        return self._sktnames["ayanas"]


def format_time(t):
    """
    format time
    :param t: datetime object
    :return:
    """
    return "%02d:%02d:%02d" % (t[0], t[1], t[2])


def format_name_hms(nhms, lookup):
    name_txt = lookup[str(nhms[0])]
    time_txt = format_time(nhms[1])
    if len(nhms) == 4:
        name_txt += "\n" + lookup[str(nhms[2])]
        time_txt += "\n" + format_time(nhms[3])

    return name_txt, time_txt


def parse_date(date):
    """
    Parse a given date
    :param date: Datetime object
    :return:
    """
    try:
        dt = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
        date = Date(dt.year, dt.month, dt.day)
    except ValueError:
        # Probably the user entered negative year, strptime can't handle it.
        day, month, year = map(int, date.split('/'))
        date = Date(year, month, day)
    return date


def timestamp(t):
    return time.mktime(dateparser.parse(t).timetuple())


def compute_timezone_offset(date, tzone):
    """
    Computes timezone offset for a given date and timezone
    :param date: Datetime object
    :param timezone: timezone objecct
    :return: timezone offset
    """
    if isinstance(date, basestring):
        date = parse_date(date)
    dt = datetime(date.year, date.month, date.day)
    # offset from UTC (in hours). Needed especially for DST countries
    tz_offset = tzone.utcoffset(dt, is_dst=True).total_seconds() / 3600.
    return tz_offset



