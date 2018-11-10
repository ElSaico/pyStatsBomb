pyStatsBomb
===========


[![](https://img.shields.io/pypi/v/pystatsbomb.svg)](https://pypi.python.org/pypi/pystatsbomb)
[![](https://img.shields.io/travis/ElSaico/pyStatsBomb.svg)](https://travis-ci.org/ElSaico/pyStatsBomb)
[![Documentation Status](https://readthedocs.org/projects/pystatsbomb/badge/?version=latest)](https://pystatsbomb.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/ElSaico/pyStatsBomb/shield.svg)](https://pyup.io/repos/github/ElSaico/pyStatsBomb/)


Python port of the [StatsBombR](https://github.com/StatsBomb/StatsBombR) library.


* Free software: Mozilla Public License 2.0
* Documentation: https://pystatsbomb.readthedocs.io


Features
--------

* Free data access
* API data access (TODO)
* Data cleaning helpers

### StatsBombR compatibility

* `FreeCompetitions`: `pystatsbomb.free.get_competitions()`
* `FreeMatches`: `pystatsbomb.free.get_matches(competition_ids)`
* `MultiCompEvents`: TODO
* `StagingMultiCompEvents`: TODO
* `StatsBombFreeEvents`: `pystatsbomb.free.get_events(matches=None)`
* `StatsBombFreeLineups`: `pystatsbomb.free.get_lineups(matches=None)`
* `allclean`: `pystatsbomb.helpers.all_clean(df)`
* `alllineups`: TODO
* `allmatches`: TODO
* `allstaging`: TODO
* `annotate_pitchSB`: TODO
* `cleanlocations`: `pystatsbomb.helpers.clean_locations(df)`
* `competitions`: TODO
* `defensiveinfo`: TODO
* `formatelapsedtime`: `pystatsbomb.helpers.format_elapsed_time(df)`
* `freezeframeinfo`: `pystatsbomb.helpers.freeze_frame_info(df)`
* `get.gamestate`: TODO
* `get.lineups`: TODO
* `get.lineupsFree`: `pystatsbomb.free.get_match_lineups(match)`
* `get.matchFree`: `pystatsbomb.free.get_match_events(match)`
* `get.matches`: TODO
* `getOpposingTeam`: TODO
* `getmatch`: TODO
* `getminutesplayed`: TODO
* `goalkeeperinfo`: `pystatsbomb.helpers.goalkeeper_info(df)`
* `matchesvector`: TODO
* `possessioninfo`: `pystatsbomb.helpers.possession_info(df)`
* `shotinfo`: `pystatsbomb.helpers.shot_info(df)`
* `stagingcomps`: TODO
* `stagingevents`: TODO
* `stagingmatches`: TODO

Credits
-------

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
