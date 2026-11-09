**Français** · [English](#english)

# Montage « De la bouteille à la montagne » (Volvic / Chaîne des Puys)

Chaîne de scripts Python + ffmpeg qui fabrique un court montage vidéo à partir de **photos et d'une vidéo libres de droits** (Wikimedia Commons), avec musique composée par code, sous-titres et transitions. Rien n'est téléchargé à la main : les médias sont récupérés par `fetch.py`, et leurs auteurs et licences sont listés dans `credits.json`.

## Ordre de fabrication
Dans un dossier de travail contenant `work/` et `dl/` :
```bash
python3 fetch.py         # télécharge photos + vidéo libres (Wikimedia Commons) dans dl/
python3 music.py         # compose la musique         -> work/musique.wav
python3 build_scenes.py  # rend les 14 scènes         -> work/sNN_*.mp4
python3 make_ass.py      # sous-titres                -> work/subs.ass
python3 assemble.py out.mp4
```
Les textes sont dans `make_ass.py`, les durées et transitions dans `plan.py`.

## Prérequis
`ffmpeg`, Python 3 avec `Pillow` et `numpy`.

## Médias et licences
Les médias ne sont **pas** inclus dans ce dépôt. Chacun garde sa licence d'origine : voir `credits.json` pour les auteurs et licences, et créditez-les si vous publiez le résultat.

## Licence
Les scripts sont sous [MIT](LICENSE).

---

# English

# "From the bottle to the mountain" montage (Volvic / Chaîne des Puys)

A chain of Python + ffmpeg scripts that builds a short video montage from **freely licensed photos and a video** (Wikimedia Commons), with music composed in code, subtitles and transitions. Nothing is downloaded by hand: media are fetched by `fetch.py`, and their authors and licenses are listed in `credits.json`.

## Build order
In a working folder containing `work/` and `dl/`:
```bash
python3 fetch.py         # downloads free photos + video (Wikimedia Commons) into dl/
python3 music.py         # composes the music        -> work/musique.wav
python3 build_scenes.py  # renders the 14 scenes     -> work/sNN_*.mp4
python3 make_ass.py      # subtitles                 -> work/subs.ass
python3 assemble.py out.mp4
```
Texts are in `make_ass.py`, durations and transitions in `plan.py`.

## Requirements
`ffmpeg`, Python 3 with `Pillow` and `numpy`.

## Media and licenses
The media are **not** included in this repository. Each keeps its original license: see `credits.json` for authors and licenses, and credit them if you publish the result.

## License
The scripts are under [MIT](LICENSE).
