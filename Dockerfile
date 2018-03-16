FROM python:3.6
MAINTAINER Bryce McDonnell <bryce@bridgetownint.com>

RUN mkdir /app

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000

CMD ["python", "tallies.py"]
