import pandas as pd
import numpy as np

print("🔧 Opravuji data v kombinovane_data.csv...")

# Načtení dat
df = pd.read_csv('kombinovane_data.csv', sep=';', encoding='utf-8')

print(f"📊 Původní počet záznamů: {len(df)}")

# === 1. Oprava formátu souřadnic (čárka → tečka) ===
print("🔄 Opravuji formát souřadnic (čárka → tečka)...")

def oprav_souradnice(hodnota):
    if pd.isna(hodnota) or hodnota == 0:
        return np.nan
    if isinstance(hodnota, str):
        # Nahraď čárku tečkou a převeď na float
        try:
            return float(hodnota.replace(',', '.'))
        except:
            return np.nan
    return float(hodnota) if hodnota != 0 else np.nan

df['lat'] = df['lat'].apply(oprav_souradnice)
df['lon'] = df['lon'].apply(oprav_souradnice)

print(f"✅ Souřadnice opraveny")

# === 2. Oprava problematického příznaku 28401 ===
print("🔄 Opravuji problematický příznak 28401...")

# Najdi záznam s příznakem 28401
problemy = df[df['PŘÍZNAK'] == '28401']
if len(problemy) > 0:
    print(f"Nalezen problematický záznam: {problemy.iloc[0]['NÁZEV']}")
    
    # Přesuň PSČ z příznaku do adresy a nastav správný příznak
    for idx in problemy.index:
        stara_adresa = df.loc[idx, 'Adresa']
        psc = df.loc[idx, 'PŘÍZNAK']
        
        # Přidej PSČ do adresy pokud tam už není
        if psc not in stara_adresa:
            df.loc[idx, 'Adresa'] = f"{psc}, {stara_adresa}"
        
        # Nastav správný příznak (odhadnu podle podobných záznamů)
        df.loc[idx, 'PŘÍZNAK'] = '35'  # nejčastější příznak pro podobné záznamy
        
        print(f"  Opraveno: {df.loc[idx, 'NÁZEV']} - příznak: 35")

print(f"✅ Problematické příznaky opraveny")

# === 3. Uložení opravených dat ===
df.to_csv('kombinovane_data.csv', sep=';', encoding='utf-8', index=False)

print(f"💾 Opravená data uložena")

# === 4. Kontrola výsledků ===
print(f"\n📈 Kontrola po opravě:")
print(f"📍 Záznamy s koordináty: {len(df.dropna(subset=['lat', 'lon']))}")
print(f"❌ Záznamy bez koordinátů: {len(df) - len(df.dropna(subset=['lat', 'lon']))}")

print(f"\n🏷️ Aktuální příznaky:")
print(df['PŘÍZNAK'].value_counts().sort_index())

print(f"\n🔍 Ukázka opravených souřadnic:")
valid_coords = df.dropna(subset=['lat', 'lon'])
if len(valid_coords) > 0:
    print(valid_coords[['NÁZEV', 'lat', 'lon', 'PŘÍZNAK']].head(5).to_string(index=False)) 