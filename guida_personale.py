import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
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
    inizio_oggi = adesso.replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        canali_map = {}
        for chan in root.findall('channel'):
            chan_id = chan.get('id')
            display_name = chan.find('display-name')
            if chan_id and display_name is not None:
                canali_map[chan_id] = display_name.text

        rss = ET.Element("rss", version="2.0")
        channel_rss = ET.SubElement(rss, "channel")
        
        ET.SubElement(channel_rss, "title").text = f"Agenda TV Burroughs7005 [{adesso.strftime('%H:%M')}]"
        ET.SubElement(channel_rss, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel_rss, "description").text = "Programmi filtrati con data di pubblicazione"

        programmi_validi = []
        for prog in root.findall('programme'):
            orario_raw = prog.get('start', '')
            if len(orario_raw) < 14: continue
            
            data_prog = datetime.strptime(orario_raw[:14], "%Y%m%d%H%M%S")
            if data_prog < inizio_oggi: continue

            titolo = prog.find('title').text if prog.find('title') is not None else ""
            descrizione = prog.find('desc').text if prog.find('desc') is not None else ""
            
            testo_programma = (titolo + " " + descrizione).lower()
            if any(key.lower() in testo_programma for key in KEYWORDS):
                id_canale = prog.get('channel', '')
                nome_canale = canali_map.get(id_canale, id_canale)

                programmi_validi.append({
                    'data': data_prog,
                    'titolo': titolo,
                    'desc': descrizione,
                    'canale': nome_canale
                })

        # Torniamo all'ordinamento CRONOLOGICO NORMALE (dal più vicino al più lontano)
        programmi_validi.sort(key=lambda x: x['data'])

        visti = set()
        ultimo_giorno = None
        giorni_settimana = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ", "SABATO", "DOMENICA"]
        
        for p in programmi_validi:
            chiave_duplicato = (p['data'].strftime('%Y%m%d%H%M'), p['titolo'])
            if chiave_duplicato in visti: continue
            visti.add(chiave_duplicato)

            giorno_corrente = p['data'].strftime('%Y%m%d')
            
            if giorno_corrente != ultimo_giorno:
                sep = ET.SubElement(channel_rss, "item")
                nome_giorno = giorni_settimana[p['data'].weekday()]
                data_f = p['data'].strftime('%d %b')
                ET.SubElement(sep, "title").text = f"--- {nome_giorno} {data_f} ---"
                # Data fittizia per i separatori (un minuto prima del primo programma del giorno)
                pub_sep = p['data'] - timedelta(minutes=1)
                ET.SubElement(sep, "pubDate").text = pub_sep.strftime("%a, %d %b %Y %H:%M:%S +0000")
                ultimo_giorno = giorno_corrente

            item = ET.SubElement(channel_rss, "item")
            ET.SubElement(item, "title").text = f"{p['data'].strftime('%H:%M')} [{p['canale']}] - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']
            
            # AGGIUNTA FONDAMENTALE: La pubDate dice al lettore l'ordine esatto
            ET.SubElement(item, "pubDate").text = p['data'].strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{p['data'].strftime('%Y%m%d%H%M')}-{p['titolo'][:20]}"

        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: Agenda pronta per NetNewsWire.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: {e}")

def elabora():
    base_dir = "/home/pi/guida-tv"
    input_f = f"{base_dir}/guida_tv_raw.xml"
    rss_f = f"{base_dir}/index.xml"
    if os.path.exists(input_f):
        genera_rss(input_f, rss_f)
        os.remove(input_f)

if __name__ == "__main__":
    elabora()
