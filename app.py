import streamlit as st
from calculations import *
import pandas as pd
import openpyxl

# st.sidebar.subheader("Menu")

# # Page configuration
# st.set_page_config(
#     page_title="Streamlit App",
#     page_icon=":guardsman:",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Title
st.title("Fundamentele Analyse: Aandeel")
st.subheader("Welkom Vince!")
st.image("image.png", use_column_width=True)
st.subheader("Hoe werkt het?")
st.text("Gebruik deze app om gegevens in te vullen van een aandeel. Daarna zullen automatisch financiële ratio's van het aandeel worden berekend. Onder elke ratio staat een richtlijn die uit het boek Beleggen voor Dummies komt. Je kan dit 'advies' gebruiken om betere investeringsbeslissingen te nemen.")
st.text("Er is een Aandelen pagina waar je de benodigde informatie kan invullen over een aandeel. Deze informatie vind je op De Giro pagina bij elk aandeel.")

# Itemize the coming updates
st.text("Komende updates:")
st.text("- Laatste nieuwsberichten van een aandeel")
st.text("- ETF pagina")