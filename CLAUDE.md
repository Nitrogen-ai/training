# training

## Was das ist
- EINZIGE Quelle aller interaktiven Trainer (HTML).
- Über GitHub Pages veröffentlicht: nitrogen-ai.github.io/training/
- Neutrale URL für den Unterrichtseinsatz. ClassroomSpark
  (Landingpage für Lehrkräfte) wird hier nicht erwähnt oder verlinkt.

## Konventionen
- Jeder Trainer ist eine einzelne, offline lauffähige HTML-Datei
  — keine CDN-Abhängigkeiten.
- Oberflächensprache passend zum Fach (Englisch-Trainer auf Englisch).
- Trainer werden NUR hier bearbeitet, nie in ClassroomSpark.

## Ausnahme: pse-assets/ (periodensystem_trainer.html)
- Vier statische Downloads für den "PSE-Poster"-Exportbutton im Trainer:
  `pse-poster-sek{1,2}-de-en.{html,pdf}`. Quelle: das zweisprachige SEK-II-
  PSE-Poster der Nutzerin/des Nutzers (`Unterricht/Material SEK II/Chemie/
  Periodensystem SEK II (zweisprachig).html/.pdf`, außerhalb dieses Repos).
  SEK-I-Variante = dieselbe Vorlage, aber ohne die Elektronenkonfigurations-
  Zeile pro Zelle (per Skript entfernt, nicht von Hand).
- Beide Varianten haben eine ausgeschriebene Legende (OZ/Masse/EN in Worten,
  nicht nur als Kürzel) auf Seite 2 des Posters — das war ursprünglich nur
  knapp abgekürzt und wurde auf Nutzerwunsch ergänzt.
- Bei Änderungen an der Quelldatei: `.html`-Varianten neu aus der Quelle
  ableiten (Skript-Ansatz, kein manuelles Koordinaten-Fummeln — die Zellen
  im PSE-Poster sind absolut positioniert, siehe Kommentare im Trainer-Code
  für die genaue Vorgehensweise), dann PDFs neu erzeugen, z. B. mit lokal
  installiertem Chrome im Headless-Modus:
  `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless
  --disable-gpu --no-sandbox --print-to-pdf=out.pdf --print-to-pdf-no-header
  file:///pfad/zur/datei.html`.

## Zusammenspiel
- ClassroomSpark/index.html verlinkt auf die Dateien hier
  (Play Online und Download). Neue Trainer dort ergänzen.
- Dateinamen nicht ändern, ohne die Links in ClassroomSpark anzupassen.

## Öffentlich — Vorsicht
- Public Repo mit GitHub Pages, von Schüler:innen einsehbar.
  Keine personenbezogenen Daten.
