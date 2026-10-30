# snoerscherm.nl

Website van Snoer & Scherm (Maurits Oldenburg), gehost op GitHub Pages met eigen domein.

## Zo werkt de site

- De HTML-pagina's in de hoofdmap worden **gegenereerd**. Pas ze niet met de hand aan.
- Teksten staan in `_bron/paginas/` (één bestand per pagina, Jinja2).
- Gedeelde stukken (kopbalk, menu, footer, knoppen, het reparatielabel) staan in `_bron/sjablonen/`.
- Paginalijst, titels, meta-beschrijvingen, diensten en contactgegevens staan in `_bron/bouw.py`.
- Opmaak: `css/site.css`. Interactie (menu's, plakbalk): `js/site.js`. Lettertypen staan in `fonts/` (Inter en League Spartan, OFL).
- Foto's voor de site staan in `img/` en worden gemaakt uit de originelen in `Assets/` met `_bron/afbeeldingen.py`.

## Na elke wijziging

```
pip install jinja2 pillow   # eenmalig
python3 _bron/bouw.py       # bouwt alle pagina's en sitemap.xml opnieuw
```

Alleen bij nieuwe of andere foto's: `python3 _bron/afbeeldingen.py`.

Een nieuwe pagina: maak `_bron/paginas/<naam>.html` (kopieer een bestaande dienstpagina), voeg hem toe aan `PAGINAS` in `bouw.py` en, als het een dienst is, aan `DIENSTEN`.

## Afspraken voor teksten

- Spreek bezoekers aan met **u**. Schrijf in de ik-vorm (Maurits).
- Pagina's zijn ingedeeld per soort apparaat. Klachten staan als herkenbare klantzinnen in de koppen ("Mijn Senseo lekt water onderdoor").
- Beloof niet meer dan klopt: het onderzoek is gratis en kost niets als repareren niet lukt; de reparatie zelf wordt betaald na akkoord op een vaste prijs. 3 maanden garantie op arbeid, onderdelen volgen de garantie van de leverancier. Geen btw (KOR).
- Niet in het aanbod: telefoons, magnetrons, soldeerwerk (laadpoorten, sticks van PlayStation- en Xbox-controllers).
- Geen woon- of werkadres van Maurits op de site. Het enige adres is het inleverpunt (The Social Hub, alleen op afspraak).

## Beweging

Animaties volgen de web-animation-design-richtlijnen: alleen `transform` en `opacity`, ease-out voor in- en uitkomen, ease-in-out voor beweging op het scherm, hover-effecten alleen bij `(hover: hover) and (pointer: fine)`, en alles uit bij `prefers-reduced-motion`. Het enige grote moment is het reparatielabel in de hero dat aan het snoer in beeld zwaait.
