import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import shutil

KEYWORDS = [
    "Annika", "Bastardi di Pizzofalcone", "Che tempo che fa", "Coliandro",
    "Il Commissario Montalbano", "Propaganda Live", "Quante storie", 
    "Schiavone", "Shetland", "La Torre di Babele",
    "Kubrick", "Alberto Angela", "Mario Monicelli", "Ettore Scola",
    "Gassman", "Tino Buazzelli", "Eduardo De Filippo", "Nino Manfredi",
    "Ugo Tognazzi", "Vittorio De Sica",
    "Pallavolo", "Superlega", "Tigotà", "Volley Femminile", "Volley Maschile", "Credem Banca"
]

def genera_rss(xml_file, rss_file):
    adesso = datetime.now()
    inizio_oggi = adesso.replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        canali_map = {chan.get('id'): chan.find('display-name').text 
                      for chan in root.findall('channel') 
                      if chan.get('id') and chan.find('display-name') is not None}

        rss = ET.Element("rss", version="2.0")
        channel_rss = ET.SubElement(rss, "channel")
        ET.SubElement(channel_rss, "title").text = f"Agenda TV [{adesso.strftime('%H:%M')}]"
        ET.SubElement(channel_rss, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel_rss, "description").text = "Guida TV Filtrata"

        programmi = []
        for prog in root.findall('programme'):
            start = prog.get('start', '')[:14]
            if not start: continue
            data_p = datetime.strptime(start, "%Y%m%d%H%M%S")
            if data_p < inizio_oggi: continue

            titolo = prog.find('title').text if prog.find('title') is not None else ""
            desc = prog.find('desc').text if prog.find('desc') is not None else ""
            
            if any(k.lower() in (titolo + " " + desc).lower() for k in KEYWORDS):
                programmi.append({'data': data_p, 'titolo': titolo, 'desc': desc, 'canale': canali_map.get(prog.get('channel'), 'TV')})

        # 1. Ordiniamo cronologicamente (dal più vicino al più lontano)
        programmi.sort(key=lambda x: x['data'])

        # 2. Rimuoviamo i duplicati (stesso titolo e orario)
        visti = set()
        programmi_unici = []
        for p in programmi:
            chiave = (p['data'], p['titolo'])
            if chiave not in visti:
                visti.add(chiave)
                programmi_unici.append(p)

        # 3. Creiamo il feed con pubDate "a scalare"
        # Più il programma è lontano, più la pubDate è vecchia.
        # Questo forza il lettore RSS a mettere OGGI in cima.
        data_fittizia = adesso
        ultimo_giorno = None
        giorni = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ", "SABATO", "DOMENICA"]

        for p in programmi_unici:
            giorno_corrente = p['data'].strftime('%Y%m%d')
            
            # Separatore Giorno
            if giorno_corrente != ultimo_giorno:
                sep = ET.SubElement(channel_rss, "item")
                ET.SubElement(sep, "title").text = f"--- {giorni[p['data'].weekday()]} {p['data'].strftime('%d %b')} ---"
                ET.SubElement(sep, "pubDate").text = data_fittizia.strftime("%a, %d %b %Y %H:%M:%S +0000")
                data_fittizia -= timedelta(seconds=1) # Scaliamo di un secondo
                ultimo_giorno = giorno_corrente

            item = ET.SubElement(channel_rss, "item")
            ET.SubElement(item, "title").text = f"{p['data'].strftime('%H:%M')} [{p['canale']}] - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']
            ET.SubElement(item, "pubDate").text = data_fittizia.strftime("%a, %d %b %Y %H:%M:%S +0000")
            data_fittizia -= timedelta(seconds=1)
            
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{p['data'].strftime('%Y%m%d%H%M')}-{p['titolo'][:10]}"

        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding="utf-8"))
            
    except Exception as e:
        print(f"Errore: {e}")

def elabora():
    d = "/home/pi/guida-tv"
    if os.path.exists(f"{d}/guida_tv_raw.xml"):
        genera_rss(f"{d}/guida_tv_raw.xml", f"{d}/index.xml")
        os.remove(f"{d}/guida_tv_raw.xml")

if __name__ == "__main__":
    elabora()
