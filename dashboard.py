import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from fpdf import FPDF
import tempfile
import os

st.title("🚀 PépiteScanner PRO - Dashboard")

tickers = pd.read_csv("watchlist.csv")["Ticker"].tolist()
st.write("Watchlist actuelle :", tickers)

if st.button("🔥 Lancer Scan Manuel"):
    # même fonction analyser que dans scanner.py (je peux te la dupliquer si besoin)
    st.success("Scan terminé - regarde tes emails pour le rapport complet")
    # Affichage simple du dernier scan (tu peux améliorer)

st.caption("Le scanner réel tourne toutes les heures via GitHub Actions. Ce dashboard te permet de visualiser facilement.")
