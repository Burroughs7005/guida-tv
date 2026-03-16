#!/bin/bash
cd ~/guida-tv

echo "--- Inizio aggiornamento: $(date) ---"

# 1. Scarica da Pavia
scp -P 551 pi@100.125.95.69:/home/pi/guida-tv/guida_tv.xml ~/guida-tv/guida_tv_raw.xml

# 2. Elabora con Python (ora legge il file locale)
python3 ~/guida-tv/guida_personale.py

# 3. Comprime per GitHub (Riduce da 100MB a ~12MB)
gzip -c ~/guida-tv/guida_tv.xml > ~/guida-tv/guida_tv.xml.gz

# 4. Rimuove i file pesanti per non intasare Git
rm guida_tv_raw.xml guida_tv.xml

# 5. Push su GitHub
git add guida_tv.xml.gz aggiorna_epg.sh guida_personale.py
git commit -m "EPG Professionale Compressa $(date +'%d-%m-%Y %H:%M')"
git push origin main

echo "--- Fine processo ---"
