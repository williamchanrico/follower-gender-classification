# follower-gender-classifier

Know the gender of your Instagram followers!

Consist of 4 parts:

- The frontend app built with `socketio, flask, html & javascript`
- and 3 different implementation of classifier algorithm: support vector machine, naive bayes, and adaboost

## Getting Started

```
export IG_USERNAME=
export IG_PASSWORD=
```

Assuming you have `virtualenv` installed:

- `virtualenv venv && source venv/bin/activate`
- `pip install -r requirements.txt`
- `cd app && ./app.py`

```
$ ./app.py -h
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

## Under construction!