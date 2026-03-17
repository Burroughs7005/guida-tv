import os
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil

# --- CONFIGURAZIONE KEYWORD ---
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
    print(f"[{adesso.strftime('%H:%M:%S')}] Filtraggio programmi futuri...")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Guida TV Personalizzata Burroughs7005"
        ET.SubElement(channel, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel, "description").text = f"Solo programmi futuri - Aggiornato il {adesso.strftime('%d/%m/%Y %H:%M')}"

        trovati = 0
        for prog in root.findall('programme'):
            orario_raw = prog.get('start', '') # Formato: 20260317063000 +0000
            
            if len(orario_raw) < 14: continue
            
            # Convertiamo l'orario del programma in un oggetto datetime per il confronto
            # Usiamo solo i primi 14 caratteri (YYYYMMDDHHMMSS)
            data_prog = datetime.strptime(orario_raw[:14], "%Y%m%d%H%M%S")
            
            # --- FILTRO TEMPORALE: Salta se il programma è già iniziato ---
            if data_prog < adesso:
                continue

            titolo_tag = prog.find('title')
            desc_tag = prog.find('desc')
            titolo = titolo_tag.text if titolo_tag is not None else ""
            descrizione = desc_tag.text if desc_tag is not None else ""
            
            testo_programma = (titolo + " " + descrizione).lower()
            if any(key.lower() in testo_programma for key in KEYWORDS):
                item = ET.SubElement(channel, "item")
                
                # Formattazione titolo con Giorno e Ora (es: Mar 17 - 20:15)
                giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
                giorno_str = giorni_settimana[data_prog.weekday()]
                ora_prefisso = f"{giorno_str} {data_prog.strftime('%d')} - {data_prog.strftime('%H:%M')} "
                
                ET.SubElement(item, "title").text = f"{ora_prefisso}- {titolo}"
                ET.SubElement(item, "description").text = descrizione
                trovati += 1

        if trovati == 0:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = "Nessun programma futuro trovato"
            ET.SubElement(item, "description").text = "Controlla di nuovo più tardi o espandi le keyword."

        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: {trovati} programmi futuri trovati.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: {e}")

def elabora():
    base_dir = "/home/pi/guida-tv"
    input_f = f"{base_dir}/guida_tv_raw.xml"
    output_f = f"{base_dir}/guida_tv.xml"
    rss_f = f"{base_dir}/index.xml"
    
    if os.path.exists(input_f):
        shutil.copy2(input_f, output_f)
        genera_rss(input_f, rss_f)
        os.remove(input_f)
    else:
        print("Errore: guida_tv_raw.xml non trovato.")

if __name__ == "__main__":
    elabora()
