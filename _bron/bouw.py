"""Bouwt alle HTML-pagina's van snoerscherm.nl, plus sitemap.xml.

Gebruik: python3 _bron/bouw.py

Pas teksten aan in _bron/paginas/ en de gedeelde stukken in _bron/sjablonen/.
De HTML-bestanden in de hoofdmap worden door dit script overschreven, dus wijzig
die niet met de hand. Nodig: Python 3.9+ met jinja2 (pip install jinja2).

De map _bron/ begint met een liggend streepje, dus GitHub Pages publiceert hem niet.
"""
import hashlib
import json
import re
from html import unescape
from datetime import date
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

BRON = Path(__file__).resolve().parent
ROOT = BRON.parent

SITE = {
    "url": "https://snoerscherm.nl/",
    "naam": "Snoer & Scherm",
    "eigenaar": "Maurits Oldenburg",
    "tel": "015-2001202",
    "tel_link": "tel:+31152001202",
    "tel_int": "+31152001202",
    "wa_nummer": "31152001202",
    "email": "maurits@snoerscherm.nl",
    "kvk": "96720018",
    "google": "https://maps.app.goo.gl/x6gsZct3UxF71vwT9?g_st=ac",
    "plaatsen": ["Delft", "Delfgauw", "Pijnacker", "Nootdorp", "Rijswijk"],
    "plaatsen_tekst": "Delft, Delfgauw, Pijnacker, Nootdorp en Rijswijk",
    "uren": "10.00 tot 22.00 uur",
    "inleverpunt": {
        "naam": "The Social Hub",
        "straat": "Van Leeuwenhoekpark 1",
        "postcode": "2611 DW",
        "plaats": "Delft",
        "kaart": "https://www.google.com/maps/search/?api=1&query=The+Social+Hub+Van+Leeuwenhoekpark+1+Delft",
    },
    "deelbeeld": "img/snoer-en-scherm-delen.jpg",
    "jaar": date.today().year,
}

# Volgorde = volgorde op het dienstenbord, in het menu en in de footer.
DIENSTEN = [
    {"groep": "computers", "url": "computerhulp-aan-huis-delft.html", "naam": "Computerhulp aan huis",
     "info": "Trage laptop, virus, gehackt e-mailadres of een nieuwe computer instellen"},
    {"groep": "computers", "url": "water-over-laptop-delft.html", "naam": "Water over uw laptop",
     "info": "Wat u nu meteen moet doen, en waarom haast helpt", "spoed": True},
    {"groep": "computers", "url": "computerhulp-senioren-delft.html", "naam": "Computerhulp voor senioren",
     "info": "Uitleg in gewone woorden, bij u aan tafel en in uw tempo"},
    {"groep": "apparaten", "url": "koffiemachine-reparatie-delft.html", "naam": "Koffiemachines",
     "info": "Senseo, Nespresso en volautomaten van De'Longhi, Philips en Jura"},
    {"groep": "apparaten", "url": "stofzuiger-reparatie-delft.html", "naam": "Stofzuigers",
     "info": "Steelstofzuigers en robots zoals Roomba en Roborock"},
    {"groep": "apparaten", "url": "huishoudelijke-apparaten-reparatie-delft.html", "naam": "Huishouden en gereedschap",
     "info": "Afzuigkap, strijkijzer, waterkoker, mixer of boormachine"},
    {"groep": "apparaten", "url": "platenspeler-audio-reparatie-delft.html", "naam": "Platenspeler en audio",
     "info": "Platenspelers, versterkers en luidsprekers"},
    {"groep": "apparaten", "url": "feest-av-apparatuur-reparatie-delft.html", "naam": "Feest- en AV-apparatuur",
     "info": "Rookmachines, licht, actieve speakers en mengpanelen"},
    {"groep": "apparaten", "url": "kleine-elektronica-reparatie-delft.html", "naam": "Kleine elektronica",
     "info": "Joy-Con drift, e-readers, koptelefoons en printers"},
]
DIENST = {d["url"]: d for d in DIENSTEN}

