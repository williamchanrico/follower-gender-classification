FROM python:3.7-slim-bullseye

WORKDIR /app

# libgom1 required by xgboost
RUN apt-get update && \
	apt-get -y --no-install-recommends install \
	libgomp1

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt \
	&& python -m nltk.downloader punkt

COPY . .

ENTRYPOINT [ "python3", "./app.py"]
CMD ["--help"]
