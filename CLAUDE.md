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
  SEK-I-Variante = dieselbe Vorlage, aber pro Zelle die Elektronenkonfigurations-
  Zeile durch das Emoji des Elements ersetzt (dieselben Emojis wie in der
  `EL`-Datenliste im Trainer selbst, per Skript aus dort extrahiert — nicht
  von Hand eingetragen), bei sonst unverändertem hellem/weißem Zellhintergrund
  (tonersparend zum Ausdrucken gedacht, bewusst nicht auf das dunkle Trainer-
  Farbschema umgestellt).
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

## Formel-Konstruktion (chemical_communication_trainer.html)
Datenmodell: `{atoms:[{e,x,y,lp,hidden}], bonds:[{a,b,o,st?}]}`, Bindungslänge 1, y wächst nach
unten. `render(struct, opts)` zeichnet Lewis (`showH/showLP`) oder Skelett (`hidden` = C ohne
Beschriftung); große Moleküle (Skalierung < `BOND_MIN`) bekommen eine breitere/höhere viewBox statt
Überlauf; `struct.note` = Fußnote (`{de,en}`); Bindung mit `st:"wedge"|"hash"` = Keil/Strich.

**Zwei Generationen, bewusst nebeneinander:**
- *Ältere Einzelgeneratoren* (Alkane … Ester, Isomere): je Stoffklasse eigene Funktionen
  (`nAlkaneFull`, `nAcidSkeletal`, `branchedAlkeneFull` …) mit handgesetzten Koordinaten.
  Nicht anfassen ohne Regressionstest — die Ausgabe ist Byte für Byte abgesichert (siehe unten).
  Tot (unbenutzt): `attachMethylRadial`, `addHsRadial`, `skeletalToFull`.
- *Konstruktions-Engine* (Polyene, Polyole; Abschnitt „KONSTRUKTIONS-ENGINE" vor dem Katalog):
  Eingabe = Kurzschreibweise des Schweratom-Graphen (SMILES-artig, `parseSpec`), Ausgabe = beide
  Formeln aus **einer** Koordinatenbasis.

**Regeln der Engine (Winkel relativ zur ankommenden Bindung dIn):**
| Regel | Vorschrift |
|---|---|
| S1 Kette | 1 Nachfolger → dIn ± 60°, Vorzeichen wechselt je Atom (Zickzack = E/trans); sp → dIn (linear) |
| S2 Trigonal | 2 Nachfolger → Hauptkette dIn + s·60°, Zweig dIn − s·60° (alle Winkel 120°) |
| S3 Kreuz | 3 Nachfolger → dIn, dIn ± 90° |
| S4 Ring | regelmäßiges n-Eck, gleicher Drehsinn; Substituenten auf der Außenwinkelhalbierenden, zwei Stück ± `EXO_FAN`/2 |
| S5 OH im Skelett | O und H als eigene Atome, H gebogen (C–O ± 60°) auf der freieren Seite |
| L1 Struktur | fehlende H (C 4, O 2 Bindungen) gleichmäßig in die Winkellücken: 90° am CH₃/CH₂ (Kreuz), 120° am sp²-C, O–H linear; danach Energie-Minimierung gegen H-Überlappung |
| L2 Fischer | Polyole: Kette senkrecht, OH waagerecht (Kreuz um 90° gedreht), H nach L1 |
| Stereo | Fischer-Seite (R/L) bzw. Marke `<R>`/`<S>` → Keil/Strich aus den fertigen Koordinaten (Spatprodukt / CIP-Rang), nie von Hand |
Das Layout wird aus 192 Kandidaten (Startrichtung, Drehsinne, Ringseiten) gewählt: keine
Überlappung → waagerecht → Keile vor Strichen → wenig H-Überlappung → erstes Atom links.

**Neues Molekül in der Engine:** Eintrag in `ENGINE_DEFS` (`spec` oder `chain`, Name/en/Formel/
Aliasse, `sub`), Kontext-Info in `CONTEXT_INFO`, ggf. Aggregatzustand in `STATE_AT_STP`.
Prüfen: Valenzen/Atomzahlen (C/H/O-Bilanz), keine Paare < 0,6 im Lewis-Bild, Sichtprüfung gegen die
Vorlage-SVG (Carotinoid-Vorlagen liegen unter `Material SEK II/Chemie/LK/Q1/…/02-Chemische Bindung/
Carotinoide/stuff/`; sie sind reine Grafiken ohne Graph — nachgebaut, nicht eingebettet).

**Regressionstest (nicht im Repo):** Skript per `node:vm` laden (`renderApp()` am Ende abschneiden,
`document`/`window` stubben), alle Substanzen × {structural, skeletal} × {de, en} rendern und mit dem
Stand vor der Änderung vergleichen; muss 0 Abweichungen liefern.

**Bekannte Inkonsistenzen der älteren Generatoren (dokumentiert, nicht behoben):**
- Alkin-Skelette mit endständiger Dreifachbindung (Propin ab Pent-1-in): am C hinter dem linearen
  Segment 150° statt 120° (`nAlkyneSkeletal`, Zickzack startet mit 30° statt 60° Abknickung).
- Hydroxyl-H im Skelett: Alkanole gebogen (120°), Alkansäuren linear in Verlängerung der C–O-Achse.
- Verzweigte Alkane/Alkene/Alkine: Hauptkette in der Lewis-Formel mit Abstand 2, unverzweigte mit 1.

## Stoffklassen-Übersicht: Stufen-Info
`CLASS_LEVEL` (`grade` = SEK-I-Jahrgang, `sek2`, `deep` = Vertiefung) ist die einzige Quelle für das
aufklickbare Info-Feld („i") oben rechts an jeder Stoffklasse und für `YEAR_CLASSES`.
SEK I 7–8: Elemente/Nichtmetalle, Metalle, Salze, Molekülverbindungen. SEK I 9–10: Säuren, Basen,
Alkane … Ester. Vertiefung: Übergangsmetalle, Aromaten, Polyene 🌈, Polyole 🍬. `sek2` ist für alle
Klassen `true` (Wiederholung/Grundlagen) — bei Bedarf in `CLASS_LEVEL` ändern.

## Zusammenspiel
- ClassroomSpark/index.html verlinkt auf die Dateien hier
  (Play Online und Download). Neue Trainer dort ergänzen.
- Dateinamen nicht ändern, ohne die Links in ClassroomSpark anzupassen.

## Öffentlich — Vorsicht
- Public Repo mit GitHub Pages, von Schüler:innen einsehbar.
  Keine personenbezogenen Daten.
