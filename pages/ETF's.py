import streamlit as st
import pandas as pd
import datetime
from calculations import parse_degiro_number, format_degiro_number
from pdf_extraction import parse_kiid

st.set_page_config(page_title="ETF's", page_icon="📈")

st.title("Fundamentele Analyse: ETF's")

st.write(
    "Vul de gegevens uit DeGiro in om een ETF te beoordelen op kosten, structuur, "
    "fiscaliteit en performance. Onder elke metric verschijnt een groene/oranje/rode "
    "indicatie."
)

# ====================================================================
# PDF UPLOAD — KIID/EID auto-fill
# ====================================================================
with st.expander("📄 **Sneller invullen: upload het KIID/EID document**", expanded=True):
    st.caption(
        "Upload een Essentiële-Informatiedocument (EID) of Key Investor Information "
        "Document (KIID) van de fondsbeheerder — werkt voor iShares, Vanguard, VanEck, "
        "Amundi etc., in NL of ENG. De velden voor structuur en kosten worden "
        "automatisch ingevuld. AUM, performance en holdings zitten niet in een "
        "KIID — die blijven handmatig."
    )
    uploaded_pdf = st.file_uploader("KIID/EID PDF", type="pdf", key="kiid_pdf")
    if uploaded_pdf is not None:
        if st.button("📥 Velden invullen uit PDF"):
            try:
                extracted, _full_text = parse_kiid(uploaded_pdf)
                if extracted:
                    for k, v in extracted.items():
                        st.session_state[k] = v
                    leesbaar = ", ".join(k.replace("etf_", "") for k in extracted.keys())
                    st.success(f"✓ {len(extracted)} veld(en) gevonden: {leesbaar}")
                    st.rerun()
                else:
                    st.warning("Geen velden herkend in deze PDF — vul handmatig in.")
            except ImportError as e:
                st.error(f"{e}")
            except Exception as e:
                st.error(f"Fout bij verwerken: {e}")

st.warning(
    "⚠️ **DeGiro-conventie voor de fondsgrootte:** `M` = miljard (10⁹), `B` = biljoen (10¹²). "
    "De parser hieronder accepteert beide suffixes — je mag de waarde letterlijk plakken (`75,4M`, `1,2B`)."
)

# ====================================================================
# SECTIE 1 — IDENTIFICATIE
# ====================================================================
st.subheader("1️⃣ Identificatie")
st.caption(
    "📍 **Bron:** auto-ingevuld uit het KIID-document (naam + ISIN). "
    "Ticker zie je bovenaan de DeGiro-pagina."
)

col_id1, col_id2, col_id3 = st.columns([2, 2, 1])
with col_id1:
    etf_naam = st.text_input("Naam", key="etf_naam", placeholder="iShares Core MSCI World")
with col_id2:
    isin = st.text_input("ISIN", key="etf_isin", placeholder="IE00B4L5Y983")
with col_id3:
    ticker = st.text_input("Ticker", key="etf_ticker", placeholder="IWDA")

st.divider()

# ====================================================================
# SECTIE 2 — FONDSSTRUCTUUR
# ====================================================================
st.subheader("2️⃣ Fondsstructuur")
st.caption(
    "📍 **Bron:** KIID/EID-document van de fondsbeheerder (download via de link "
    "naar het PRIIP/EID op de DeGiro ETF-pagina, of via de site van de uitgever). "
    "Domicilie, replicatie, UCITS en uitkeringsbeleid worden uit het PDF gehaald. "
    "AUM staat alleen in de factsheet — vul handmatig in."
)

