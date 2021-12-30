<h1 align="center">Follower Gender Classifier</h1>

<div align="center">
  :house_with_garden:
</div>
<div align="center">
  <strong>Know the gender of your followers!</strong>
</div>
<div align="center">
	A quick <code>hack</code> to support my short text classification <a href="https://www.sciencedirect.com/science/article/pii/S1877050919310609?via%3Dihub">thesis</a>. This code is NOT polished nor maintained!
</div>

<br />

<div align="center">
  <!-- Stability -->
  <a href="https://github.com/williamchanrico/follower-gender-classification"> <img
	src="https://img.shields.io/badge/stability-experimental-orange.svg?style=flat-square&label=Stability&color=red"
	alt="API stability" />
  </a>
  <!-- GPL License -->
  <a href="https://github.com/williamchanrico/follower-gender-classification/blob/master/LICENSE"><img
	src="https://img.shields.io/github/license/williamchanrico/follower-gender-classification?style=flat-square&label=License&color=yellow"
	border="0"
	alt="GPL Licence"
	title="GPL Licence">
  </a>
  <!-- Docker -->
  <a href="https://hub.docker.com/repository/docker/williamchanrico/follower-gender-classification"><img
	src="https://img.shields.io/docker/v/williamchanrico/follower-gender-classification?color=blue&label=Docker&style=flat-square"
	border="0"
	alt="Docker"
	title="Docker">
  </a>
</div>

<div align="center">
  <h3>
    <a href="https://classify.arzhon.id">
      Demo (temporary)
    </a>
  </h3>
</div>

# Introduction

![screenshot1](screenshots/screenshot.jpg?raw=true "Screenshot1")

### Goal

The goal of this code demo is to **predict gender of social media users based on comments section on Instagram profile** by using AdaBoost, XGBoost, Support Vector Machine, and Naive Bayes Classifier combined with a grid search and K- Fold validation.

How many are males vs females?

We collect `comments` against followers' Instagram picture media `posts` and format them as bag-of-words along with other pre-processing.

### Data Labelling

To label the data that was used to train the model, we use [Azure FaceAPI](https://azure.microsoft.com/en-us/services/cognitive-services/face/#overview) to filter pictures where there's only one person and is able to detect their gender.

# Overview

The code demo consists of several parts:

- The **frontend** built with `socketio, flask, html & javascript`,
- and 4 different implementations of classifier algorithm: xgboost, support vector machine, naive bayes, and adaboost.

> [adab/](./adab/)

Implementing AdaBoost using `sklearn` library.

> [app.py](./app.py)

Main entrypoint for the Flask application (this project).

> [data/](./data/)

Data dump(s) or saved pickle files (cache, models, etc.).

> [screenshots/](./screenshots/)

Screenshots.

> [naive_bayes/](./naive_bayes/)

Implementing naive bayes algorithm using `nltk` library.

> [svm](./svm)

Implementing Support Vector Machine algorithm using `sklearn` library.

> [thirdparty/](./thirdparty/)

Third-party related library supporting this project.

> [xgb](./xgb)

Implementing eXtreme gradient boosting algorithm using `xgboost` library.

# Getting Started

The config is simply loaded by app.py via [decouple](https://github.com/henriquebastos/python-decouple#env-file) package, keeping things simple.

Run `cp .env.example .env` and fill the necessary variables.

## Docker

```
docker run --env-file=.env -p 9000:9000 williamchanrico/follower-gender-classification:v0.1.0
```

## Manual

Assuming you have `virtualenv` and `python3-pip` installed:

- `virtualenv venv && source venv/bin/activate`
- `pip3 install -r requirements.txt`
- `python -m nltk.downloader punkt`
- Optionally, you may need `libgomp1` depending on your operating system (required by xgboost)

```sh
python3 app.py
```

# Python Version

```
$ python --version
Python 3.7.1
```

# License

[GNU General Public License v3.0](https://github.com/williamchanrico/follower-gender-classification/blob/master/LICENSE)
