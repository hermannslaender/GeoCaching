import os
import shutil
import re
import zipfile
import time


source_directory = "D:/Downloads/"
target_directory = "D:/OneDrive/Dokumente/GeoCaching/gpx/"


def gpx_cleaner(filename, HTML = None):
    with open(filename, 'r', encoding='utf-8') as file:
        gpx_content = file.read()

    #print(f"- bereinige {filename}")
    gpx_content = re.sub(r"<gpx.*?><wpt lat", "<gpx><wpt lat", gpx_content, flags=re.DOTALL) # entfernt den überflüsisgen Header
    gpx_content = re.sub(r'<wpt lat="0" lon="0">.*?</wpt>', "", gpx_content, flags=re.DOTALL) # entfernt Wegpunkte ohne Koordinaten
    gpx_content = re.sub(r"<time>.*?</time>", "", gpx_content, flags=re.DOTALL) # entfernt die Uhrzeit
    #gpx_content = re.sub(r"<url>.*?</url>", "", gpx_content, flags=re.DOTALL)
    #gpx_content = re.sub(r"<urlname>.*?</urlname>", "", gpx_content, flags=re.DOTALL) # wird als Name im Garmin benötigt
    if HTML: # logs sind in Listen und PocketQueries unterschiedlich, entfernt die Kurzbeschreibung
        gpx_content = re.sub(r"<groundspeak:short_description html.*?</groundspeak:short_description>", "", gpx_content, flags=re.DOTALL)
    else:
        gpx_content = re.sub(r"<groundspeak:short_description>.*?</groundspeak:short_description>", "", gpx_content, flags=re.DOTALL)
    if HTML: # logs sind in Listen und PocketQueries unterschiedlich, entfernt die Langbeschreibung
        gpx_content = re.sub(r"<groundspeak:long_description html.*?</groundspeak:long_description>", "", gpx_content, flags=re.DOTALL)
    else:
        gpx_content = re.sub(r"<groundspeak:long_description>.*?</groundspeak:long_description>", "", gpx_content, flags=re.DOTALL)
    gpx_content = re.sub(r"<groundspeak:encoded_hints>.*?</groundspeak:encoded_hints>", "", gpx_content, flags=re.DOTALL) # entfernt Hints
    gpx_content = re.sub(r"<groundspeak:logs>.*?</groundspeak:logs>", "", gpx_content, flags=re.DOTALL) # entfernt Logs
    gpx_content = re.sub(r"<wpt[^>]*>(?:(?!<groundspeak:cache).)*?</wpt>", "", gpx_content, flags=re.DOTALL) # entfernt Wegpunkite ohne die Cache-Information
    gpx_content = re.sub(r"^\s*$\n", "", gpx_content, flags=re.MULTILINE) # entfernt Leerzeilen

    print("-", gpx_content.count("<wpt lat"), "GeoCaches")
    #print(gpx_content)

    #print(f"- lösche {filename}")
    os.remove(filename) # löscht unbereinigte datei

    filename = filename.replace(".gpx", "_clean.gpx")
    #print(f"- erzeuge {filename}")
    with open(filename, 'w', encoding='utf-8') as file: # erzeuge bereinigte datei
        file.write(gpx_content)

    return filename


def unzip_pocket_query(filename):
    #print(f"- entpacke {filename}")
    global source_directory
    with zipfile.ZipFile(filename, 'r') as zip_ref: # auspacken
         zip_ref.extractall(source_directory)
    #print(f"- lösche {filename}")
    os.remove(filename) # löscht ZIP
    filename = filename.replace(".zip", "-wpts.gpx")
    #print(f"- lösche {filename}")
    os.remove(filename) # löscht WPTS
    filename = filename.replace("-wpts.gpx", ".gpx")
    return filename

if len(os.listdir(source_directory)) == 0:
    print("keine Datei gefunden")

for filename in os.listdir(source_directory):
    match filename:
        case "zu_erledigen.gpx" | "geloest_nicht_geloggt.gpx":
            print("GeoCaching-Liste: ", filename)
            clean_file = gpx_cleaner(source_directory+filename, HTML = False)
            file_name = target_directory+filename
            #print(f"- verschiebe {filename}")
            shutil.move(clean_file, file_name) # verschiebt bereinigte GPX

        case _ if re.match(r"^\d{8}_.+\.zip$", filename):
            print("PocketQuery: ", source_directory+filename)
            gpx_file = unzip_pocket_query(source_directory+filename)
            clean_file= gpx_cleaner(gpx_file, HTML = True)
            file_name = target_directory+re.search(r'_(.*?)\.', filename).group(1)+".gpx"
            #print(f"{file_name = }")
            shutil.move(clean_file, file_name)

        case _:
            print("Sonstige: ", filename)

time.sleep(3)
