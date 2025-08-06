import pandas as pd
import streamlit as st
import pydeck as pdk
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Interaktivní mapa adres", layout="wide")
st.title("Interaktivní mapa adres - 25.06.2025")

# === 1. Načtení dat ===
CSV_SOUBOR = "kombinovane_data_aktualizovane.csv"
ODDELENI = ";"
KODOVANI = "utf-8"

# Načti sloučená data
df = pd.read_csv(CSV_SOUBOR, encoding=KODOVANI, sep=ODDELENI)

# Převod souřadnic na číselné hodnoty (pandas může načíst jako text)
df["lat"] = pd.to_numeric(df["lat"], errors='coerce')
df["lon"] = pd.to_numeric(df["lon"], errors='coerce')

# Převod nulových koordinátů na NaN
df.loc[df["lat"] == 0, "lat"] = None
df.loc[df["lon"] == 0, "lon"] = None


# === 2. Filtrování podle PŘÍZNAK ===
priznaky = sorted(df["PŘÍZNAK"].dropna().unique())
vybrane = st.multiselect("Filtr PŘÍZNAK", priznaky, default=priznaky)

# === 2a. Přiřazení barev jednotlivým příznakům ===
# Definuj 11 barev (můžeš upravit podle vkusu)
barvy = [
    [0, 180, 60, 160],    # červená
    [0, 120, 200, 160],   # modrá
    [200, 30, 0, 160],    # zelená
    [255, 140, 0, 160],   # oranžová
    [160, 0, 200, 160],   # fialová
    [255, 215, 0, 160],   # žlutá
    [0, 200, 200, 160],   # tyrkysová
    [120, 0, 0, 160],     # tmavě červená
    [0, 0, 120, 160],     # tmavě modrá
    [0, 120, 0, 160],     # tmavě zelená
    [120, 120, 120, 160], # šedá
]
priznak2barva = {p: barvy[i % len(barvy)] for i, p in enumerate(priznaky)}

# Filtrování
df_filt = df[df["PŘÍZNAK"].isin(vybrane) & df["lat"].notnull() & df["lon"].notnull()].copy()
df_filt["barva"] = df_filt["PŘÍZNAK"].map(priznak2barva)

# === 3. Zobrazení mapy ===
st.subheader(f"Počet zobrazených bodů: {len(df_filt)}")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pdk.ViewState(
        latitude=49.8,
        longitude=15.5,
        zoom=7,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=df_filt,
            get_position='[lon, lat]',
            get_color='barva',
            get_radius=500,
            radiusMinPixels=5,
            radiusMaxPixels=30,
            pickable=True,
        ),
    ],
    tooltip={"text": "{NÁZEV}\n{Adresa}\nPŘÍZNAK: {PŘÍZNAK}\nCF: {CF}"}
))

# === 3a. Legenda barev ===
barva2hex = lambda rgba: '#%02x%02x%02x' % tuple(rgba[:3])
legend_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;">'
for p in priznaky:
    legend_html += f'<div style="display:flex;align-items:center;"><div style="width:18px;height:18px;border-radius:50%;background:{barva2hex(priznak2barva[p])};margin-right:6px;"></div>{p}</div>'
legend_html += '</div>'
components.html(legend_html, height=40 + 30 * ((len(priznaky)+4)//5))

# === 4. Výpis nenalezených adres ===
nenalezeno = df[df["lat"].isnull() | df["lon"].isnull()]
if not nenalezeno.empty:
    st.warning(f"Adresy, které se nepodařilo najít ({len(nenalezeno)}):")
    st.write(nenalezeno[["NÁZEV", "Adresa", "PŘÍZNAK"]]) 
