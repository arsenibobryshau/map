import pandas as pd

print("🔍 DETAILNÍ ANALÝZA NENALEZENÝCH ADRES")
print("=" * 50)

# Načtení dat
df = pd.read_csv('kombinovane_data.csv', sep=';', encoding='utf-8')

# Nenalezené adresy
nenalezeno = df[df['lat'].isna() | df['lon'].isna()]

print(f"📊 Celkem záznamů: {len(df)}")
print(f"📍 Záznamy s koordináty: {len(df.dropna(subset=['lat', 'lon']))}")
print(f"❌ Záznamy bez koordinátů: {len(nenalezeno)}")
print(f"📈 Úspěšnost: {((len(df)-len(nenalezeno))/len(df)*100):.1f}%")

print(f"\n🏷️ Nenalezené podle příznaků:")
print(nenalezeno['PŘÍZNAK'].value_counts().sort_index())

print(f"\n❓ MOŽNÉ PŘÍČINY PROBLÉMŮ:")

# Analýza typických problémů
problemy = {
    "Prázdná adresa": 0,
    "Pouze PSČ": 0,
    "Neúplná adresa": 0,
    "Speciální znaky": 0,
    "Překlepy": 0,
    "Zahraniční adresy": 0
}

print(f"\n📝 SEZNAM VŠECH NENALEZENÝCH ADRES:")
print("-" * 50)

for i, (idx, row) in enumerate(nenalezeno.iterrows(), 1):
    adresa = str(row['Adresa']).strip()
    
    # Kategorizace problémů
    if not adresa or adresa == 'nan':
        problemy["Prázdná adresa"] += 1
        problem = "❌ PRÁZDNÁ"
    elif len(adresa.split(',')) == 2 and adresa.split(',')[0].strip().isdigit():
        problemy["Pouze PSČ"] += 1
        problem = "📮 JEN PSČ"
    elif any(znak in adresa for znak in ['(', ')', 'areál', 'vjezd']):
        problemy["Speciální znaky"] += 1
        problem = "🏢 SLOŽITÁ"
    elif any(mesto in adresa.upper() for mesto in ['SLOVAKIA', 'MYJAVA', 'PÚCHOV', 'HLOHOVEC']):
        problemy["Zahraniční adresy"] += 1
        problem = "🌍 SLOVENSKO"
    elif len(adresa.split(',')) < 2:
        problemy["Neúplná adresa"] += 1
        problem = "⚠️ NEÚPLNÁ"
    else:
        problemy["Překlepy"] += 1
        problem = "🔤 PŘEKLEP?"
    
    print(f"{i:3d}. {problem} | {row['NÁZEV'][:40]:40s} | {adresa}")

print(f"\n📊 SHRNUTÍ PROBLÉMŮ:")
for problem, pocet in problemy.items():
    if pocet > 0:
        print(f"  {problem}: {pocet} adres")

print(f"\n💡 DOPORUČENÍ PRO ZLEPŠENÍ:")
print("1. 🌍 Slovenské adresy - potřeba jiný geokódovací servis")
print("2. 🏢 Složité adresy - zjednodušit formát (odstranit 'areál', závorky)")
print("3. ⚠️ Neúplné adresy - doplnit chybějící informace")
print("4. 📮 Pouze PSČ - doplnit ulici a číslo popisné")
print("5. 🔤 Překlepy - ručně opravit nejčastější chyby")

print(f"\n🎯 S těmito opravami by se dalo dostat na 99%+ úspěšnost!") 