# follower-gender-classifier

Know the gender of your Instagram followers!

Consist of 4 parts:

- The frontend app built with `socketio, flask, html & javascript`
- and 3 different implementation of classifier algorithm: support vector machine, naive bayes, and adaboost

## Screenshot

![screenshot1](screenshots/screenshot01.png?raw=true "Screenshot1")

![screenshot2](screenshots/screenshot02.png?raw=true "Screenshot2")

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
