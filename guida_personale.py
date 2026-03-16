import os
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil

def genera_rss(xml_file, rss_file):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Analisi XML e generazione RSS professionale...")
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Guida TV Professionale Burroughs7005"
        ET.SubElement(channel, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel, "description").text = f"Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        programmi = root.findall('programme')
        
        if not programmi:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = "Nessun programma trovato"
            ET.SubElement(item, "description").text = "Verificare il grabber su Pavia."
        else:
            # Prendiamo i primi 100 programmi per mantenere il feed leggero
            for prog in programmi[:100]:
                item = ET.SubElement(channel, "item")
                
                titolo_tag = prog.find('title')
                desc_tag = prog.find('desc')
                
                titolo = titolo_tag.text if titolo_tag is not None else "Senza Titolo"
                descrizione = desc_tag.text if desc_tag is not None else "Nessuna descrizione"
                orario_raw = prog.get('start', '')
                
                # Formattazione orario: da 20260316203000 a 20:30
                if len(orario_raw) >= 12:
                    ora = orario_raw[8:10]
                    minuti = orario_raw[10:12]
                    titolo_finale = f"{ora}:{minuti} - {titolo}"
                else:
                    titolo_finale = titolo
                
                ET.SubElement(item, "title").text = titolo_finale
                ET.SubElement(item, "description").text = descrizione

        # Scrittura con dichiarazione XML corretta
        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: {len(programmi)} programmi processati.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: {e}")

def elabora():
    base_dir = "/home/pi/guida-tv"
    input_f = f"{base_dir}/guida_tv_raw.xml"
    output_f = f"{base_dir}/guida_tv.xml"
    rss_f = f"{base_dir}/index.xml"
    
    if os.path.exists(input_f):
        # 1. Sposta il file raw per la compressione successiva
        if os.path.exists(output_f): os.remove(output_f)
        shutil.copy2(input_f, output_f)
        
        # 2. Genera l'RSS (index.xml)
        genera_rss(output_f, rss_f)
        
        # 3. Pulisce il file raw temporaneo
        os.remove(input_f)
    else:
        print("Errore: File guida_tv_raw.xml non trovato. Controlla il download da Pavia.")

if __name__ == "__main__":
    elabora()
