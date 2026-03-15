import requests
import gzip
from lxml import etree
from datetime import datetime
import os

# --- CONFIGURAZIONE ---
XMLTV_URL = "https://www.epg-guide.com/it.xml.gz"
GITHUB_USER = "Burroughs7005"
REPO_NAME = "guida-tv"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) RaspberryPi/Glasgy'}

# Le tue parole chiave
KEYWORDS = [
    "Annika", "Bastardi di Pizzofalcone", "Che tempo che fa", "Coliandro",
    "Il Commissario Montalbano", "Propaganda Live", "Quante storie", 
    "Schiavone", "Shetland", "La Torre di Babele", "Kubrick", "Alberto Angela", 
    "Mario Monicelli", "Ettore Scola", "Gassman", "Tino Buazzelli", 
    "Eduardo De Filippo", "Nino Manfredi", "Ugo Tognazzi", "Vittorio De Sica",
    "Pallavolo", "Superlega", "Tigotà", "Volley Femminile", "Volley Maschile"
]

def scarica_e_filtra():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scaricamento palinsesto...")
    try:
        r = requests.get(XMLTV_URL, headers=HEADERS, timeout=60)
        r.raise_for_status()
        
        # Verifica se è un GZIP (i primi due byte devono essere 1f 8b)
        if r.content[:2] != b'\x1f\x8b':
            print("Errore: Il server non ha restituito un file compresso valido.")
            return []

        with open("temp.xml.gz", "wb") as f:
            f.write(r.content)
        
        programmi_filtrati = []
        with gzip.open("temp.xml.gz", "rb") as f:
            tree = etree.parse(f)
            root = tree.getroot()
            oggi = datetime.now().strftime("%Y%m%d")
            
            for prog in root.xpath("//programme"):
                start = prog.get("start")
                # Filtriamo solo programmi di oggi
                if not start.startswith(oggi): 
                    continue
                
                titolo = "".join(prog.xpath("./title/text()"))
                desc = "".join(prog.xpath("./desc/text()"))
                canale = prog.get("channel")
                
                testo_completo = (titolo + " " + desc).lower()
                for key in KEYWORDS:
                    if key.lower() in testo_completo:
                        ora = f"{start[8:10]}:{start[10:12]}"
                        programmi_filtrati.append({
                            'titolo': titolo,
                            'ora': ora,
                            'canale': canale,
                            'desc': desc
                        })
                        break
        return programmi_filtrati

    except Exception as e:
        print(f"Errore durante lo scaricamento o il parsing: {e}")
        return []

def genera_rss(programmi):
    print(f"Generazione feed per {len(programmi)} programmi trovati...")
    rss = etree.Element("rss", version="2.0")
    channel = etree.SubElement(rss, "channel")
    etree.SubElement(channel, "title").text = "Guida TV Personalizzata Burroughs7005"
    etree.SubElement(channel, "link").text = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/"
    etree.SubElement(channel, "description").text = f"Aggiornato il {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    # Se non ci sono match, aggiungiamo un avviso nel feed
    if not programmi:
        item = etree.SubElement(channel, "item")
        etree.SubElement(item, "title").text = "Nessun programma trovato per oggi"
        etree.SubElement(item, "description").text = "Prova a controllare i termini chiave."

    for p in programmi:
        item = etree.SubElement(channel, "item")
        etree.SubElement(item, "title").text = f"[{p['ora']}] {p['titolo']} - {p['canale']}"
        etree.SubElement(item, "description").text = p['desc']
        etree.SubElement(item, "guid", isPermaLink="false").text = f"{p['ora']}-{p['titolo']}-{p['canale']}"

    # Scrittura del file index.xml con formattazione leggibile
    with open("index.xml", "wb") as f:
        f.write(etree.tostring(rss, xml_declaration=True, encoding="utf-8", pretty_print=True))

if __name__ == "__main__":
    progs = scarica_e_filtra()
    genera_rss(progs)
    print("Processo completato.")
