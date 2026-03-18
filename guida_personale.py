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
    inizio_oggi = adesso.replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"[{adesso.strftime('%H:%M:%S')}] Generazione agenda ottimizzata per NetNewsWire...")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Mappa Canali
        canali_map = {}
        for chan in root.findall('channel'):
            chan_id = chan.get('id')
            display_name = chan.find('display-name')
            if chan_id and display_name is not None:
                canali_map[chan_id] = display_name.text

        rss = ET.Element("rss", version="2.0")
        channel_rss = ET.SubElement(rss, "channel")
        
        timestamp_titolo = adesso.strftime('%H:%M')
        ET.SubElement(channel_rss, "title").text = f"Agenda TV Burroughs7005 [{timestamp_titolo}]"
        ET.SubElement(channel_rss, "link").text = "https://burroughs7005.github.io/guida-tv/"
        ET.SubElement(channel_rss, "description").text = f"Programmi filtrati - Aggiornato il {adesso.strftime('%d/%m/%Y %H:%M')}"

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

        # ORDINAMENTO INVERSO: I programmi più vicini (oggi) finiscono "in cima" al file XML
        # Questo forza molti lettori RSS a mostrarli per primi.
        programmi_validi.sort(key=lambda x: x['data'], reverse=True)

        # RIMOZIONE DUPLICATI (stessa ora, stesso titolo)
        visti = set()
        ultimo_giorno = None
        giorni_settimana = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ", "SABATO", "DOMENICA"]
        
        for p in programmi_validi:
            # Controllo duplicati (ignoriamo il canale, se titolo e ora sono uguali è lo stesso show)
            chiave_duplicato = (p['data'].strftime('%Y%m%d%H%M'), p['titolo'])
            if chiave_duplicato in visti:
                continue
            visti.add(chiave_duplicato)

            giorno_corrente = p['data'].strftime('%Y%m%d')
            
            # Nota: con l'ordine inverso, i separatori di giorno appariranno "sotto" i programmi del giorno stesso
            # ma è necessario per mantenere la coerenza cronologica nel lettore RSS.
            if giorno_corrente != ultimo_giorno:
                sep = ET.SubElement(channel_rss, "item")
                nome_giorno = giorni_settimana[p['data'].weekday()]
                data_f = p['data'].strftime('%d %b')
                ET.SubElement(sep, "title").text = f"--- {nome_giorno} {data_f} ---"
                ET.SubElement(sep, "description").text = "Inizio elenco"
                ultimo_giorno = giorno_corrente

            item = ET.SubElement(channel_rss, "item")
            ora_str = p['data'].strftime('%H:%M')
            ET.SubElement(item, "title").text = f"{ora_str} [{p['canale']}] - {p['titolo']}"
            ET.SubElement(item, "description").text = p['desc']
            # Aggiungiamo un GUID univoco basato su data e titolo per aiutare il lettore RSS
            guid = ET.SubElement(item, "guid", isPermaLink="false")
            guid.text = f"{p['data'].strftime('%Y%m%d%H%M')}-{p['titolo'][:20]}"

        with open(rss_file, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(ET.tostring(rss, encoding="utf-8"))
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: Agenda aggiornata e pulita.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: {e}")

def elabora():
    base_dir = "/home/pi/guida-tv"
    input_f = f"{base_dir}/guida_tv_raw.xml"
    rss_f = f"{base_dir}/index.xml"
    
    if os.path.exists(input_f):
        genera_rss(input_f, rss_f)
        # Non eliminiamo il raw se vogliamo fare test, ma qui seguiamo il tuo workflow
        os.remove(input_f)
    else:
        print("Errore: guida_tv_raw.xml non trovato.")

if __name__ == "__main__":
    elabora()
