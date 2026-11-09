import json, re, sys, urllib.parse, urllib.request, html
UA = {"User-Agent": "volvic-video-project/1.0 (personal montage project)"}
API = "https://commons.wikimedia.org/w/api.php"
def api(**kw):
    kw.update(action="query", format="json")
    with urllib.request.urlopen(urllib.request.Request(API + "?" + urllib.parse.urlencode(kw), headers=UA), timeout=40) as r:
        return json.load(r)
def get(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20): f.write(chunk)
want = {
 "bouteille":  ("File:Volvic Natürliches Mineralwasser (16805913963).jpg", 1800),
 "source1":    ("File:Source de Volvic.JPG", 1900),
 "source2":    ("File:La Source Profonde Clairvic à Volvic (229742587).jpeg", 2048),
 "chaine1":    ("File:Panorama de la chaîne des Puys.jpg", 2800),
 "chaine2":    ("File:Chaîne des Puys - 139.jpg", 2800),
 "chaine3":    ("File:Volcans de la Chaîne des Puys et Massif du Sancy.jpg", 2800),
 "dome1":      ("File:Puy de Dôme during autumn.jpg", 2800),
 "dome2":      ("File:Puy de Dôme - 136.jpg", 2800),
 "pariou1":    ("File:Puy Pariou - 137.jpg", 2800),
 "pariou2":    ("File:Vue du Puy de Dôme depuis le Puy de Pariou.jpg", 2800),
 "pariou3":    ("File:Orcines - puy Pariou 20210810-01.jpg", 2800),
 "cratere":    ("File:Cratere puy de pariou.jpg", 2800),
 "video":      ("File:En Auvergne, du Puy de Dôme au Cantal - Bande-annonce.webm", None),
}
credits = {}
for key, (title, width) in want.items():
    d = api(titles=title, prop="imageinfo", iiprop="url|size|extmetadata", iiurlwidth=width or 0,
            iiextmetadatafilter="LicenseShortName|Artist|LicenseUrl")
    p = next(iter(d["query"]["pages"].values()))
    if "imageinfo" not in p: print("INTROUVABLE", title); continue
    i = p["imageinfo"][0]; m = i["extmetadata"]
    url = (i.get("thumburl") if width and i["width"] > width else i["url"])
    ext = "webm" if key == "video" else "jpg"
    dest = f"dl/{key}.{ext}"
    get(url, dest)
    artist = html.unescape(re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "?"))).strip()
    credits[key] = dict(title=title[5:], artist=artist, license=m.get("LicenseShortName", {}).get("value", "?"))
    print(f"ok {key:9} {credits[key]['license']:12} {artist[:40]}")
json.dump(credits, open("credits.json", "w"), ensure_ascii=False, indent=1)
