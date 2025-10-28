#!/bin/bash
mkdir -p /home/site/wwwroot/.pip
cp /home/site/wwwroot/pip.conf /home/site/wwwroot/.pip/pip.conf
export PIP_CONFIG_FILE=/home/site/wwwroot/.pip/pip.conf
pip install --upgrade pip
pip install streamlit
pip install vaultspeed-sdk
pip install -r /home/site/wwwroot/requirements.txt
streamlit run /home/site/wwwroot/pages/main.py --server.port=8000 --server.address=0.0.0.0
