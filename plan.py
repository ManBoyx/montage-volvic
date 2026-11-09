# Calendrier du montage : durées des scènes, transitions, instants de début.
FPS = 30
# (nom, durée en s) : durées réglées sur la vitesse de lecture des sous-titres (~15 car./s)
SCENES = [
    ("bouteille", 8.5), ("source2", 5.8), ("source1", 7.4), ("chaine1", 6.7),
    ("drone", 9.0), ("chaine2", 6.7), ("dome1", 6.3), ("dome2", 6.4),
    ("droneD", 6.3), ("pariou3", 6.4), ("pariou2", 6.5), ("chaine3", 7.8),
    ("outro", 7.5), ("credits", 11.0),
]
# transition k -> k+1 : (type xfade, durée)
TRANS = [
    ("fadewhite", 1.0), ("smoothup", 1.0), ("circleopen", 1.0), ("fade", 1.0),
    ("smoothleft", 1.0), ("fade", 1.0), ("fade", 1.0), ("slideleft", 1.0),
    ("fade", 1.0), ("smoothright", 1.0), ("circleclose", 1.0), ("fadeblack", 1.0),
    ("fadeblack", 1.5),
]
NAMES = [n for n, _ in SCENES]
D = [d for _, d in SCENES]
# début de chaque scène sur la timeline finale
S = [sum(D[:k]) - sum(t for _, t in TRANS[:k]) for k in range(len(D))]
START = dict(zip(NAMES, S))
TOTAL = S[-1] + D[-1]
# instant de chaque xfade dans le flux enchaîné
OFFSETS = [S[k + 1] for k in range(len(TRANS))]
if __name__ == "__main__":
    for (n, d), s in zip(SCENES, S): print(f"{n:10} début {s:6.2f}  durée {d:4.1f}")
    print("total", TOTAL)
