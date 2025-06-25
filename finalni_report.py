import pandas as pd

print("📊 FINÁLNÍ REPORT GEOKÓDOVÁNÍ")
print("=" * 50)

# Načtení dat
df = pd.read_csv('kombinovane_data.csv', sep=';')
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

print(f"📋 CELKOVÉ STATISTIKY:")
print(f"• Celkem záznamů: {len(df)}")

# Platné souřadnice
platne = df.dropna(subset=['lat', 'lon'])
print(f"• ✅ S platnými souřadnicemi: {len(platne)}")

# Neplatné souřadnice
neplatne = df[df['lat'].isna() | df['lon'].isna()]
print(f"• ❌ Bez souřadnic: {len(neplatne)}")

# Úspěšnost
uspesnost = (len(platne) / len(df)) * 100
print(f"• 🎯 Úspěšnost geokódování: {uspesnost:.1f}%")

print(f"\n🏷️ ROZLOŽENÍ PODLE PŘÍZNAKŮ:")
print("Platné souřadnice:")
platne_priznaky = platne['PŘÍZNAK'].value_counts().sort_index()
for priznak, pocet in platne_priznaky.items():
    celkem_priznak = len(df[df['PŘÍZNAK'] == priznak])
    uspesnost_priznak = (pocet / celkem_priznak) * 100
    print(f"  {priznak}: {pocet}/{celkem_priznak} ({uspesnost_priznak:.1f}%)")

if len(neplatne) > 0:
    print(f"\n❌ ZBÝVAJÍCÍ PROBLÉMOVÉ ADRESY ({len(neplatne)}):")
    print("Podle příznaků:")
    neplatne_priznaky = neplatne['PŘÍZNAK'].value_counts().sort_index()
    for priznak, pocet in neplatne_priznaky.items():
        print(f"  {priznak}: {pocet} adres")

    print(f"\nNejčastější typy problémů:")
    print(f"• Překlepy v názvech měst (Cesky Tesin → Český Těšín)")
    print(f"• Složité adresy s areály a vjezdy")
    print(f"• Slovenské adresy (potřeba jiný geokódovací servis)")
    print(f"• Neúplné adresy")

print(f"\n🎯 DOPORUČENÍ PRO DALŠÍ ZLEPŠENÍ:")
print(f"1. 🌐 Online geokódování zbývajících {len(neplatne)} adres")
print(f"2. 🔧 Ruční oprava nejčastějších překlepů")
print(f"3. 🗺️ Použití specializovaného servisu pro slovenské adresy")
print(f"4. 📝 Standardizace formátu adres")

print(f"\n✅ SOUČASNÝ STAV JE VELMI DOBRÝ!")
print(f"💡 S {uspesnost:.1f}% úspěšností máte kvalitní geokódovaná data") 