# Sous-titres ASS : narration, titres, étiquettes de lieu, crédits.
from plan import START, D, NAMES, S

FONT = "Noto Sans"
HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FONT},50,&H00FFFFFF,&H00FFFFFF,&H70000000,&H00000000,0,0,0,0,100,100,0.5,0,3,15,0,2,230,230,72,1
Style: Title,{FONT},78,&H00FFFFFF,&H00FFFFFF,&H78000000,&H00000000,1,0,0,0,100,100,9,0,3,34,0,5,100,100,40,1
Style: Tag,{FONT},30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,1,0,0,0,100,100,7,0,1,0,3,7,96,96,84,1
Style: Credit,{FONT},31,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0.5,0,1,0,3,5,160,160,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


events = []


def ev(start, end, style, text, fx=r"\fad(450,450)", layer=0):
    events.append(f"Dialogue: {layer},{ts(start)},{ts(end)},{style},,0,0,0,,{{{fx}}}{text}")


def reading(text):
    import re
    vis = re.sub(r'\{[^}]*\}', '', text).replace('\\N', '')
    return max(2.4, 0.9 + len(vis) / 15)


def narrate(scene, lines, first=1.1):
    t = START[scene] + first
    for line in lines:
        d = reading(line)
        ev(t, t + d, "Sub", line)
        t += d + 0.25
    return t


def tag(scene, text, first=1.0, dur=4.2):
    t = START[scene] + first
    ev(t, t + dur, "Tag", text, fx=r"\fad(500,500)\blur0.6")


# --- scène par scène --------------------------------------------------------
b = START["bouteille"]
ev(b + 0.6, b + 3.5, "Title", "DE LA BOUTEILLE À LA MONTAGNE", fx=r"\fad(700,700)")
narrate("bouteille", ["Une bouteille d'eau… mais d'où vient-elle vraiment ?"], first=3.7)

tag("source2", "VOLVIC  ·  PUY-DE-DÔME  ·  AUVERGNE")
narrate("source2", ["Direction Volvic, en Auvergne, au pied des volcans."])
narrate("source1", ["Elle y est captée dans une source profonde, avant d'être mise en bouteille."])

tag("chaine1", "LA CHAÎNE DES PUYS")
narrate("chaine1", ["Mais son vrai berceau, c'est cette montagne : la chaîne des Puys."])

narrate("drone", ["Environ 80 volcans, alignés au cœur de l'Auvergne.", "Tous endormis depuis plus de 6 000 ans."])
narrate("chaine2", ["Un paysage classé au patrimoine mondial de l'UNESCO depuis 2018."])

tag("dome1", "PUY DE DÔME  ·  ENV. 1 465 m")
narrate("dome1", ["Au centre, le Puy de Dôme, le plus haut volcan de la chaîne."])
narrate("dome2", ["Depuis son sommet, la vue embrasse tous les volcans voisins."])
narrate("droneD", ["Des cratères, des prairies : un paysage façonné par le feu."])

tag("pariou3", "PUY DE PARIOU")
narrate("pariou3", ["Le cratère du Puy de Pariou, vestige d'une ancienne éruption."])
narrate("pariou2", ["Il y a 13 500 ans, une éruption a comblé la vallée de Volvic."])

tag("chaine3", "UN FILTRE NATUREL", dur=5.0)
narrate("chaine3", [r"La pluie met environ 5 ans à traverser 6 couches de roche volcanique.{\fs34}\N(selon la marque)"])

o = START["outro"]
narrate("outro", ["Voilà le voyage d'une goutte d'eau."], first=1.0)
ev(o + 4.4, o + 7.4, "Title", "DE LA MONTAGNE À LA BOUTEILLE", fx=r"\fad(700,900)")

c = START["credits"]
credits = (r"{\fs58\b1\fsp10}CRÉDITS{\b0\fsp0}\N{\fs12} \N"
           r"{\fs30\c&HCCCCCC&}Images : Wikimedia Commons{\c&HFFFFFF&}\N{\fs12} \N"
           r"Bouteille : Tony Webster (CC BY 2.0)\N"
           r"Source : Matthieu Perona (CC BY 3.0) · Mahé Petit Garçon Curieux (CC BY-SA 3.0)\N"
           r"Paysages : Anthony Baratier · Medium69 · François Grodwohl · Clément Bardot · Pymouss · Nouill (CC BY-SA 4.0)\N{\fs12} \N"
           r"Plans de drone : « Des racines et des ailes », France Télévisions (CC BY 3.0)\N"
           r"Musique et sons : composés pour ce montage\N{\fs12} \N"
           r"{\fs26\c&HCCCCCC&}Montage personnel, non officiel. Volvic est une marque de Danone.")
ev(c + 1.2, c + 10.2, "Credit", credits, fx=r"\fad(900,900)")

open("work/subs.ass", "w", encoding="utf-8").write(HEADER + "\n".join(events) + "\n")
print(len(events), "événements ; fin des sous-titres :", ts(max(float(e.split(',')[2].split(':')[2]) for e in events)))
# contrôle : fin des sous-titres de chaque scène vs fin de la scène (début de la transition suivante comprise)
def sec(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
for k, n in enumerate(NAMES):
    ends = [sec(e.split(",")[2]) for e in events if e.startswith("Dialogue: 0") and
            S[k] <= sec(e.split(",")[1]) < S[k] + D[k] - 1.0]
    if ends:
        print(f"{n:10} sous-titres jusqu'à {max(ends):6.2f} ; scène finit {S[k] + D[k]:6.2f}")
