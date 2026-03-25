import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

def load_watchlist():
    df = pd.read_csv("watchlist.csv")
    return df["Ticker"].tolist()

def analyser_ticker(ticker):
    try:
        data = yf.Ticker(ticker).history(period="3mo")
        if len(data) < 30: return None
        info = yf.Ticker(ticker).info
        prix = data['Close'].iloc[-1]
        vol_ratio = data['Volume'].iloc[-1] / data['Volume'].rolling(10).mean().iloc[-1]
        mcap = info.get('marketCap', 0) / 1e9
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
        loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + gain/loss)) if loss != 0 else 50
        score = (vol_ratio * 3) + ((100 - rsi) * 2) + (10 / (prix + 0.01)) + (2 / (mcap + 0.01))

        court = "🚀 Fort rebond possible (1-7 jours)" if rsi < 40 and vol_ratio > 4 else "📈 Rebond probable" if vol_ratio > 3 else "➡️ Neutre court terme"
        moyen = "🌟 Potentiel élevé (1-4 semaines)" if mcap < 2 and score > 22 else "📊 Potentiel modéré"

        return {
            "Ticker": ticker, "Prix": round(prix,3), "Vol Ratio": round(vol_ratio,2),
            "RSI": round(rsi,1), "Market Cap": round(mcap,2), "Change 5j": round((data['Close'].iloc[-1]/data['Close'].iloc[-6]-1)*100,1),
            "Score": round(score,1), "Court terme": court, "Moyen terme": moyen
        }
    except:
        return None

def envoyer_email(sujet, html):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg["Subject"] = sujet
    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
    server.quit()

if __name__ == "__main__":
    tickers = load_watchlist()
    results = [analyser_ticker(t) for t in tickers]
    results = [r for r in results if r]
    df = pd.DataFrame(results).sort_values("Score", ascending=False)

    df_filtre = df[(df["Prix"] <= 15) & (df["Vol Ratio"] >= 3) & (df["RSI"] <= 45) & (df["Market Cap"] <= 3) & (df["Score"] >= 18)]

    if not df_filtre.empty:
        html = f"<h2>🚨 PÉPITES DÉTECTÉES - {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>{df_filtre.to_html(index=False)}"
        envoyer_email("🚨 Nouvelle Pépite !", html)

    # Rapport quotidien à 8h
    if datetime.now().hour == 8 or datetime.now().hour == 9:  # sécurité horaire
        html_daily = f"<h2>📊 Rapport Quotidien PépiteScanner - {datetime.now().strftime('%Y-%m-%d')}</h2><h3>Top 10</h3>{df.head(10).to_html(index=False)}"
        envoyer_email("📊 Rapport Quotidien - PépiteScanner", html_daily)
