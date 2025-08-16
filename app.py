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
st.subheader("Welkom bij de Fundamentele Analyse App!")
st.text("Gebruik deze app om financiële ratio's van aandelen te berekenen.")
st.text("Vul de benodigde gegevens in en bekijk de resultaten.")