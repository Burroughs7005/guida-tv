import os
import xml.etree.ElementTree as ET
from datetime import datetime

def genera_rss(xml_file, rss_file):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generazione feed RSS (index.xml)...")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Guida TV Professionale"
        ET.SubElement(channel, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel, "description").text = "EPG aggiornata via Schedules Direct"

        # Esportiamo i programmi per l'RSS
        for programme in root.findall('programme')[:100]:
            item = ET.SubElement(channel, "item")
            title_node = programme.find('title')
            desc_node = programme.find('desc')
            
            title = title_node.text if title_node is not None else "Programma"
            desc = desc_node.text if desc_node is not None else "Nessuna descrizione disponibile"
            start = programme.get('start')
            
            ET.SubElement(item, "title").text = f"{title} [{start}]"
            ET.SubElement(item, "description").text = desc

        with open(rss_file, "wb") as f:
            f.write(ET.tostring(rss, encoding="utf-8"))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: index.xml creato.")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Errore: {e}")

def elabora():
    input_f = "/home/pi/guida-tv/guida_tv_raw.xml"
    output_f = "/home/pi/guida-tv/guida_tv.xml"
    rss_f = "/home/pi/guida-tv/index.xml"
    
    if os.path.exists(input_f):
        if os.path.exists(output_f): os.remove(output_f)
        os.rename(input_f, output_f)
        genera_rss(output_f, rss_f)
    else:
        print(f"ERRORE: Non trovo {input_f}")

if __name__ == "__main__":
    elabora()
