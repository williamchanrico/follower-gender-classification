<h1 align="center">Follower Gender Classifier</h1>

<div align="center">
  :house_with_garden:
</div>
<div align="center">
  <strong>Know the gender of your followers!</strong>
</div>
<div align="center">
  A <code>project</code> to support my thesis.
</div>

<br />

<div align="center">
  <!-- Stability -->
  <a href="https://nodejs.org/api/documentation.html#documentation_stability_index">
    <img src="https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square"
      alt="API stability" />
  </a>
  <!-- GPL License -->
  <a href="http://flask.pocoo.org/"><img
	src="https://badges.frapsoft.com/os/gpl/gpl.png?v=103"
	border="0"
	alt="GPL Licence"
	title="GPL Licence">
  </a>
  <!-- Open Source Love -->
  <a href="http://flask.pocoo.org/"><img
	src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103"
	border="0"
	alt="Open Source Love"
	title="Open Source Love">
  </a>
</div>

<div align="center">
  <h3>
    <a href="https://classify.arzhon.id">
      Demo
    </a>
  </h3>
</div>

## Introduction

The goal is to determine how many of your Instagram follower(s) are male/female.

Consist of several parts:

- The frontend built with `socketio, flask, html & javascript`
- and 4 different implementation of classifier algorithm: xgboost, support vector machine, naive bayes, and adaboost

## Screenshot

![screenshot1](screenshots/screenshot.png?raw=true "Screenshot1")

## Getting Started

```sh
export IG_USERNAME=
export IG_PASSWORD=

# To limit the number of processed comments data:
#   follower_limit x media_per_follower x comments_per_media
#
# Defaults to 5000
export COMPUTE_THRESHOLD=
```

Assuming you have `virtualenv` and `python3-pip` installed:

- `virtualenv venv && source venv/bin/activate`
- `pip3 install -r requirements.txt`
- Get into python3 interactive mode and run:
```
Python 3.5.2 (default, Nov 12 2018, 13:43:14)
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import nltk
>>> nltk.download('punkt')
[nltk_data] Downloading package punkt to /home/william/nltk_data...
[nltk_data]   Unzipping tokenizers/punkt.zip.
True
```
- `cd app && python3 app.py`

```
$ python3 app.py -h
usage: app.py [-h] [-p PORT] [-o HOST] [-d] [-e ENV] [-s SECRET]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  specifies the port to listen on
  -o HOST, --host HOST  specifies the interface address to listen on
  -d, --debug           specifies the debug mode
  -e ENV, --env ENV     specifies the env for flask to run
  -s SECRET, --secret SECRET
                        specifies the session secret key
```

## Python Version

```
$ python --version
Python 3.7.1
```

## Contributing

Pull requests for new features, bug fixes, and suggestions are welcome!

## License

[GNU General Public License v3.0](https://github.com/williamchanrico/follower-gender-classification/blob/master/LICENSE.md)
