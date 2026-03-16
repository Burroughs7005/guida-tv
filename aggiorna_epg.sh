#!/bin/bash

# Vai nella cartella corretta
cd ~/guida-tv

echo "--- START: $(date) ---"

# 1. Scarica da Pavia (Pavia -> Glasgow)
# Usa la porta 551 che abbiamo verificato prima
echo "Prelievo dati da Pavia..."
scp -P 551 pi@100.125.95.69:/home/pi/guida-tv/guida_tv.xml ~/guida-tv/guida_tv_raw.xml

# 2. Esegui lo script Python (Sposta il file)
python3 ~/guida-tv/guida_personale.py

# 3. Comprime il file per GitHub (GZIP)
# Questo riduce le dimensioni drasticamente
echo "Compressione in corso..."
gzip -f ~/guida-tv/guida_tv.xml

# 4. Spedisci su GitHub
echo "Invio a GitHub..."
git add guida_tv.xml.gz aggiorna_epg.sh guida_personale.py
git commit -m "EPG Professional Update $(date +'%d-%m-%Y %H:%M')"
git push origin main

echo "--- FINE: Operazione completata ---"
