import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

KEYWORDS = ["Annika", "Bastardi di Pizzofalcone", "Che tempo che fa", "L'ispettore Coliandro", "Il Commissario Montalbano", "Propaganda Live", "Quante storie", "Rocco Schiavone", "Shetland", "La Torre di Babele", "Kubrick", "Alberto Angela", "Mario Monicelli", "Ettore Scola", "Gassman", "Tino Buazzelli", "Eduardo De Filippo", "Nino Manfredi", "Ugo Tognazzi", "Vittorio De Sica", "Tigotà", "Volley Femminile", "Volley Maschile", "Superlega Credem"]

def genera_rss(xml_file, rss_file):
    adesso = datetime.now()
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        canali_map = {chan.get('id'): chan.find('display-name').text for chan in root.findall('channel') if chan.get('id') and chan.find('display-name') is not None}
        rss = ET.Element("rss", version="2.0")
        channel_rss = ET.SubElement(rss, "channel")
        ET.SubElement(channel_rss, "title").text = f"Agenda TV"

        programmi = []
        for prog in root.findall('programme'):
            start, stop = prog.get('start', '')[:14], prog.get('stop', '')[:14]
            if not start or not stop: continue
            d_start, d_stop = datetime.strptime(start, "%Y%m%d%H%M%S"), datetime.strptime(stop, "%Y%m%d%H%M%S")
            if d_start < adesso.replace(hour=0, minute=0, second=0): continue
            
            titolo = prog.find('title').text if prog.find('title') is not None else ""
            desc = prog.find('desc').text if prog.find('desc') is not None else ""
            
            if any(k.lower() in (titolo + " " + desc).lower() for k in KEYWORDS):
                durata = int((d_stop - d_start).total_seconds() / 60)
                programmi.append({'data': d_start, 'durata': durata, 'titolo': titolo, 'desc': desc, 'canale': canali_map.get(prog.get('channel'), 'TV')})

        programmi.sort(key=lambda x: x['data'])
        visti, data_pub = set(), adesso
        for p in programmi:
            if (p['data'], p['titolo']) in visti: continue
            visti.add((p['data'], p['titolo']))
            
            pref = "Oggi" if p['data'].date() == adesso.date() else ("Domani" if p['data'].date() == (adesso + timedelta(days=1)).date() else p['data'].strftime('%d/%m'))
            item = ET.SubElement(channel_rss, "item")
            # Inseriamo la durata nel titolo per il Mac
            ET.SubElement(item, "title").text = f"[{pref}] {p['data'].strftime('%H:%M')} ({p['durata']}m) - {p['canale']} - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']
            ET.SubElement(item, "pubDate").text = data_pub.strftime("%a, %d %b %Y %H:%M:%S +0000")
            data_pub -= timedelta(seconds=1)
            
        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding="utf-8"))
    except Exception as e: print(f"Errore: {e}")

def elabora():
    d = "/home/pi/guida-tv"
    if os.path.exists(f"{d}/guida_tv_raw.xml"):
        genera_rss(f"{d}/guida_tv_raw.xml", f"{d}/index.xml")
        os.remove(f"{d}/guida_tv_raw.xml")
if __name__ == "__main__": elabora()
