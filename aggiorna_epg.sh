#!/bin/bash
cd ~/guida-tv

echo "--- START: $(date) ---"

# 1. Prelievo dati da Pavia (raspy)
echo "Download da Pavia (raspy)..."
scp -P 551 pi@100.125.95.69:/home/pi/guida-tv/guida_tv.xml ~/guida-tv/guida_tv_raw.xml

# 2. Elaborazione (crea guida_tv.xml e index.xml)
python3 ~/guida-tv/guida_personale.py

# 3. Compressione XML per backup/decoder
echo "Compressione XMLTV..."
gzip -f ~/guida-tv/guida_tv.xml

# 4. Sincronizzazione GitHub
echo "Push su GitHub..."
git add index.xml guida_tv.xml.gz aggiorna_epg.sh guida_personale.py
git commit -m "Aggiornamento EPG e RSS $(date +'%d-%m-%Y %H:%M')"
git push origin main

echo "--- FINE: Tutto aggiornato ---"