INFO = [
    {"url": "werkwijze-en-kosten.html", "naam": "Werkwijze en kosten", "lang": "Werkwijze en kosten",
     "info": "Gratis onderzoek, een vaste prijs vooraf en 3 maanden garantie"},
    {"url": "inleveren-op-afspraak-delft.html", "naam": "Inleveren", "lang": "Inleveren op afspraak",
     "info": "Uw apparaat afgeven op een tijd en plek die u uitkomt"},
    {"url": "over-mij.html", "naam": "Over mij", "lang": "Over mij",
     "info": "Wie er achter Snoer & Scherm zit en hoe ik werk"},
    {"url": "veelgestelde-vragen.html", "naam": "Vragen", "lang": "Veelgestelde vragen",
     "info": "Over kosten, garantie, bereikbaarheid en wat ik niet repareer"},
]
for _i in INFO:
    DIENST[_i["url"]] = {**_i, "naam": _i["lang"]}

GROEP_NAAM = {"computers": "Computers en laptops", "apparaten": "Elektrische apparaten"}

# Elke pagina: bestand, sjabloon, titel, beschrijving en waar hij in de kruimels hangt.
PAGINAS = [
    {"bestand": "index.html", "titel": "Computerhulp en reparatie aan huis in Delft | Snoer & Scherm",
     "beschrijving": "Computerhulp en reparatie van koffiemachines, stofzuigers en audio, aan huis in Delft, Delfgauw, Pijnacker, Nootdorp en Rijswijk. Onderzoek gratis, prijs vooraf.",
     "prio": "1.0", "soort": "home"},

    {"bestand": "computerhulp-aan-huis-delft.html", "dienst": "Computerhulp en laptopreparatie",
     "titel": "Computerhulp en laptopreparatie in Delft | Snoer & Scherm",
     "beschrijving": "Trage laptop, virus, gehackt e-mailadres of een nieuwe computer instellen? Maurits helpt aan huis in Delft en omstreken. Gratis onderzoek, vaste prijs vooraf."},
    {"bestand": "water-over-laptop-delft.html", "dienst": "Waterschade aan laptops verhelpen",
     "titel": "Water over uw laptop in Delft? Dit moet u nu doen | Snoer & Scherm",
     "beschrijving": "Water, koffie of een ander vocht over uw laptop gemorst in Delft? Lees wat u nu direct moet doen en waarom snelheid bepaalt of uw laptop het overleeft."},
    {"bestand": "computerhulp-senioren-delft.html", "dienst": "Computerhulp voor senioren",
     "titel": "Computerhulp voor senioren in Delft | Snoer & Scherm",
     "beschrijving": "Hulp met uw computer, e-mail, foto's of printer, bij u thuis in Delft en omstreken. Uitleg zonder vaktaal en hulp bij verdachte berichten. Onderzoek gratis."},
    {"bestand": "koffiemachine-reparatie-delft.html", "dienst": "Koffiemachine reparatie",
     "titel": "Koffiemachine reparatie in Delft | Snoer & Scherm",
     "beschrijving": "Uw Senseo, Nespresso of volautomaat van De'Longhi, Philips of Jura kapot? Ik repareer koffiemachines aan huis in Delft en omstreken."},
    {"bestand": "stofzuiger-reparatie-delft.html", "dienst": "Stofzuiger reparatie",
     "titel": "Stofzuiger reparatie Delft, ook robotstofzuigers | Snoer & Scherm",
     "beschrijving": "Roomba, Roborock of een steelstofzuiger kapot? Ik repareer stofzuigers aan huis in Delft en omstreken."},
    {"bestand": "huishoudelijke-apparaten-reparatie-delft.html", "dienst": "Reparatie van huishoudelijke apparaten en gereedschap",
     "titel": "Huishoudelijke apparaten repareren in Delft | Snoer & Scherm",
     "beschrijving": "Afzuigkap, strijkijzer, waterkoker, mixer of boormachine kapot? Ik repareer huishoudelijke apparaten en gereedschap aan huis in Delft en omstreken."},
    {"bestand": "platenspeler-audio-reparatie-delft.html", "dienst": "Platenspeler en audioapparatuur reparatie",
     "titel": "Platenspeler en audioapparatuur reparatie Delft | Snoer & Scherm",
     "beschrijving": "Platenspeler, luidsprekers of versterker kapot? Ik repareer audioapparatuur aan huis in Delft en omstreken."},
    {"bestand": "feest-av-apparatuur-reparatie-delft.html", "dienst": "Feest- en AV-apparatuur reparatie",
     "titel": "Feest- en AV-apparatuur reparatie Delft | Snoer & Scherm",
     "beschrijving": "Rookmachine, lichteffect, actieve speaker of mengpaneel kapot? Ik repareer feest- en AV-apparatuur voor buurthuizen, verenigingen, cafés en dj's in Delft."},
    {"bestand": "kleine-elektronica-reparatie-delft.html", "dienst": "Reparatie van kleine elektronica",
     "titel": "Joy-Con drift en kleine elektronica, Delft | Snoer & Scherm",
     "beschrijving": "Joy-Con die vanzelf stuurt, e-reader die niet laadt, koptelefoon of printer kapot? Ik kijk ernaar in Delft en omstreken en zeg eerlijk wat wel en niet kan."},

    {"bestand": "werkwijze-en-kosten.html", "titel": "Werkwijze en kosten van een reparatie | Snoer & Scherm",
     "beschrijving": "Zo werkt een reparatie bij Snoer & Scherm: gratis onderzoek, een vaste prijs voordat ik begin, betalen achteraf en 3 maanden garantie op het werk."},
    {"bestand": "inleveren-op-afspraak-delft.html", "titel": "Apparaat inleveren op afspraak in Delft | Snoer & Scherm",
     "beschrijving": "Laptop of apparaat kapot en liever niet thuis wachten? Geef het op afspraak af op een plek die u uitkomt in Delft, bijvoorbeeld naast station Delft."},
    {"bestand": "over-mij.html", "titel": "Over Maurits Oldenburg | Snoer & Scherm in Delft",
     "beschrijving": "Maak kennis met Maurits Oldenburg van Snoer & Scherm: computerhulp en reparatie van elektrische apparaten, aan huis in Delft en omstreken.",
     "soort": "over"},
    {"bestand": "veelgestelde-vragen.html", "titel": "Veelgestelde vragen | Snoer & Scherm, computerhulp Delft",
     "beschrijving": "Wat kost een reparatie, hoe snel kunt u komen, wat repareer ik niet en hoe zit het met garantie? Antwoorden op de vragen die ik het vaakst krijg.",
     "soort": "faq"},

    {"bestand": "404.html", "titel": "Pagina niet gevonden | Snoer & Scherm", "kruimel": "Niet gevonden",
     "beschrijving": "Deze pagina bestaat niet (meer).", "noindex": True, "soort": "404"},
]


