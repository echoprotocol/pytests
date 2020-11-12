FROM jfloff/alpine-python:3.7-slim

WORKDIR /home/

RUN apt-get update && apt-get install -y git make gcc g++ libffi-dev libssl-dev python-dev python3-dev python3-pip

RUN git clone https://github.com/vishnubob/wait-for-it.git
ADD ./requirements.txt /home/
RUN pip3 install -r requirements.txt

ADD ./common /home/common
ADD ./fixtures /home/fixtures
ADD ./pre_run_scripts /home/pre_run_scripts
ADD ./resources /home/resources
ADD ./suites /home/suites

ADD ./.env /home/
ADD ./__init__.py /home/
ADD ./docker-compose.yml /home/docker-compose.yml
ADD ./genesis.json /home/
ADD ./genesis_update_global_parameters.json /home/
ADD ./project.py /home/
ADD ./setup.cfg /home/
ADD ./test_runner.py /home/
