import pandas as pd

print("📊 STATISTIKY sloučeného souboru kombinovane_data.csv")
print("=" * 50)

# Načtení souboru
df = pd.read_csv('kombinovane_data.csv', sep=';', encoding='utf-8')

print(f"📋 Celkem záznamů: {len(df)}")
print(f"📍 Záznamy s koordináty: {len(df.dropna(subset=['lat', 'lon']))}")
print(f"❌ Záznamy bez koordinátů: {len(df) - len(df.dropna(subset=['lat', 'lon']))}")

print(f"\n🏷️ Různé příznaky: {sorted(df['PŘÍZNAK'].unique())}")

print(f"\n📈 Rozložení podle příznaků:")
print(df['PŘÍZNAK'].value_counts().sort_index())

# Ukázka záznamů s RINO příznakem
rino_count = len(df[df['PŘÍZNAK'] == 'RINO'])
print(f"\n🔍 Záznamy s příznakem RINO: {rino_count}")

if rino_count > 0:
    print("Ukázka RINO záznamů:")
    print(df[df['PŘÍZNAK'] == 'RINO'].head(5)[['NÁZEV', 'Adresa']].to_string(index=False)) 