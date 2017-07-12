# -*- coding: utf-8 -*-
from argparse import ArgumentParser, RawTextHelpFormatter
import requests
from panchanga.lib.panchanga import *
from panchanga.lib.common import TODAY, format_time, DATA_DIR
from panchanga.lib.common import PlaceNotFound, DB
from panchanga.lib.common import format_name_hms
from panchanga.lib.common import timestamp
from panchanga.cli import __version__

NO_MOON = False
try:
    from pyphoon.main import putmoon
except ImportError:
    print "Install pyphoon 'pip install https://github.com/dhoomakethu/pyphoon/tarball/master#egg=pyphoon-1.0' for moon information"
    NO_MOON = True

cities = sktnames = None
CEND = u'\33[0m'
CGREEN = u'\33[32m'

# Command line utils

description = """
    Command line Panchanga aka Hindu calendar
"""


def dabbafy(content, width=None, height=None, strip=True):
    """
    add a dabba around the given content
    :param content: list of strings
    :return:
    """
    new_content = []
    for line in content:
        if strip:
            line = line.strip()
        line = line.replace("\t", "    ")
        lines = line.split("\n")
        for l in lines:
            new_content.append(l)

    if not width:
        width = len(max(new_content, key=len))
    dabbafied = [u"┌"+ u"─" * (width+1) + u"┐",
                 u"└" + u"─" * (width + 1) + u"┘"]
    for i, line in enumerate(new_content, start=1):
        # line = line.replace("\t", "    ")
        # lines = line.split("\n")
        # for  line in lines:
        line = u'│ {: <{}}'.format(line, width) + u"│"

        dabbafied.insert(i, line)

    if height and len(dabbafied) < height:
        for i in range(len(dabbafied)-1, height-1):
            empty = u'│ {: <{}}'.format(u"", width) + u"│"
            dabbafied.insert(i, empty)

    return dabbafied


def combine_dabbas(dabba_list):
    """
    Combines multiple dabbas
    :param dabbas: struct {level: content}
    :return:
    """
    combined_dabbas = []
    line_no = 0
    for level, dabbas in dabba_list.iteritems():
        height = len(dabbas[0])
        dabba_count = len(dabbas)
        if dabba_count == 1 and level == 0:
            combined_dabbas.extend(dabbas[0])
        elif dabba_count == 2:
            for dabba1, dabba2 in zip(*dabbas):
                if line_no == 0:
                    combined_dabbas.append(dabba1[:-1]+u'┬' + dabba2[1:])
                elif line_no == height-1:
                    combined_dabbas.append(dabba1[:-1] + u'┴' + dabba2[1:])
                else:
                    combined_dabbas.append(dabba1[:-1]  + dabba2)
                line_no += 1
        elif dabba_count == 3:
            for dabba1, dabba2, dabba3 in zip(*dabbas):
                if line_no == 0:
                    combined_dabbas.append(dabba1[:-1]+u'┬' + dabba2[1:-1]+u'┬' + dabba3[1:])
                elif line_no == height-1:
                    combined_dabbas.append(dabba1[:-1] + u'┴' + dabba2[1:-1] + u'┴' + dabba3[1:])
                else:
                    combined_dabbas.append(dabba1[:-1]  + dabba2[:-1] + dabba3)
                line_no += 1
        else:
            last_line = combined_dabbas[-1]
            last_line = u"├" + last_line[1:-1] + u"┤"
            combined_dabbas[-1] = last_line
            line_width = len(combined_dabbas[-1])
            for no, line in enumerate(dabbas[0][1:]):
                first = last = u"│"
                line = line[1:-1]
                line = line.strip()
                if no == len(dabbas[0]) -2:
                    first = u'└'
                    last = u"┘"
                    line = first + line.center(line_width - 2, u"─") + last
                else:
                    centered = u"{}{}{}".format(CGREEN, line.center(line_width - 2), CEND)
                    line = first + centered + last

                combined_dabbas.append(line)
    return combined_dabbas


def calculate_panchanga(date, place, sktnames):
    jd = gregorian_to_jd(date)
    tithis = sktnames.tithis
    nakshatras = sktnames.nakshatras
    vaaras = sktnames.vaaras
    yogas = sktnames.yogas
    karanas = sktnames.karanas
    masas = sktnames.masas
    samvats = sktnames.samvats
    ritus = sktnames.ritus
    raashis = sktnames.rashis
    aayanas = sktnames.ayanas

    ti = tithi(jd, place)
    nak = nakshatra(jd, place)
    yog = yoga(jd, place)
    mas = masa(jd, place)
    rtu = ritu(mas[0])
    rasi = raasi(jd)
    ayana = aayana(jd)
    kar = karana(jd, place)
    vara = vaara(jd)
    srise = sunrise(jd, place)[1]
    sset = sunset(jd, place)[1]
    mrise = moonrise(jd, place)
    mset = moonset(jd, place)
    kday = ahargana(jd)
    kyear, sakayr = elapsed_year(jd, mas[0])
    samvat = samvatsara(jd, mas[0])
    day_dur = day_duration(jd, place)[1]
    panchanga = []
    # Update GUI one by one. First the easy ones

    panchanga.append("")
    panchanga.append(u"Śālivāhana śaka %d" % (sakayr))
    panchanga.append(u"%s samvatsara" % (samvats[str(samvat)]))
    panchanga.append(u"%s " % (aayanas[str(ayana)]))
    panchanga.append(u"Surya Rāśi: %s" % (raashis[str(int(rasi))]))
    panchanga.append(u"%s ṛtu" % (ritus[str(rtu)]))
    name, hms = format_name_hms(ti, tithis)
    month_name = masas[str(mas[0])]
    is_leap = mas[1]
    if is_leap:
        month_name = "Adhika " + month_name.lower()
    panchanga.append(month_name + u" māsa")
    panchanga.append(u"tithi: {}".format(name))
    panchanga.append(u"tithi time: {}".format(hms))

    name, hms = format_name_hms(nak, nakshatras)
    panchanga.append(u"vara: %s" % vaaras[str(vara)])
    panchanga.append(u"nakshatra: {}".format(name))
    panchanga.append(u"nakshatra time: {}".format(hms))
    name, hms = format_name_hms(yog, yogas)
    panchanga.append(u"yoga: {}".format(name))
    panchanga.append(u"yoga time: {}".format(hms))
    panchanga.append(u"karana: %s" % karanas[str(kar[0])])
    panchanga.append(u" -- ")

    panchanga.append(u"GataKali: %d" % (kyear))
    panchanga.append(u"KaliDay: %d" % (kday))

    # Next update the complex ones

    return panchanga, mrise, mset, srise, sset, day_dur


