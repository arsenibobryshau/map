import pandas as pd 
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import os
import re
import requests
import json

# === 1. Nastavení ===
CSV_SOUBOR = "gpt.csv"              # Název tvého CSV souboru
ODDELENI = ";"                      # Oddělovač ve tvém souboru
KODOVANI = "cp1250"                 # Kódování souboru (Windows-1250 pro češtinu)
MAPA_SOUBOR = "interaktivni_mapa.html"  # Výstupní soubor mapy
CACHE_SOUBOR = "geocode_cache.csv"      # Soubor pro cache

# === 2. Načtení dat ===
df = pd.read_csv(CSV_SOUBOR, encoding=KODOVANI, sep=ODDELENI)
df = df[['NÁZEV', 'Adresa', 'PŘÍZNAK']].dropna()


# === 2a. Načtení cache ===
if os.path.exists(CACHE_SOUBOR):
    cache_df = pd.read_csv(CACHE_SOUBOR, encoding="utf-8")
else:
    cache_df = pd.DataFrame(columns=["Adresa", "lat", "lon"])

cache = dict()
for _, row in cache_df.iterrows():
    cache[row["Adresa"]] = (row["lat"], row["lon"])

# === 3. Geokódování adres s cache a retry ===
geolocator = Nominatim(user_agent="mapa_adres")

# Počítadlo pro průběžné ukládání
ulozeno_od_posledniho = 0
celkem = len(df)

# === Pomocná funkce pro uložení cache ===
def uloz_cache():
    cache_df = pd.DataFrame([
        {"Adresa": adresa, "lat": lat, "lon": lon}
        for adresa, (lat, lon) in cache.items()
    ])
    cache_df.to_csv(CACHE_SOUBOR, index=False, encoding="utf-8")

def geocode_with_cache(adresa, idx=None):
    global ulozeno_od_posledniho
    if adresa in cache:
        lat, lon = cache[adresa]
        if pd.isna(lat) or pd.isna(lon):
            return None
        return (lat, lon)
    # Pokud není v cache, zkusíme až 5x
    for attempt in range(5):
        try:
            location = geolocator.geocode(adresa, timeout=10)
            if location:
                cache[adresa] = (location.latitude, location.longitude)
                ulozeno_od_posledniho += 1
                if ulozeno_od_posledniho >= 100:
                    uloz_cache()
                    ulozeno_od_posledniho = 0
                    if idx is not None:
                        print(f"Zbývá zpracovat: {celkem - idx - 1}")
                return (location.latitude, location.longitude)
            else:
                time.sleep(2)  # počkej 2 sekundy a zkus znovu
        except Exception as e:
            print(f"Chyba při geokódování '{adresa}': {e}, pokus {attempt+1}/5")
            time.sleep(5)  # počkej 5 sekund a zkus znovu
    # Pokud se nepodaří ani po 5 pokusech, zkusíme PSČ
    psc_match = re.search(r"(\d{5})", adresa)
    if psc_match:
        psc = psc_match.group(1)
        # Rozlišení států podle PSČ
        if psc.startswith('8') or psc.startswith('9'):
            stat = "Slovensko"
        else:
            stat = "Česká republika"
        psc_adresa = f"{psc} {stat}"
        for attempt in range(3):
            try:
                location = geolocator.geocode(psc_adresa, timeout=10)
                if location:
                    cache[adresa] = (location.latitude, location.longitude)
                    ulozeno_od_posledniho += 1
                    if ulozeno_od_posledniho >= 100:
                        uloz_cache()
                        ulozeno_od_posledniho = 0
                        if idx is not None:
                            print(f"Zbývá zpracovat: {celkem - idx - 1}")
                    return (location.latitude, location.longitude)
                else:
                    time.sleep(2)
            except Exception as e:
                print(f"Chyba při geokódování PSČ '{psc_adresa}': {e}, pokus {attempt+1}/3")
                time.sleep(5)
        # Pokud selže i PSČ, zkusíme ještě město+PSČ+stát
        # Pokusíme se vytáhnout město z adresy (část za čárkou, kde je PSČ a město)
        mesto_match = re.search(r"\d{5}\s*([\w\s\-\.]+)", adresa)
        if mesto_match:
            mesto = mesto_match.group(1).strip()
            mesto_psc_adresa = f"{mesto}, {psc}, {stat}"
            for attempt in range(2):
                try:
                    location = geolocator.geocode(mesto_psc_adresa, timeout=10)
                    if location:
                        cache[adresa] = (location.latitude, location.longitude)
                        ulozeno_od_posledniho += 1
                        if ulozeno_od_posledniho >= 100:
                            uloz_cache()
                            ulozeno_od_posledniho = 0
                            if idx is not None:
                                print(f"Zbývá zpracovat: {celkem - idx - 1}")
                        return (location.latitude, location.longitude)
                    else:
                        time.sleep(2)
                except Exception as e:
                    print(f"Chyba při geokódování město+PSČ '{mesto_psc_adresa}': {e}, pokus {attempt+1}/2")
                    time.sleep(5)
    # Pokud se nepodaří ani to, uložíme None
    cache[adresa] = (None, None)
    ulozeno_od_posledniho += 1
    if ulozeno_od_posledniho >= 100:
        uloz_cache()
        ulozeno_od_posledniho = 0
        if idx is not None:
            print(f"Zbývá zpracovat: {celkem - idx - 1}")
    return None

