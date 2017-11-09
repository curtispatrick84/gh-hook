#!/bin/bash
cd /gh-listener

/etc/init.d/nginx start
python -u server.py