col_s1, col_s2 = st.columns(2)
with col_s1:
    domicilie = st.selectbox(
        "Domicilie",
        ["Ierland (IE)", "Luxemburg (LU)", "Nederland (NL)", "Duitsland (DE)",
         "Verenigde Staten (US)", "Anders"],
        key="etf_domicilie",
        help="Het land waar het fonds juridisch is geregistreerd",
    )
    distributie = st.selectbox(
        "Uitkeringsbeleid",
        ["Accumulerend", "Distribuerend", "Onbekend"],
        key="etf_distributie",
        help="Accumulerend = winst wordt herbelegd. Distribuerend = winst wordt uitgekeerd.",
    )
    ucits = st.checkbox("UCITS conform", value=True, key="etf_ucits",
                       help="Verplicht voor NL particulieren")

with col_s2:
    replicatie = st.selectbox(
        "Replicatiemethode",
        ["Fysiek volledig", "Fysiek sampling", "Synthetisch (swap)", "Onbekend"],
        key="etf_replicatie",
        help="Hoe de index gevolgd wordt",
    )
    aum_raw = st.text_input(
        "Fondsgrootte / AUM",
        key="etf_aum_raw",
        placeholder="bijv. 75,4M of 1,2B",
        help="Mag direct uit DeGiro geplakt: M = miljard, B = biljoen",
    )
    aum = 0.0
    if aum_raw and aum_raw.strip():
        try:
            aum = parse_degiro_number(aum_raw)
            st.caption(f"= € {format_degiro_number(aum)}")
        except ValueError:
            st.error(f"Kan '{aum_raw}' niet lezen — gebruik bv. `75,4M` of `1,2B`")

st.divider()

# ====================================================================
# SECTIE 3 — KOSTEN
# ====================================================================
st.subheader("3️⃣ Kosten")
st.caption(
    "📍 **Bron:** TER wordt uit het KIID gehaald (kijk in 'Wat zijn de kosten?'-tabel). "
    "Kernselectie zie je in DeGiro aan het oranje 'Kernselectie'-label bovenaan de ETF-pagina."
)

col_k1, col_k2 = st.columns(2)
with col_k1:
    ter = st.number_input("Lopende kosten / TER (%)", step=0.01, min_value=0.0, key="etf_ter")
with col_k2:
    in_kernselectie = st.checkbox("In DeGiro Kernselectie (gratis aankoop)",
                                  value=False, key="etf_kernselectie")

st.divider()

# ====================================================================
# SECTIE 4 — PRIJS & DIVIDEND
# ====================================================================
st.subheader("4️⃣ Prijs & Dividend")
st.caption(
    "📍 **Bron:** koers staat groot bovenaan de DeGiro ETF-pagina. "
    "Dividend yield staat in de factsheet van de fondsbeheerder (DeGiro toont dit "
    "meestal niet); voor accumulerende ETF's is het 0%."
)

col_p1, col_p2 = st.columns(2)
with col_p1:
    actuele_koers = st.number_input("Actuele koers (€)", step=0.01, min_value=0.0, key="etf_koers")
with col_p2:
    dividend_yield = st.number_input("Dividend yield (%)", step=0.01, min_value=0.0, key="etf_dividend")

st.divider()

# ====================================================================
# SECTIE 5 — PERFORMANCE
# ====================================================================
st.subheader("5️⃣ Performance")
st.caption(
    "📍 **Bron:** DeGiro prijsgrafiek — selecteer de periode (1D/1M/1J/3J/5J/10J) en "
    "lees het rendementspercentage af bij de grafiek. Of de factsheet/uitgever-website "
    "voor exacte kalenderjaar-rendementen. Vul **cumulatieve** percentages in — "
    "geannualiseerd 5Y wordt zelf berekend."
)

col_pf1, col_pf2, col_pf3, col_pf4, col_pf5 = st.columns(5)
with col_pf1:
    ytd = st.number_input("YTD (%)", step=0.1, key="etf_ytd")
with col_pf2:
    return_1y = st.number_input("1 jaar (%)", step=0.1, key="etf_1y")
with col_pf3:
    return_3y = st.number_input("3 jaar cum. (%)", step=0.1, key="etf_3y")
with col_pf4:
    return_5y = st.number_input("5 jaar cum. (%)", step=0.1, key="etf_5y")
