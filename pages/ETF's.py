import streamlit as st
from calculations import *
import pandas as pd

st.set_page_config(page_title="ETF's", page_icon="📈")
# ETF Page
st.subheader("ETF Analyse")
tickers = st.text_input("Enter ETF tickers (comma separated)", key="tickers", placeholder="VWRL, IWDA, EIMI").split(',')
# When input is empty, show a warning
if not tickers or tickers == ['']:
    st.warning("Voer ten minste één ETF ticker in, gescheiden door een komma.")
else:
    tickers = [ticker.strip() for ticker in tickers if ticker.strip()]
df = pd.DataFrame([analyze_etf(t) for t in tickers])
st.dataframe(df, use_container_width=True)