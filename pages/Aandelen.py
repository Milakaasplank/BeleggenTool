import streamlit as st
from calculations import *
import pandas as pd
from GoogleNews import GoogleNews
from pygooglenews import GoogleNews
from openai import OpenAI
import os

# client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

st.set_page_config(page_title="Aandelen", page_icon="📈")

st.title("Fundamentele Analyse: Aandelen")

st.write("Vul de gegevens in over een aandeel om de financiële ratio's te berekenen. Onder een ratio komt automatisch een groene (goed), oranje (matig) of rode (slecht) tekst te staan. Dit geeft aan hoe het aandeel scoort op dit onderdeel van de fundamentele analyse.")

st.warning(
    "⚠️ **Let op de DeGiro-conventie — die wijkt af van wat je verwacht:**\n\n"
    "- DeGiro **`M`** = **miljard** (10⁹) — dus NIET miljoen!\n"
    "- DeGiro **`B`** = **biljoen** (10¹²)\n"
    "- Geen suffix in DeGiro = meestal al in miljoenen\n\n"
    "**Deze app verwacht alle totaalwaardes in miljoenen.** Reken dus om:\n\n"
    "| DeGiro toont | Werkelijk bedrag | Vul in app in |\n"
    "|---|---|---|\n"
    "| `37,6M` | €37,6 miljard | **`37600`** |\n"
    "| `3,8B` | €3,8 biljoen | **`3800000`** |\n"
    "| `651` (geen suffix) | €651 miljoen | **`651`** |\n"
    "| `5,593M` aandelen | 5,593 mrd aandelen | **`5593`** |\n\n"
    "🔍 Onder elk veld verschijnt de geïnterpreteerde waarde — controleer altijd of de magnitude klopt.\n\n"
    "Per-aandeel waardes (koers) en percentages vul je gewoon zoals DeGiro ze toont."
)

st.text_input("Enter the name of the stock", key="stock_name", placeholder="Aandeel Naam")
# ----------------TODO: Search google news for articles related to the stock ----------
# if "stock_name" in st.session_state:
#     gn = GoogleNews()
#     # Search for financial news articles related to the stock name
#     search = gn.search(('Financial news ' + st.session_state["stock_name"]), when='7d')
#     # Transform the results into a pandas DataFrame
#     df = pd.DataFrame(search['entries'])
#     df.sort_values(by='published', ascending=False, inplace=True)
#     # Show the titles and links of the articles, show 5
#     st.subheader("Recent Financial News Articles")
#     for index, row in df.iterrows():
#         st.markdown(f"[{row['title']}]({row['link']}) - {row['published']}")

# Ask openai for a short summary on what they do
# if "stock_name" in st.session_state:
#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "user", "content": f"Geef een korte samenvatting van wat {st.session_state['stock_name']} doet."}
#         ]
#     )
#     st.subheader("Bedrijfsinformatie")
#     st.write(response.choices[0].message.content)

# Layout for input
st.subheader("Financiële Gegevens")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Balans")
    activa = st.number_input("Total Assets (in M €)", step=1.0, key="activa")
    st.caption(preview_geld_M(activa))
    passiva = st.number_input("Total Liabilities (in M €)", step=1.0, key="passiva")
    st.caption(preview_geld_M(passiva))
    st.caption("ℹ️ Boekwaarde per aandeel wordt automatisch berekend uit eigen vermogen ÷ aantal aandelen.")

with col2:
    st.subheader("Resultatenrekening")
    nettowinst = st.number_input("Netincome (in M €)", step=1.0, key="nettowinst")
    st.caption(preview_geld_M(nettowinst))
    tienjaars_staatsobligatie = st.number_input("10-Year Government Bond Yield (%)", step=0.01, key="tienjaars_staatsobligatie")

st.subheader("Overzicht")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Prijsdata")
    uitstaande_aandelen = st.number_input("Outstanding Shares (in M)", step=0.01, key="uitstaande_aandelen")
    st.caption(preview_aantal_M(uitstaande_aandelen))
    actuele_beurskoers = st.number_input("Current Stock Price (€)", step=0.01, key="actuele_beurskoers")

