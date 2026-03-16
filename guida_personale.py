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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Analisi e filtraggio programmi...")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Creazione struttura RSS
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Guida TV Personalizzata Burroughs7005"
        ET.SubElement(channel, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel, "description").text = f"Listato unico aggiornato il {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        trovati = 0
        for prog in root.findall('programme'):
            titolo_tag = prog.find('title')
            desc_tag = prog.find('desc')
            
            titolo = titolo_tag.text if titolo_tag is not None else ""
            descrizione = desc_tag.text if desc_tag is not None else ""
            
            # Filtro Keyword (Case Insensitive)
            testo_programma = (titolo + " " + descrizione).lower()
            if any(key.lower() in testo_programma for key in KEYWORDS):
                item = ET.SubElement(channel, "item")
                
                # Gestione orario
                orario_raw = prog.get('start', '')
                ora_prefisso = f"{orario_raw[8:10]}:{orario_raw[10:12]} - " if len(orario_raw) >= 12 else ""
                
                # Listato pulito: solo titolo (con ora) e descrizione. Niente <link>.
                ET.SubElement(item, "title").text = f"{ora_prefisso}{titolo}"
                ET.SubElement(item, "description").text = descrizione
                trovati += 1

        # Fallback se non ci sono match
        if trovati == 0:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = "Nessun programma trovato"
            ET.SubElement(item, "description").text = "Nessun match con le keyword attuali."

        # Scrittura file RSS
        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: {trovati} programmi filtrati.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: {e}")

def elabora():
    base_dir = "/home/pi/guida-tv"
    input_f = f"{base_dir}/guida_tv_raw.xml"
    output_f = f"{base_dir}/guida_tv.xml" # File per gzip
    rss_f = f"{base_dir}/index.xml"
    
    if os.path.exists(input_f):
        # Manteniamo una copia per il processo di compressione dello script .sh
        shutil.copy2(input_f, output_f)
        
        # Generiamo il feed filtrato
        genera_rss(input_f, rss_f)
        
        # Pulizia file raw
        os.remove(input_f)
    else:
        print("Errore: guida_tv_raw.xml non trovato.")

if __name__ == "__main__":
    elabora()
