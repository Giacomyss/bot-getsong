#!/bin/bash

sudo apt install pip virtualenv
virtualenv getsong
cp main.py getsong
cp config.cfg getsong
pushd getsong
source ./bin/activate
pip install -U requests
pip install -U youtube-dl