# === Hlavní volání s indexem pro výpis průběhu ===
coords = [geocode_with_cache(adresa, idx) for idx, adresa in enumerate(df["Adresa"])]
df["lat"] = [x[0] if x else None for x in coords]
df["lon"] = [x[1] if x else None for x in coords]

# === 3a. Uložení cache ===
uloz_cache()

df = df.dropna(subset=["lat", "lon"])

# === 4. Vytvoření mapy ===
m = folium.Map(location=[49.8, 15.5], zoom_start=7)
marker_cluster = MarkerCluster().add_to(m)

def barva_priznaku(priznak):
    try:
        p = int(priznak)
        if p < 50:
            return "green"
        elif p < 150:
            return "orange"
        else:
            return "red"
    except:
        return "gray"

for _, row in df.iterrows():
    priznak = str(row["PŘÍZNAK"])
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=row["NÁZEV"],
        icon=folium.Icon(color=barva_priznaku(row["PŘÍZNAK"])),
        tooltip=f"PŘÍZNAK: {priznak}",
    ).add_to(marker_cluster)

# === 5. Uložení ===
m.save(MAPA_SOUBOR)
print(f"Mapa uložena jako: {MAPA_SOUBOR}")

# === 6. Přidání filtru do HTML ===
# Získáme unikátní hodnoty PŘÍZNAK
priznaky = sorted(df["PŘÍZNAK"].astype(str).unique())

# Vložíme filtr do HTML
with open(MAPA_SOUBOR, "r", encoding="utf-8") as f:
    html = f.read()

# Vytvoříme select box a JS skript
options_html = '\n'.join([f'<option value="{p}">{p}</option>' for p in priznaky])
select_html = (
    '<div id="priznak-filter" style="position: fixed; top: 10px; left: 50px; z-index: 9999; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 8px #888;">\n'
    '  <label for="priznak-select"><b>Filtr PŘÍZNAK:</b></label><br>\n'
    f'  <select id="priznak-select" multiple size="{min(8, len(priznaky))}" style="width: 120px;">\n'
    f'    {options_html}\n'
    '  </select>\n'
    '  <button onclick="selectAllPriznaky()">Vše</button>\n'
    '  <button onclick="deselectAllPriznaky()">Žádný</button>\n'
    '</div>\n'
    '<script>\n'
    'function updateMarkers() {\n'
    '  var select = document.getElementById("priznak-select");\n'
    '  var selected = Array.from(select.selectedOptions).map(o => o.value);\n'
    '  var allMarkers = document.querySelectorAll(".leaflet-marker-icon");\n'
    '  allMarkers.forEach(function(marker) {\n'
    '    var priznak = marker.getAttribute("data-priznak");\n'
    '    if (!priznak) { marker.style.display = "block"; return; }\n'
    '    if (selected.includes(priznak)) {\n'
    '      marker.style.display = "block";\n'
    '    } else {\n'
    '      marker.style.display = "none";\n'
    '    }\n'
    '  });\n'
    '}\n'
    'document.getElementById("priznak-select").addEventListener("change", updateMarkers);\n'
    'function selectAllPriznaky() {\n'
    '  var select = document.getElementById("priznak-select");\n'
    '  for (var i = 0; i < select.options.length; i++) {\n'
    '    select.options[i].selected = true;\n'
    '  }\n'
    '  updateMarkers();\n'
    '}\n'
    'function deselectAllPriznaky() {\n'
    '  var select = document.getElementById("priznak-select");\n'
    '  for (var i = 0; i < select.options.length; i++) {\n'
    '    select.options[i].selected = false;\n'
    '  }\n'
    '  updateMarkers();\n'
    '}\n'
    '// Po načtení stránky vyber vše s malým zpožděním\n'
    'window.onload = function() { setTimeout(selectAllPriznaky, 500); };\n'
    '</script>\n'
)

# Vložíme filtr těsně za <body>
html = html.replace('<body>', '<body>' + select_html)

