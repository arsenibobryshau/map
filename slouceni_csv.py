import pandas as pd
import numpy as np

print("🔄 Načítám CSV soubory...")

# === 1. Načtení dodav_map.csv ===
print("📊 Zpracovávám dodav_map.csv...")
# Zkusíme různá kódování
try:
    dodav = pd.read_csv("dodav_map.csv", encoding="utf-8", sep=";")
    print("✅ Použito kódování: utf-8")
except UnicodeDecodeError:
    try:
        dodav = pd.read_csv("dodav_map.csv", encoding="cp1250", sep=";")
        print("✅ Použito kódování: cp1250")
    except UnicodeDecodeError:
        try:
            dodav = pd.read_csv("dodav_map.csv", encoding="iso-8859-2", sep=";")
            print("✅ Použito kódování: iso-8859-2")
        except UnicodeDecodeError:
            dodav = pd.read_csv("dodav_map.csv", encoding="latin-1", sep=";")
            print("✅ Použito kódování: latin-1")

# Převod na standardní formát
dodav_standard = pd.DataFrame()
dodav_standard["NÁZEV"] = dodav["FIRMA"]
dodav_standard["PŘÍZNAK"] = dodav["PŘÍZNAK"].astype(str)

# Sestavení adresy z ULICE, MESTO, PSC
dodav_standard["Adresa"] = ""
for i, row in dodav.iterrows():
    adresa_casti = []
    if pd.notna(row["ULICE"]) and str(row["ULICE"]).strip():
        adresa_casti.append(str(row["ULICE"]).strip())
    if pd.notna(row["PSC"]) and str(row["PSC"]).strip():
        adresa_casti.append(str(row["PSC"]).strip())
    if pd.notna(row["MESTO"]) and str(row["MESTO"]).strip():
        adresa_casti.append(str(row["MESTO"]).strip())
    
    dodav_standard.loc[i, "Adresa"] = ", ".join(adresa_casti)

# Převod zeměpisných souřadnic (pozor na prázdné hodnoty)
dodav_standard["Latitude"] = dodav["ZEMSIRKA"]
dodav_standard["Longitude"] = dodav["ZEMDELKA"]

# Nahrazení nulových souřadnic prázdnými hodnotami
dodav_standard.loc[dodav_standard["Latitude"] == 0, "Latitude"] = np.nan
dodav_standard.loc[dodav_standard["Longitude"] == 0, "Longitude"] = np.nan

print(f"✅ dodav_map.csv: {len(dodav_standard)} záznamů zpracováno")

# === 2. Načtení jenom_rino_geocoded.csv ===
print("📊 Zpracovávám jenom_rino_geocoded.csv...")
rino = pd.read_csv("jenom_rino_geocoded.csv", encoding="utf-8", sep=";")

# Už má správnou strukturu, jen zkontrolujeme sloupce
rino_standard = rino[["NÁZEV", "Adresa", "PŘÍZNAK", "Latitude", "Longitude"]].copy()

# Převod prázdných souřadnic na NaN
rino_standard["Latitude"] = pd.to_numeric(rino_standard["Latitude"], errors='coerce')
rino_standard["Longitude"] = pd.to_numeric(rino_standard["Longitude"], errors='coerce')

print(f"✅ jenom_rino_geocoded.csv: {len(rino_standard)} záznamů zpracováno")

# === 3. Sloučení obou dataframů ===
print("🔗 Slučuji oba soubory...")
kombinovany = pd.concat([dodav_standard, rino_standard], ignore_index=True)

# === 4. Převod souřadnic na správný formát ===
kombinovany["lat"] = kombinovany["Latitude"]
kombinovany["lon"] = kombinovany["Longitude"]

# Ponechání pouze potřebných sloupců
final = kombinovany[["NÁZEV", "Adresa", "PŘÍZNAK", "lat", "lon"]].copy()

# === 5. Uložení sloučeného souboru ===
output_file = "kombinovane_data.csv"
final.to_csv(output_file, encoding="utf-8", sep=";", index=False)

print(f"💾 Sloučený soubor uložen jako: {output_file}")
print(f"📊 Celkem záznamů: {len(final)}")

# === 6. Statistiky ===
print("\n📈 Statistiky:")
print(f"- Záznamy s koordináty: {len(final.dropna(subset=['lat', 'lon']))}")
print(f"- Záznamy bez koordinátů: {len(final) - len(final.dropna(subset=['lat', 'lon']))}")
print(f"- Různé příznaky: {sorted(final['PŘÍZNAK'].unique())}")

# Ukázka prvních řádků
print("\n🔍 Ukázka výsledku:")
print(final.head(10).to_string(index=False)) 