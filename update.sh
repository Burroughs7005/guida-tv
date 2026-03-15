#!/bin/bash
cd /home/pi/guida-tv
/usr/bin/python3 guida_personale.py
git add index.xml
git commit -m "Update $(date +'%d/%m/%Y %H:%M')"
git push origin main
