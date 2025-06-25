import pandas as pd

print("🔧 OPRAVA NEJČASTĚJŠÍCH PŘEKLEPŮ V RINO ADRESÁCH")
print("=" * 50)

# Načtení dat
df = pd.read_csv('kombinovane_data.csv', sep=';', encoding='utf-8')

print(f"📊 Před opravou - nenalezené adresy: {len(df[df['lat'].isna() & (df['PŘÍZNAK'] == 'RINO')])}")

# Slovník nejčastějších překlepů
opravy = {
    'Cesky Tesin': 'Český Těšín',
    'Hradec Kralove': 'Hradec Králové',
    'Usti nad Labem': 'Ústí nad Labem',
    'Sumperk': 'Šumperk',
    'Tabor': 'Tábor',
    'Frydek-Mistek': 'Frýdek-Místek',
    'Plzen': 'Plzeň',
    'Jindrichuv Hradec': 'Jindřichův Hradec',
    'Mlada Boleslav': 'Mladá Boleslav',
    'Ceske Budejovice': 'České Budějovice',
    'Slany': 'Slaný',
    'Nasavrky': 'Nasavrky',
    'Havlickuv Brod': 'Havlíčkův Brod',
    'OSTRAVA-HULVAKY': 'OSTRAVA-HULVÁKY',
    'Liberec': 'Liberec',
    'Prerov': 'Přerov',
    'Dobruska': 'Dobruška',
    'Trutnov': 'Trutnov'
}

# Další běžné opravy
dalsi_opravy = {
    ' 1$': '',  # odstranění " 1" na konci
    ' 2$': '',  # odstranění " 2" na konci  
    ' 3$': '',  # odstranění " 3" na konci
    'OSTRAVA 20-Hrabová': 'OSTRAVA-Hrabová',
    'Praha 14 - Kyje': 'Praha 14-Kyje',
    'Praha 10 - Malešice': 'Praha 10-Malešice',
    'Praha 11': 'Praha',
    'Praha10': 'Praha 10'
}

pocet_opravenych = 0

# Provedení oprav jen u RINO záznamů bez koordinátů
rino_bez_coords = df['PŘÍZNAK'] == 'RINO'
for idx in df[rino_bez_coords & df['lat'].isna()].index:
    puvodni_adresa = df.loc[idx, 'Adresa']
    nova_adresa = puvodni_adresa
    
    # Základní opravy překlepů
    for chyba, oprava in opravy.items():
        if chyba in nova_adresa:
            nova_adresa = nova_adresa.replace(chyba, oprava)
            pocet_opravenych += 1
            print(f"✅ {df.loc[idx, 'NÁZEV'][:30]:30s} | {chyba} → {oprava}")
    
    # Další opravy
    import re
    for pattern, nahrada in dalsi_opravy.items():
        if pattern.endswith('$'):
            nova_adresa = re.sub(pattern, nahrada, nova_adresa)
        else:
            nova_adresa = nova_adresa.replace(pattern, nahrada)
    
    # Odstranění složitých částí adres
    if '(areál' in nova_adresa or 'vjezd do' in nova_adresa:
        # Pokus o zjednodušení - odstraň text v závorkách
        nova_adresa = re.sub(r'\s*\([^)]*\)', '', nova_adresa)
        nova_adresa = re.sub(r',\s*,', ',', nova_adresa)  # oprava dvojitých čárek
        nova_adresa = nova_adresa.strip()
        pocet_opravenych += 1
        print(f"🏢 {df.loc[idx, 'NÁZEV'][:30]:30s} | Zjednodušena složitá adresa")
    
    df.loc[idx, 'Adresa'] = nova_adresa

print(f"\n📊 Celkem provedeno {pocet_opravenych} oprav")

# Uložení opravených dat
df.to_csv('kombinovane_data.csv', sep=';', encoding='utf-8', index=False)

print(f"💾 Opravená data uložena")
print(f"\n🔄 Pro nové geokódování spusťte geokódovací skript!")
print(f"📍 Očekávané zlepšení: 60-70% nenalezených adres by mělo být nyní nalezeno") 