with col_pf5:
    return_10y = st.number_input("10 jaar cum. (%)", step=0.1, key="etf_10y")

st.divider()

# ====================================================================
# SECTIE 6 — BLOOTSTELLING
# ====================================================================
st.subheader("6️⃣ Blootstelling")
st.caption(
    "📍 **Bron:** type en regio worden uit het KIID afgeleid (beleggingsdoelstelling + index-naam). "
    "Aantal posities, top-holdings en sector-/regioverdelingen staan **niet** in een KIID — "
    "die vind je in de factsheet of op de website van de uitgever (iShares.com, vanguard.nl etc.)."
)

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    type_fonds = st.selectbox(
        "Type",
        ["Aandelen", "Obligaties", "Vastgoed", "Grondstoffen", "Mixed", "Anders"],
        key="etf_type",
    )
with col_b2:
    regio = st.selectbox(
        "Regio",
        ["Wereldwijd", "Verenigde Staten", "Europa", "Opkomende Markten", "Azië",
         "Nederland", "Anders"],
        key="etf_regio",
    )
with col_b3:
    aantal_holdings = st.number_input("Aantal posities", step=1, min_value=0, key="etf_holdings")

st.divider()

# ====================================================================
# BEOORDELING
# ====================================================================
st.subheader("📊 Beoordeling")


def kleur(text, color):
    return f"<span style='color: {color};'>{text}</span>"


# 5Y geannualiseerd
if return_5y > -100:
    return_5y_annualized = ((1 + return_5y / 100) ** (1 / 5) - 1) * 100
else:
    return_5y_annualized = 0.0

# Rij 1: kosten/structuur
m1, m2, m3, m4 = st.columns(4)

# TER
m1.metric("TER", f"{ter:.2f}%", border=True)
m1.caption("Jaarlijkse kosten van het fonds")
if 0 < ter <= 0.20:
    m1.markdown(kleur("Goedkoop (≤ 0,20%)", "green"), unsafe_allow_html=True)
elif ter <= 0.50:
    m1.markdown(kleur("Acceptabel (≤ 0,50%)", "orange"), unsafe_allow_html=True)
else:
    m1.markdown(kleur("Duur (> 0,50%)", "red"), unsafe_allow_html=True)

# AUM
m2.metric("Fondsgrootte", format_degiro_number(aum) if aum else "—", border=True)
m2.caption("Hoger = liquider, minder kans op liquidatie")
if aum >= 500_000_000:
    m2.markdown(kleur("Groot (> €500M)", "green"), unsafe_allow_html=True)
elif aum >= 100_000_000:
    m2.markdown(kleur("Middelgroot (€100M–€500M)", "orange"), unsafe_allow_html=True)
else:
    m2.markdown(kleur("Klein (< €100M)", "red"), unsafe_allow_html=True)

# Domicilie
m3.metric("Domicilie", domicilie.split(" (")[0], border=True)
m3.caption("Fiscaal relevant voor NL belegger")
if domicilie.startswith("Ierland") or domicilie.startswith("Luxemburg"):
    m3.markdown(kleur("Fiscaal gunstig — geen dividendlek", "green"), unsafe_allow_html=True)
elif domicilie.startswith("Nederland"):
    m3.markdown(kleur("NL gedomicilieerd — OK", "orange"), unsafe_allow_html=True)
elif domicilie.startswith("Verenigde"):
    m3.markdown(kleur("US — risico op dividendlek", "red"), unsafe_allow_html=True)
else:
    m3.markdown(kleur("Onbekende behandeling", "orange"), unsafe_allow_html=True)

# Replicatie
m4.metric("Replicatie", replicatie.split(" (")[0], border=True)
m4.caption("Hoe de index gevolgd wordt")
if replicatie.startswith("Fysiek volledig"):
    m4.markdown(kleur("Volledige replicatie — laag risico", "green"), unsafe_allow_html=True)
