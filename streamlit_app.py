import streamlit as st
import pandas as pd
import numpy as np
import pickle

# =========================
# NAIVE MODEL CLASS (REQUIRED FOR LOADING)
# =========================
class NaiveModel:
    def __init__(self, strategy="last"):
        self.strategy = strategy

    def predict(self, data, steps=30):
        data = list(data)

        if self.strategy == "last":
            last_value = data[-1]
            return [last_value] * steps

        elif self.strategy == "drift":
            trend = data[-1] - data[-2]
            preds = []
            last_value = data[-1]

            for _ in range(steps):
                next_val = last_value + trend
                preds.append(next_val)
                last_value = next_val

            return preds

# =========================
# LOAD MODEL
# =========================
with open("naive_model.pkl", "rb") as f:
    model = pickle.load(f)

st.title("Stock Price Prediction App")
st.write("Predict the next 30 days of stock prices")

# =========================
# FILE INPUT
# =========================
uploaded_file = st.file_uploader("Upload stock CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.write(df.head())

    # =========================
    # VALIDATION
    # =========================
    if "Close" not in df.columns:
        st.error("CSV must contain a 'Close' column")
    else:
        close_prices = df["Close"].dropna().values

        if len(close_prices) < 2:
            st.error("Not enough data for prediction")
        else:
            # =========================
            # PREDICTION
            # =========================
            last_price = close_prices[-1]
            preds = [last_price for i in range(30)]

            # =========================
            # CREATE FUTURE DATES
            # =========================
            last_date = pd.to_datetime(df.iloc[-1]["Date"]) if "Date" in df.columns else pd.Timestamp.today()

            future_dates = pd.date_range(start=last_date, periods=31)[1:]

            pred_df = pd.DataFrame({
                "Date": future_dates,
                "Predicted Price": preds
            })
            
            st.subheader("Forecast")

            # =========================
            # PREPARE ACTUAL DATA
            # =========================
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
                actual_df = df[["Date", "Close"]].copy()
            else:
                # fallback if no date column
                actual_df = df[["Close"]].copy()
                actual_df["Date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))

            actual_df["Type"] = "Actual"

            # =========================
            # PREPARE PREDICTION DATA
            # =========================
            pred_plot = pred_df.copy()
            pred_plot.columns = ["Date", "Close"]
            pred_plot["Type"] = "Predicted"

            # =========================
            # COMBINE
            # =========================
            combined = pd.concat([actual_df.tail(100), pred_plot])

            # =========================
            # PLOT
            # =========================
            st.line_chart(
                combined.set_index("Date")[["Close"]]
            ) 

            # =========================
            # OUTPUT TABLE
            # =========================
            st.subheader("30-Day Forecast Table")
            st.write(pred_df)

            # =========================
            # INSIGHTS
            # =========================
            change = ((preds[-1] - preds[0]) / preds[0]) * 100

            st.subheader(" Insights")
            st.write(f"Expected Change: {change:.2f}%")
            st.write(f"Max Price: {max(preds):.2f}")
            st.write(f"Min Price: {min(preds):.2f}")

            # =========================
            # RECOMMENDATION
            # =========================
            if change > 1:
                rec = " BUY!!"
            elif change < -1:
                rec = " SELL"
            else:
                rec = " HOLD"

            st.subheader(" Recommendation")
            st.write(rec)

            # =========================
            # DOWNLOAD
            # =========================
            csv = pred_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                " Download Predictions",
                data=csv,
                file_name="predictions.csv",
                mime="text/csv"
            )