def colorify(content):
    content[:] = [u"{0}{1:30s}{2}".format(CGREEN,c,CEND) for c in content]
    return content


def parse_moon(moon, mrise, mset):
    moon = moon.split("\n")
    moon_iter = iter((["Moon Rise:", mrise], ["Moon Set:", mset]))
    moon_stages = ["Full Moon", "Last Quarter", "First Quarter", "New Moon"]
    for i, l in enumerate(moon[:]):
        l = l.split("\t")
        if len(l) > 1:
            if not l[1].isspace():
                if any(moon_stage in l[1] for moon_stage in moon_stages):
                    m = next(moon_iter, "")
                    l[1] = "{}: {}".format(m[0], format_time(m[1]))
                else:
                    l[1] = ""
                moon[i] = "\t".join(l)

    moon[:] = [u" {}".format(minfo) for minfo in moon]
    # moon[:] = [u"{}".format(unicode(minfo, 'utf-8')) for minfo in moon]
    return moon


def run_cli():
    DEFAULTS = DB.load_config()
    args = []
    cli_parser = ArgumentParser(prog="panchanga_cli",
                                description=description,
                                formatter_class=RawTextHelpFormatter)

    cli_parser.add_argument(
        "--data-dir",
        metavar="(str)",
        help="Data directory with cities.json and sktnames.json file",
        default=DATA_DIR
    )
    cli_parser.add_argument(
        "-d",
        "--date",
        metavar="(str)",
        help="date in DD/MM/YYYY format (default today)",
        default=TODAY
    )

    cli_parser.add_argument(
        "-p",
        "--place",
        metavar="(str)",
        help="Place (default Bangalore) or comma separate co-ordinates(12.5, 78.6)",
        default=DEFAULTS.get("place")
    )
    cli_parser.add_argument(
        "--no-weather",
        help="Do not display weather info ",
        action="store_true"
    )
    cli_parser.add_argument(
        "--no-moon",
        help="Do not display moon info ",
        action="store_true"
    )
    cli_parser.add_argument(
        "--offline",
        help="Resolve place name offline",
        action="store_true"
    )

    cli_parser.add_argument('--version',
                            action='version',
                            version='%(prog)s {version}'.format(
                                version=__version__))

    use_coordinates = False
    moon = [""]
    weather = [""]
    args, unknown = cli_parser.parse_known_args()
    data_dir = args.data_dir
    date = args.date
    place = args.place
    no_weather = args.no_weather
    no_moon = args.no_moon
    offline = args.offline
    load_cities = False
    if place != DEFAULTS.get("place", "Bengaluru"):
        load_cities = True
    db = DB(data_dir, offline=offline, load_cities=load_cities)

    if not no_weather:
        r = requests.get("http://wttr.in/{}?0&q&T".format(place))
        if r.status_code == 200:
            weather = r.content.decode("utf-8")
            weather = weather.split("\n")
            weather[:] = [u"{}".format(winfo) for winfo in weather]

    place_info, date_obj = db.resolve_location(place, date,
                                               offline=offline)
    if isinstance(place_info, PlaceNotFound):
        cli_parser.exit(place_info.msg)

    panchanga, mrise, mset, srise, sset, day_dur = calculate_panchanga(
        date_obj, place_info, db.sktnames)
    if not no_moon and not NO_MOON:
        moon = putmoon(timestamp(date), 6, "@", False)
        moon = parse_moon(moon, mrise, mset)
    location = ["Place: {}".format(place),
                "Latitude: {}".format(place_info.latitude),
                "Longitude: {}".format(place_info.longitude),
                "Timezone: {}".format(place_info.timezone_hr),
                "Time: {}".format(TODAY),
                "",
                "Sunrise: {}".format(format_time(srise)),
                "Sunset: {}".format(format_time(sset)),
                "Day duration: {}".format(format_time(day_dur)),
                ]
    width = max(len(max(weather, key=len)), len(max(moon, key=len)),
                len(max(location, key=len)))
    height = max(len(weather), len(moon), len(location))
    location = dabbafy(location, width=width + 5, height=height + 2)
    dabba1 = [location]
    if not no_weather:
        weather = dabbafy(weather, width=width + 5, height=height + 2,
                          strip=False)
        dabba1.append(weather)
    if not no_moon and not NO_MOON:
        moon = dabbafy(moon, height=height + 2, width=width + 5,
                       strip=False)
        dabba1.append(moon)

    p_info = dabbafy(panchanga, width=2 * width)

    dabbas = {0: dabba1, 1: [p_info]}
    combined_dabbas = combine_dabbas(dabbas)

    print u"\n".join(combined_dabbas)
    db.save_config(place, place_info)


if __name__ == "__main__":
    run_cli()