with col4:
    st.subheader("Ratio's")
    verwachte_winst = st.number_input("Verwachte winst (in M €)", step=1.0, key="verwachte_winst")
    st.caption(preview_geld_M(verwachte_winst))

# Calculations
st.subheader("Financial Ratios")

# Avoid crashing on empty or zero inputs
try:
    eigen_vermogen_waarde = eigen_vermogen(activa, passiva)
    solvabiliteit_waarde = solvabiliteit(eigen_vermogen_waarde, activa)
    # Alle balans- en winstvelden zijn in miljoenen, dus eenheden vallen weg
    rentabiliteit_waarde = rentabiliteit(nettowinst, eigen_vermogen_waarde or 0)
    # Boekwaarde per aandeel = eigen vermogen / aantal aandelen (M / M = € per aandeel)
    if eigen_vermogen_waarde and uitstaande_aandelen > 0:
        boekwaarde_per_aandeel = eigen_vermogen_waarde / uitstaande_aandelen
    else:
        boekwaarde_per_aandeel = 0
    wpa_waarde = wpa(nettowinst, uitstaande_aandelen)
    kw_waarde = kw(actuele_beurskoers, wpa_waarde)
    # Bereken impliciete winstgroei (%) uit huidige nettowinst → verwachte winst
    if nettowinst > 0 and verwachte_winst > 0:
        verwachte_winstgroei = (verwachte_winst - nettowinst) / nettowinst * 100
    else:
        verwachte_winstgroei = 0
    peg_waarde = peg(kw_waarde, verwachte_winstgroei)
    graham_waarde = graham_number(wpa_waarde, boekwaarde_per_aandeel)

    col1, col2, col4 = st.columns(3)
    col1.metric("Solvabiliteit", f"{solvabiliteit_waarde:.2f}%", "", border=True)
    col1.caption("Hoeverre een bedrijf in staat is om aan zijn financiële verplichtingen te voldoen, vooral op lange termijn.")
    # If 50 > solvabiliteit > 25
    if 25 < solvabiliteit_waarde < 50:
        col1.markdown("<span style='color: orange;'>Let op: Solvabiliteit tussen 25% en 50%</span>", unsafe_allow_html=True)
    elif solvabiliteit_waarde <= 25:
        col1.markdown("<span style='color: red;'>Waarschuwing: Solvabiliteit onder 25%</span>", unsafe_allow_html=True)
    else:
        col1.markdown("<span style='color: green;'>Solvabiliteit boven 50%</span>", unsafe_allow_html=True)
    col2.metric("Rentabiliteit", f"{rentabiliteit_waarde:.2f}%", "", border=True)
    col2.caption("Hoeveel winst een bedrijf maakt met het geld dat het investeert.")
    # If rentabiliteit < staatsobligaties + 10, then it is a warning
    if rentabiliteit_waarde < (tienjaars_staatsobligatie + 10):
        col2.markdown("<span style='color: red;'>Waarschuwing: Rentabiliteit onder staatsobligaties + 10%</span>", unsafe_allow_html=True)
    else:
        col2.markdown("<span style='color: green;'>Rentabiliteit boven staatsobligaties + 10%</span>", unsafe_allow_html=True)
    # col3.metric("Boekwaarde / aandeel", f"€ {boekwaarde_per_aandeel:.2f}", "", border=True)
    # col3.caption(f"Eigen vermogen ({eigen_vermogen_waarde or 0:.0f}M €) ÷ aandelen ({uitstaande_aandelen:.2f}M).")
    graham_delta = graham_waarde - actuele_beurskoers if graham_waarde > 0 and actuele_beurskoers > 0 else None
    col4.metric(
        "Graham Number",
        f"€ {graham_waarde:.2f}",
        delta=f"{graham_delta:+.2f} € vs koers" if graham_delta is not None else None,
        border=True,
    )
    col4.caption("Maximale prijs volgens Graham. Verschil met huidige koers staat boven.")
    if graham_waarde > 0 and actuele_beurskoers > 0:
        if graham_waarde > actuele_beurskoers:
            col4.markdown(
                f"<span style='color: green;'>Koers €{actuele_beurskoers:.2f} ligt €{graham_waarde - actuele_beurskoers:.2f} onder Graham → mogelijk ondergewaardeerd</span>",
                unsafe_allow_html=True,
            )
        else:
            col4.markdown(
                f"<span style='color: red;'>Koers €{actuele_beurskoers:.2f} ligt €{actuele_beurskoers - graham_waarde:.2f} boven Graham → mogelijk overgewaardeerd</span>",
                unsafe_allow_html=True,
            )
    col1, col2, col3 = st.columns(3)
    col1.metric("Winst per Aandeel", f"{wpa_waarde:.2f} €", "", border=True)
    col1.caption("Hoeveel winst een bedrijf maakt per uitstaand aandeel.")
    col2.metric("Koers-Winstverhouding", f"{kw_waarde:.2f}", "", border=True)
    col2.caption("Indicatie of een aandeel relatief duur of goedkoop is")
    # If k/w > 20, then it is a warning, under 10 is good, between 10 and 20 is okay
    if kw_waarde > 20:
        col2.markdown("<span style='color: red;'>Waarschuwing: Koers-Winstverhouding boven 20</span>", unsafe_allow_html=True)
    elif kw_waarde < 10:
        col2.markdown("<span style='color: green;'>Koers-Winstverhouding onder 10</span>", unsafe_allow_html=True)
    else:
        col2.markdown("<span style='color: orange;'>Koers-Winstverhouding tussen 10 en 20</span>", unsafe_allow_html=True)

    col3.metric("PEG Ratio", f"{peg_waarde:.2f}", "", border=True)
    col3.caption(f"Berekend met impliciete winstgroei van {verwachte_winstgroei:.1f}% (van {nettowinst:.0f}M → {verwachte_winst:.0f}M). Onder 1 = mogelijk ondergewaardeerd.")
    # If PEG > 1, then it is a warning, under 1 is warning
    if peg_waarde > 1:
        col3.markdown("<span style='color: red;'>Waarschuwing: Aandeel overgewaardeerd</span>", unsafe_allow_html=True)
    else:
        col3.markdown("<span style='color: green;'>Aandeel ondergewaardeerd</span>", unsafe_allow_html=True)
    # Save all data to file
    if st.button("Save Financial Data"):
        # Save the financial data and stock name with date of today to a file
        import datetime
        today = datetime.date.today()
        stock_name = st.session_state.get("stock_name", "Unknown Stock")
        financial_data = {
            "date": today,
            "stock_name": stock_name,
            "activa": activa,
            "passiva": passiva,
            "boekwaarde_per_aandeel": boekwaarde_per_aandeel,
            "nettowinst": nettowinst,
            "tienjaars_staatsobligatie": tienjaars_staatsobligatie,
            "uitstaande_aandelen": uitstaande_aandelen,
            "actuele_beurskoers": actuele_beurskoers,
            "verwachte_winst": verwachte_winst,
            "verwachte_winstgroei": verwachte_winstgroei,
            "eigen_vermogen": eigen_vermogen_waarde,
            "solvabiliteit": solvabiliteit_waarde,
            "rentabiliteit": rentabiliteit_waarde,
            "wpa": wpa_waarde,
            "kw": kw_waarde,
            "peg": peg_waarde,
            "graham_number": graham_waarde
        }
        # Store data in a pandas DataFrame
        df = pd.DataFrame([financial_data])
        # Save to excel
        file_name = f"{stock_name}_financial_data_{today}.xlsx"
        df.to_excel(file_name, index=False, engine='openpyxl')
        # Show success message
        st.success(f"Financial data for {stock_name} saved successfully!")
        # Storing all the inputs and ra
except Exception as e:
    st.warning(f"Vul alstublieft alle financiële gegevens correct in om de ratio's te berekenen. ({e})")