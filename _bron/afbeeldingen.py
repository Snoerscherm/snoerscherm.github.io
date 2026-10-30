"""Maakt de webversies van de foto's en logo's in img/ uit de originelen in Assets/.

Gebruik: python3 _bron/afbeeldingen.py

Alleen opnieuw draaien als er een foto bijkomt of verandert. De originelen in
Assets/ blijven onaangeraakt; de site laadt alleen de bestanden uit img/.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRON = ROOT / "Assets"
DOEL = ROOT / "img"

# naam: (bronbestand, crop (links, boven, rechts, onder) of None, breedtes)
FOTO_S = {
    "maurits-werkplek": ("Hero_Image.png", None, (560, 840, 1200)),
    "maurits-portret": ("Profile Picture.jpeg", None, (400, 720)),
    "maurits-aan-huis": ("Reparatie-aan-huis-Delft-SnoerScherm.jpg", None, (560, 824)),
    "werkplaats": ("Werkplaats-Reparatie-Delfgauw-SnoerScherm.png", (0, 380, 1536, 2300), (480, 800)),
    "koffiemachine-onderdelen": ("Koffiezetapparaat-reparatie-Delft-SnoerScherm.png", (0, 300, 1696, 2420), (480, 800)),
    "laptop-open": ("Gemini_Generated_Image_osb5cgosb5cgosb5.png", (0, 1273, 1696, 2528), (560, 960)),
    "pc-onderdelen": ("Computer-reparatie-Delfgauw-SnoerScherm.png", (0, 150, 848, 1210), (480, 800)),
}


def rgb(im):
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.convert("RGB")
    return im.convert("RGB")


def foto_s():
    for naam, (bestand, crop, breedtes) in FOTO_S.items():
        im = rgb(Image.open(BRON / bestand))
        if crop:
            im = im.crop(crop)
        for b in breedtes:
            h = round(im.height * b / im.width)
            uit = im.resize((b, h), Image.LANCZOS)
            uit.save(DOEL / f"{naam}-{b}.webp", "WEBP", quality=74, method=6)
        print(naam, im.size, "->", breedtes)

    # Deelafbeelding voor WhatsApp, Facebook en LinkedIn (1200x630)
    im = rgb(Image.open(BRON / "Hero_Image.png"))
    w, h = im.size
    doel_h = round(w * 630 / 1200)
    top = round((h - doel_h) * 0.35)
    im.crop((0, top, w, top + doel_h)).resize((1200, 630), Image.LANCZOS).save(
        DOEL / "snoer-en-scherm-delen.jpg", "JPEG", quality=82, optimize=True, progressive=True
    )


def transparant(im, drempel=236):
    """Witte achtergrond van het lange logo doorzichtig maken."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            licht = min(r, g, b)
            if licht >= drempel:
                px[x, y] = (r, g, b, 0)
            elif licht > 200 and abs(r - g) < 12 and abs(g - b) < 12:
                # zachte rand rond zwarte letters
                alpha = round(255 * (drempel - licht) / (drempel - 200))
                px[x, y] = (0, 0, 0, alpha)
    return im.crop(im.getbbox())


def logo_s():
    lang = transparant(Image.open(BRON / "Logo_Long.png"))
    h = 96
    w = round(lang.width * h / lang.height)
    lang = lang.resize((w, h), Image.LANCZOS)
    lang.save(DOEL / "logo-snoer-en-scherm.png", optimize=True)

    # Versie voor de zwarte footer: zwart wordt gebroken wit, geel blijft geel
    licht = lang.copy()
    px = licht.load()
    for y in range(licht.height):
        for x in range(licht.width):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) < 90:
                px[x, y] = (246, 246, 246, a)
    licht.save(DOEL / "logo-snoer-en-scherm-licht.png", optimize=True)
    print("logo", lang.size)

    icoon = Image.open(BRON / "Logo Only.png").convert("RGBA")
    icoon = icoon.crop(icoon.getbbox())
    zijde = max(icoon.size)
    vierkant = Image.new("RGBA", (zijde, zijde), (0, 0, 0, 0))
    vierkant.alpha_composite(icoon, ((zijde - icoon.width) // 2, (zijde - icoon.height) // 2))

    vierkant.resize((48, 48), Image.LANCZOS).save(DOEL / "favicon-48.png", optimize=True)
    vierkant.resize((192, 192), Image.LANCZOS).save(DOEL / "icoon-192.png", optimize=True)
    vierkant.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    rand = round(zijde * 0.18)
    apple = Image.new("RGBA", (zijde + 2 * rand, zijde + 2 * rand), (255, 196, 29, 255))
    apple.alpha_composite(vierkant, (rand, rand))
    apple.convert("RGB").resize((180, 180), Image.LANCZOS).save(DOEL / "apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    DOEL.mkdir(exist_ok=True)
    foto_s()
    logo_s()