def platte_tekst(html):
    tekst = re.sub(r"<[^>]+>", "", html)
    return " ".join(unescape(tekst).split())


def wa(tekst="Hallo Maurits, ik heb een vraag."):
    return f"https://wa.me/{SITE['wa_nummer']}?text={quote(tekst)}"


def bedrijf_schema():
    return {
        "@type": "LocalBusiness",
        "@id": SITE["url"] + "#bedrijf",
        "name": SITE["naam"],
        "url": SITE["url"],
        "telephone": SITE["tel_int"],
        "email": SITE["email"],
        "image": SITE["url"] + SITE["deelbeeld"],
        "logo": SITE["url"] + "img/icoon-192.png",
        "description": "Computerhulp en reparatie van elektrische apparaten, aan huis in Delft en omstreken.",
        "founder": {"@type": "Person", "@id": SITE["url"] + "over-mij.html#maurits", "name": SITE["eigenaar"]},
        "areaServed": [{"@type": "City", "name": p} for p in SITE["plaatsen"]],
        "sameAs": [SITE["google"]],
        "identifier": {"@type": "PropertyValue", "name": "KvK", "value": SITE["kvk"]},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "10:00", "closes": "22:00",
        }],
        "paymentAccepted": "Contant, creditcard, Revolut, ING, Google Pay",
        "currenciesAccepted": "EUR",
        "knowsLanguage": "nl",
    }


def kruimels(p):
    if p["bestand"] == "index.html":
        return []
    rij = [{"naam": "Home", "url": "./"}]
    d = DIENST.get(p["bestand"])
    if d and d.get("groep"):
        rij.append({"naam": GROEP_NAAM[d["groep"]], "url": "./#diensten"})
    rij.append({"naam": p.get("kruimel") or p.get("kort") or p["h1"], "url": p["bestand"]})
    return rij