elif replicatie.startswith("Fysiek sampling"):
    m4.markdown(kleur("Sampling — kleine afwijking", "orange"), unsafe_allow_html=True)
elif replicatie.startswith("Synthetisch"):
    m4.markdown(kleur("Synthetisch — tegenpartijrisico", "orange"), unsafe_allow_html=True)
else:
    m4.markdown(kleur("Methode onbekend", "orange"), unsafe_allow_html=True)

# Rij 2: toegankelijkheid/performance
m5, m6, m7, m8 = st.columns(4)

m5.metric("UCITS", "Ja" if ucits else "Nee", border=True)
m5.caption("Verplicht voor NL particulieren")
if ucits:
    m5.markdown(kleur("Toegankelijk via DeGiro", "green"), unsafe_allow_html=True)
else:
    m5.markdown(kleur("Niet toegankelijk voor NL particulier", "red"), unsafe_allow_html=True)

m6.metric("Kernselectie", "Ja" if in_kernselectie else "Nee", border=True)
m6.caption("Gratis aankoop in DeGiro")
if in_kernselectie:
    m6.markdown(kleur("Geen transactiekosten", "green"), unsafe_allow_html=True)
else:
    m6.markdown(kleur("Reguliere transactiekosten", "orange"), unsafe_allow_html=True)

m7.metric("5Y geannualiseerd", f"{return_5y_annualized:.2f}%", border=True)
m7.caption("Gemiddeld jaarlijks rendement over 5 jaar")
if return_5y_annualized >= 10:
    m7.markdown(kleur("Sterk (> 10%/jaar)", "green"), unsafe_allow_html=True)
elif return_5y_annualized >= 5:
    m7.markdown(kleur("Redelijk (5–10%/jaar)", "orange"), unsafe_allow_html=True)
elif return_5y_annualized > 0:
    m7.markdown(kleur("Zwak (< 5%/jaar)", "red"), unsafe_allow_html=True)
else:
    m7.markdown(kleur("Geen / negatief rendement", "red"), unsafe_allow_html=True)

m8.metric("# Posities", f"{int(aantal_holdings)}" if aantal_holdings else "—", border=True)
m8.caption("Aantal aandelen/obligaties in fonds")
if aantal_holdings >= 200:
    m8.markdown(kleur("Goed gespreid (> 200)", "green"), unsafe_allow_html=True)
elif aantal_holdings >= 50:
    m8.markdown(kleur("Acceptabel (50–200)", "orange"), unsafe_allow_html=True)
elif aantal_holdings > 0:
    m8.markdown(kleur("Geconcentreerd (< 50)", "red"), unsafe_allow_html=True)
else:
    m8.markdown(kleur("Onbekend", "orange"), unsafe_allow_html=True)

st.divider()

# ====================================================================
# SAVE
# ====================================================================
if st.button("💾 Save ETF Data"):
    today = datetime.date.today()
    data = {
        "date": today,
        "naam": etf_naam,
        "isin": isin,
        "ticker": ticker,
        "domicilie": domicilie,
        "distributie": distributie,
        "replicatie": replicatie,
        "ucits": ucits,
        "in_kernselectie": in_kernselectie,
        "aum": aum,
        "ter": ter,
        "actuele_koers": actuele_koers,
        "dividend_yield": dividend_yield,
        "ytd": ytd,
        "return_1y": return_1y,
        "return_3y": return_3y,
        "return_5y": return_5y,
        "return_10y": return_10y,
        "return_5y_annualized": return_5y_annualized,
        "type_fonds": type_fonds,
        "regio": regio,
        "aantal_holdings": aantal_holdings,
    }
    df = pd.DataFrame([data])
    file_name = f"{etf_naam or ticker or 'ETF'}_etf_data_{today}.xlsx"
    df.to_excel(file_name, index=False, engine='openpyxl')
    st.success(f"ETF data opgeslagen als {file_name}")
