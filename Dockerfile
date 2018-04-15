# This works for DEV only!
FROM python:3.6
MAINTAINER Bryce McDonnell <bryce@bridgetownint.com>

ENV FLASK_APP tally_http.py
ENV FLASK_DEBUG 1

RUN mkdir /app
WORKDIR /app

# this is for prod?
ADD requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0"]
