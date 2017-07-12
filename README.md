Panchagna CLI
=============

Command line version of [Drik Panchanga](https://github.com/webresh/drik-panchanga)

In addition to Computation of the five essentials of the Panchagna viz

* Tithi
* Nakshatra
* Yoga
* Karana
* Vaara

The application also provides details of the moon phase and current weather. The default location is "Bengaluru"

Requirements
------------
Install requirements.
```
     pip install -r requirements
     pip install https://github.com/dhoomakethu/pyphoon/tarball/master#egg=pyphoon-1.0

```

Using the Application
---------------------
```
usage: panchanga_cli [-h] [--data-dir str)] [-d (str)] [-p (str] [--lat LAT]
                     [--long LONG] [--timezone TIMEZONE] [--no-weather]
                     [--no-moon] [--offline] [--version]

    Command line Panchanga aka Hindu calendar

optional arguments:
  -h, --help            show this help message and exit
  --data-dir (str)      Data directory with cities.json and sktnames.json file
  -d (str), --date (str)
                        date in DD/MM/YYYY format (default today)
  -p (str), --place (str)
                        Place (default Bangalore)
  --lat LAT             Latitude in degree
  --long LONG           Longitude in degree
  --timezone TIMEZONE   timezone
  --no-weather          Do not display weather info
  --no-moon             Do not display moon info
  --offline             Resolve place name offline
  --version             show program's version number and exit
```


```
$ panchanga

┌──────────────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┐
│ Place: bengaluru                     │ Bengaluru, India                     │      ..--.                           │
│ Latitude: 12.9791198                 │                                      │    .` oo  .    Moon Rise:: 21:18:12  │
│ Longitude: 77.5912997                │     \  /       Partly cloudy         │   .o~.    O                          │
│ Timezone: Asia/Calcutta              │   _ /"".-.     26-27 °C              │   .c`_..() |    Moon Set:: 08:26:55  │
│ Time: 12/07/2017 13:21:22            │     \_(   ).   → 24 km/h             │    `..o....                          │
│                                      │     /(___(__)  10 km                 │      `'--'                           │
│ Sunrise: 06:01:11                    │                0.0 mm                │                                      │
│ Sunset: 18:49:16                     │                                      │                                      │
│ Day duration: 12:48:05               │                                      │                                      │
├──────────────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┤
│                                                                                                                    │
│                                                Śālivāhana śaka 1939                                                │
│                                                Hevilambī samvatsara                                                │
│                                                     Uttarāyaṇa                                                     │
│                                                Surya Rāśi: Mithuna                                                 │
│                                                     Grīṣma ṛtu                                                     │
│                                                    Āṣāḍha māsa                                                     │
│                                             tithi: Kṛṣṇa pakṣa tṛtīyā                                              │
│                                                tithi time: 14:04:07                                                │
│                                                  vara: Budhavāra                                                   │
│                                                nakshatra: Dhaniṣṭhā                                                │
│                                              nakshatra time: 22:49:18                                              │
│                                                    yoga: Prīti                                                     │
│                                                yoga time: 11:22:09                                                 │
│                                                   karana: Viṣṭi                                                    │
│                                                         --                                                         │
│                                                   GataKali: 5118                                                   │
│                                                  KaliDay: 1869481                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

License
-------

GNU Affero GPL version 3 (or later).


Credits
-------
panchanga cli depends on
* [wttr.in](https://github.com/chubin/wttr.in) for Weather
* [PyPhoon](https://github.com/chubin/pyphoon) for ASCII Moon
* [Geocoder](https://github.com/DenisCarriere/geocoder) for resolving locations.