# === Oprava: Přidání data-priznak atributu markerům ===
def add_data_priznak(html, priznaky):
    # Najdi všechny markery a přidej jim data-priznak podle tooltipu
    def replacer(match):
        tag = match.group(0)
        priznak = None
        title_match = re.search(r'PŘÍZNAK: (\\d+)', tag)
        if title_match:
            priznak = title_match.group(1)
        else:
            title_match = re.search(r'title=\"(\\d+)\"', tag)
            if title_match:
                priznak = title_match.group(1)
        if priznak:
            # Přidej data-priznak
            if 'data-priznak' not in tag:
                return tag.replace('class="leaflet-marker-icon', f'data-priznak="{priznak}" class="leaflet-marker-icon')
        return tag
    # Nahraď <div> i <img> s třídou leaflet-marker-icon
    html = re.sub(r'<div([^>]+class="leaflet-marker-icon[^"]*"[^>]*)>', replacer, html)
    html = re.sub(r'<img([^>]+class="leaflet-marker-icon[^"]*"[^>]*)>', replacer, html)
    return html

html = add_data_priznak(html, priznaky)

with open(MAPA_SOUBOR, "w", encoding="utf-8") as f:
    f.write(html)

# === 7. Přidání seznamu nenalezených adres ===
# Najdeme adresy, které se nepodařilo geokódovat
nenalezeno_df = df[df[["lat", "lon"]].isnull().any(axis=1)]
nenalezeno_adresy = nenalezeno_df["Adresa"].tolist()

if nenalezeno_adresy:
    seznam_html = '<div style="max-width:600px;margin:30px auto 30px auto;padding:15px;background:#fffbe6;border:1px solid #e0c97f;border-radius:8px;">'
    seznam_html += '<b>Adresy, které se nepodařilo najít:</b><ul>'
    for adresa in nenalezeno_adresy:
        seznam_html += f'<li>{adresa}</li>'
    seznam_html += '</ul></div>'
    with open(MAPA_SOUBOR, "a", encoding="utf-8") as f:
        f.write(seznam_html)

print("🌍 GEOKÓDOVÁNÍ CHYBĚJÍCÍCH ADRES")
print("=" * 40)

# Načtení dat
df = pd.read_csv('kombinovane_data.csv', sep=';')
cache = pd.read_csv('geocode_cache.csv')

# Najdi adresy s nulovými souřadnicemi
chybejici = df[(df['lat'] == 0.0) | (df['lon'] == 0.0)].copy()
print(f"📊 Chybějících adres: {len(chybejici)}")

# Nejdřív zkus cache
print(f"🔍 Hledám v cache...")
nove_adresy = []

for idx, row in chybejici.iterrows():
    adresa = row['Adresa']
    
    # Hledej v cache (různé varianty)
    cache_match = cache[
        (cache['Adresa'].str.contains(adresa.split(',')[0], case=False, na=False)) |
        (cache['Adresa'].str.upper().str.strip() == adresa.upper().strip())
    ]
    
    if len(cache_match) > 0 and not pd.isna(cache_match.iloc[0]['lat']):
        lat = cache_match.iloc[0]['lat']
        lon = cache_match.iloc[0]['lon']
        print(f"✅ Cache: {adresa[:50]}... → {lat}, {lon}")
        nove_adresy.append({
            'NÁZEV': row['NÁZEV'],
            'Adresa': adresa,
            'PŘÍZNAK': row['PŘÍZNAK'],
            'lat': lat,
            'lon': lon,
            'zdroj': 'cache'
        })
    else:
        # Přidej do seznamu pro geokódování
        nove_adresy.append({
            'NÁZEV': row['NÁZEV'],
            'Adresa': adresa,
            'PŘÍZNAK': row['PŘÍZNAK'],
            'lat': 0.0,
            'lon': 0.0,
            'zdroj': 'chybí'
        })

cache_uspech = len([a for a in nove_adresy if a['zdroj'] == 'cache'])
print(f"🎯 Z cache nalezeno: {cache_uspech} adres")

# Ulož výsledky
nove_df = pd.DataFrame(nove_adresy)
nove_df.to_csv('nove_adresy.csv', sep=';', index=False, encoding='utf-8')

print(f"💾 Uloženo do 'nove_adresy.csv'")
print(f"📈 Možné zlepšení o {cache_uspech} adres")

# Statistiky chybějících podle příznaků
chybi_stale = nove_df[nove_df['zdroj'] == 'chybí']
print(f"\n📊 Zbývá dořešit {len(chybi_stale)} adres podle příznaků:")
print(chybi_stale['PŘÍZNAK'].value_counts().sort_index())

print(f"\n💡 DOPORUČENÍ:")
print(f"1. Zkontroluj 'nove_adresy.csv' - jsou tam adresy z cache")
print(f"2. Pro zbývající adresy můžeme použít online geokódování")
print(f"3. Nebo upravit ručně nejčastější překleply")
