import os
import xml.etree.ElementTree as ET
from datetime import datetime
import shutil

# --- CONFIGURAZIONE KEYWORD ---
KEYWORDS = [
    "Annika", "Bastardi di Pizzofalcone", "Che tempo che fa", "L'ispettore Coliandro",
    "Il Commissario Montalbano", "Propaganda Live", "Quante storie", 
    "Rocco Schiavone", "Shetland", "La Torre di Babele",
    "Kubrick", "Alberto Angela", "Mario Monicelli", "Ettore Scola",
    "Gassman", "Tino Buazzelli", "Eduardo De Filippo", "Nino Manfredi",
    "Ugo Tognazzi", "Vittorio De Sica",
    "Pallavolo", "Tigotà", "Volley Femminile", "Volley Maschile", "Superlega Credem"
]

def genera_rss(xml_file, rss_file):
    adesso = datetime.now()
    print(f"[{adesso.strftime('%H:%M:%S')}] Generazione agenda raggruppata...")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Agenda TV Burroughs7005"
        ET.SubElement(channel, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel, "description").text = f"Filtro keyword attivo - Aggiornato il {adesso.strftime('%d/%m/%Y %H:%M')}"

        # Estraiamo e filtriamo i programmi validi
        programmi_validi = []
        for prog in root.findall('programme'):
            orario_raw = prog.get('start', '')
            if len(orario_raw) < 14: continue
            
            data_prog = datetime.strptime(orario_raw[:14], "%Y%m%d%H%M%S")
            if data_prog < adesso: continue

            titolo = prog.find('title').text if prog.find('title') is not None else ""
            descrizione = prog.find('desc').text if prog.find('desc') is not None else ""
            
            testo_programma = (titolo + " " + descrizione).lower()
            if any(key.lower() in testo_programma for key in KEYWORDS):
                programmi_validi.append({
                    'data': data_prog,
                    'titolo': titolo,
                    'desc': descrizione
                })

        # Ordiniamo per data
        programmi_validi.sort(key=lambda x: x['data'])

        ultimo_giorno = None
        giorni_settimana = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ", "SABATO", "DOMENICA"]
        
        for p in programmi_validi:
            giorno_corrente = p['data'].strftime('%Y%m%d')
            
            # Se cambiamo giorno, aggiungiamo un separatore
            if giorno_corrente != ultimo_giorno:
                sep = ET.SubElement(channel, "item")
                nome_giorno = giorni_settimana[p['data'].weekday()]
                data_formattata = p['data'].strftime('%d %b')
                ET.SubElement(sep, "title").text = f"--- {nome_giorno} {data_formattata} ---"
                ET.SubElement(sep, "description").text = "Inizio programmi del giorno"
                ultimo_giorno = giorno_corrente

            # Aggiungiamo il programma
            item = ET.SubElement(channel, "item")
            ora_str = p['data'].strftime('%H:%M')
            ET.SubElement(item, "title").text = f"{ora_str} - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']

        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: Agenda creata con {len(programmi_validi)} eventi.")

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
