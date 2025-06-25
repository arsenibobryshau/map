import pandas as pd
import re

# Načtení dat
print("Načítám data...")
kombinovane_df = pd.read_csv('kombinovane_data.csv', sep=';', encoding='utf-8')
dodav_df = pd.read_csv('dodav_map.csv', sep=';', encoding='utf-8')

print(f"Kombinovane data: {len(kombinovane_df)} řádků")
print(f"Dodav map: {len(dodav_df)} řádků")

# Přidání sloupce CF do kombinovaných dat
print("\nPřidávám sloupec CF...")
kombinovane_df['CF'] = None

# Spojení podle názvu firmy
for idx, row in kombinovane_df.iterrows():
    nazev = row['NÁZEV']
    
    # Hledej v dodav_map.csv podle názvu firmy
    match = dodav_df[dodav_df['FIRMA'] == nazev]
    
    if len(match) > 0:
        cf_value = match.iloc[0]['CF']
        kombinovane_df.at[idx, 'CF'] = cf_value
        print(f"✅ Nalezen CF pro {nazev[:50]}...: {cf_value}")

# Oprava PSČ v adresách (odstranění .0)
print("\nOpravuji PSČ v adresách...")
for idx, row in kombinovane_df.iterrows():
    adresa = row['Adresa']
    
    # Najdi PSČ s .0 a oprav je
    # Vzorec: číslo, tečka, nula, čárka nebo konec řetězce
    opravena_adresa = re.sub(r'(\d{5})\.0(?=,|$)', r'\1', adresa)
    
    if opravena_adresa != adresa:
        kombinovane_df.at[idx, 'Adresa'] = opravena_adresa
        print(f"🔧 Opraveno PSČ: {adresa} → {opravena_adresa}")

# Uložení aktualizovaných dat
print("\nUkládám aktualizovaná data...")
kombinovane_df.to_csv('kombinovane_data_aktualizovane.csv', sep=';', index=False, encoding='utf-8')

# Statistiky
cf_ma = kombinovane_df['CF'].notna().sum()
print(f"\n📊 Statistiky:")
print(f"Firem s CF: {cf_ma} z {len(kombinovane_df)} ({cf_ma/len(kombinovane_df)*100:.1f}%)")

print(f"\n✅ Data uložena do 'kombinovane_data_aktualizovane.csv'")
print(f"💡 Nyní můžete spustit aktualizovaný skript pro generování mapy") 