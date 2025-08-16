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
st.subheader("Welkom bij de Fundamentele Analyse App Vince!")
st.image("image.png")
st.text("Gebruik deze app om financiële ratio's van aandelen te berekenen. Je kan de data gebruiken om betere investeringsbeslissingen te nemen.")
st.text("Er is een Aandelen pagina waar je informatie kan invullen over een aandeel. Deze informatie vind je op De Giro pagina bij elk aandeel.")
# Itemize the coming updates
st.text("Komende updates:")
st.text("- Laatste nieuwsberichten van een aandeel")
st.text("- ETF pagina")