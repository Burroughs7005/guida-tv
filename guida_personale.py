import os
from datetime import datetime

def elabora():
    # Percorsi assoluti per evitare errori di cartella
    input_f = "/home/pi/guida-tv/guida_tv_raw.xml"
    output_f = "/home/pi/guida-tv/guida_tv.xml"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] --- Inizio Elaborazione Python ---")
    
    if os.path.exists(input_f):
        # Rinomina il file scaricato per passarlo al compressore gzip
        if os.path.exists(output_f):
            os.remove(output_f)
        os.rename(input_f, output_f)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESSO: File pronto per la compressione.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRORE: Non trovo {input_f}")

if __name__ == "__main__":
    elabora()
