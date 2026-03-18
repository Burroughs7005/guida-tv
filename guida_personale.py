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
        ET.SubElement(channel_rss, "description").text = "Cronologia TV Ordinata"

        programmi = []
        for prog in root.findall('programme'):
            start = prog.get('start', '')[:14]
            if not start: continue
            data_p = datetime.strptime(start, "%Y%m%d%H%M%S")
            if data_p < inizio_oggi: continue

            titolo = prog.find('title').text if prog.find('title') is not None else ""
            desc = prog.find('desc').text if prog.find('desc') is not None else ""
            
            if any(k.lower() in (titolo + " " + desc).lower() for k in KEYWORDS):
                programmi.append({
                    'data': data_p, 
                    'titolo': titolo, 
                    'desc': desc, 
                    'canale': canali_map.get(prog.get('channel'), 'TV')
                })

        # Ordine cronologico normale
        programmi.sort(key=lambda x: x['data'])

        # Filtro duplicati e scrittura Item
        visti = set()
        # Usiamo una pubDate decrescente: i programmi più lontani risulteranno "più vecchi"
        # Spingendo così i programmi di OGGI in cima alla lista di NetNewsWire
        data_pub_fittizia = adesso 

        for p in programmi:
            chiave = (p['data'], p['titolo'])
            if chiave in visti: continue
            visti.add(chiave)

            # Formattazione data nel titolo per chiarezza
            prefisso_data = p['data'].strftime('%d/%m')
            if p['data'].date() == adesso.date():
                prefisso_data = "Oggi"
            elif p['data'].date() == (adesso + timedelta(days=1)).date():
                prefisso_data = "Domani"

            item = ET.SubElement(channel_rss, "item")
            # Titolo pulito: [Data] HH:MM [Canale] Titolo
            ET.SubElement(item, "title").text = f"[{prefisso_data}] {p['data'].strftime('%H:%M')} - {p['canale']} - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']
            
            # pubDate decrescente di 1 secondo per ogni programma successivo
            ET.SubElement(item, "pubDate").text = data_pub_fittizia.strftime("%a, %d %b %Y %H:%M:%S +0000")
            data_pub_fittizia -= timedelta(seconds=1)
            
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{p['data'].strftime('%Y%m%d%H%M')}-{p['titolo'][:15]}"

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