def schema_voor(p, kruim, vragen):
    url = SITE["url"] + ("" if p["bestand"] == "index.html" else p["bestand"])
    graaf = [bedrijf_schema()]
    if p.get("soort") == "home":
        graaf.append({"@type": "WebSite", "@id": SITE["url"] + "#site", "url": SITE["url"],
                      "name": SITE["naam"], "inLanguage": "nl-NL", "publisher": {"@id": SITE["url"] + "#bedrijf"}})
    pagina = {"@type": "WebPage", "@id": url + "#pagina", "url": url, "name": p["titel"],
              "description": p["beschrijving"], "inLanguage": "nl-NL", "isPartOf": {"@id": SITE["url"] + "#site"}}
    if p.get("soort") == "over":
        pagina["@type"] = "AboutPage"
        graaf.append({"@type": "Person", "@id": SITE["url"] + "over-mij.html#maurits", "name": SITE["eigenaar"],
                      "jobTitle": "Reparateur", "worksFor": {"@id": SITE["url"] + "#bedrijf"},
                      "image": SITE["url"] + "img/maurits-portret-720.webp"})
    if p.get("soort") == "faq" and vragen:
        pagina["@type"] = ["WebPage", "FAQPage"]
        pagina["mainEntity"] = [{"@type": "Question", "name": v,
                                 "acceptedAnswer": {"@type": "Answer", "text": platte_tekst(a)}} for v, a in vragen]
    graaf.append(pagina)
    if p.get("dienst"):
        graaf.append({"@type": "Service", "name": p["dienst"], "serviceType": p["dienst"], "url": url,
                      "provider": {"@id": SITE["url"] + "#bedrijf"},
                      "areaServed": [{"@type": "City", "name": c} for c in SITE["plaatsen"]]})
    if kruim:
        graaf.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": k["naam"],
             "item": SITE["url"] + ("" if k["url"] in ("./", "./#diensten") else k["url"])}
            for i, k in enumerate(kruim)]})
    tekst = json.dumps({"@context": "https://schema.org", "@graph": graaf}, ensure_ascii=False, indent=1)
    return tekst.replace("</", "<\\/")


def maak_env():
    env = Environment(
        loader=FileSystemLoader([BRON / "sjablonen", BRON / "paginas"]),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(site=SITE, diensten=DIENSTEN, info=INFO, groep_naam=GROEP_NAAM, wa=wa, dienst=DIENST)
    return env


def lastmod_bijwerken(resultaten):
    pad = BRON / "lastmod.json"
    oud = json.loads(pad.read_text()) if pad.exists() else {}
    vandaag = date.today().isoformat()
    nieuw = {}
    for bestand, html in resultaten.items():
        h = hashlib.sha256(html.encode()).hexdigest()[:16]
        vorig = oud.get(bestand, {})
        nieuw[bestand] = {"hash": h, "datum": vorig["datum"] if vorig.get("hash") == h else vandaag}
    pad.write_text(json.dumps(nieuw, indent=1, sort_keys=True) + "\n")
    return nieuw


def main():
    env = maak_env()
    resultaten = {}
    for p in PAGINAS:
        for sleutel, standaard in (("noindex", False), ("soort", "dienst"), ("dienst", None), ("kruimel", None)):
            p.setdefault(sleutel, standaard)
        sjabloon = env.get_template(p["bestand"])
        # Eerst één keer renderen om h1, vragen en kruimeltekst uit het sjabloon op te halen.
        mod = sjabloon.make_module({"pagina": {**p, "pad": "", "kruimels": [], "schema": "", "canoniek": ""}})
        p["h1"] = getattr(mod, "h1", p["titel"])
        p["kort"] = getattr(mod, "kort", None)
        vragen = getattr(mod, "vragen", None)
        kruim = kruimels(p)
        ctx = {**p, "pad": "/" if p.get("soort") == "404" else "", "kruimels": kruim,
               "schema": schema_voor(p, kruim, vragen),
               "canoniek": SITE["url"] + ("" if p["bestand"] == "index.html" else p["bestand"])}
        html = sjabloon.render(pagina=ctx)
        resultaten[p["bestand"]] = html

    for bestand, html in resultaten.items():
        (ROOT / bestand).write_text(html, encoding="utf-8")

    datums = lastmod_bijwerken(resultaten)
    regels = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGINAS:
        if p.get("noindex"):
            continue
        loc = SITE["url"] + ("" if p["bestand"] == "index.html" else p["bestand"])
        regels += ["  <url>", f"    <loc>{loc}</loc>", f"    <lastmod>{datums[p['bestand']]['datum']}</lastmod>",
                   f"    <priority>{p.get('prio', '0.8')}</priority>", "  </url>"]
    regels.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(f"{len(resultaten)} pagina's en sitemap.xml geschreven")


if __name__ == "__main__":
    main()
