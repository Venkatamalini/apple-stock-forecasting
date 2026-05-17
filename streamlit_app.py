import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Apple Stock Forecasting",
    page_icon="📈",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }

    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================
# NAIVE MODEL CLASS
# =========================================
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

# =========================================
# LOAD MODEL
# =========================================


# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Price Forecasting")
st.markdown("Predict future stock prices using Machine Learning")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("⚙ Settings")

forecast_days = st.sidebar.slider(
    "Forecast Days",
    min_value=7,
    max_value=90,
    value=30
)

# =========================================
# FILE UPLOAD
# =========================================
uploaded_file = st.file_uploader(
    "📂 Upload Stock CSV File",
    type=["csv"]
)

if uploaded_file:

    # =====================================
    # LOAD DATA
    # =====================================
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head())

    # =====================================
    # VALIDATION
    # =====================================
    required_columns = ["Close"]

    missing_cols = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")

    else:

        # =================================
        # CLEAN DATA
        # =================================
        close_prices = df["Close"].dropna().values

        if len(close_prices) < 2:
            st.error("Not enough data for prediction")

        else:

            # =============================
            # DATE PROCESSING
            # =============================
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(
                    df["Date"],
                    errors="coerce"
                )

            else:
                df["Date"] = pd.date_range(
                    end=pd.Timestamp.today(),
                    periods=len(df)
                )

            # =============================
            # PREDICTION
            # =============================
            # =============================
            # SIMPLE FORECAST
            # =============================
            last_price = close_prices[-1]

            trend = (
            close_prices[-1] - close_prices[-2]
           )

            preds = []

            next_price = last_price

            for _ in range(forecast_days):
                next_price += trend
            preds.append(round(next_price, 2))
            

            # =============================
            # SAFE DATE HANDLING
            # =============================

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
    )

        df = df.dropna(subset=["Date"])

        if df.empty:
            last_date = pd.Timestamp.today()
        else:
            last_date = df["Date"].iloc[-1]

            future_dates = pd.date_range(
            start=last_date,
            periods=forecast_days + 1
            )[1:]

            # =============================
            # PREDICTION DATAFRAME
            # =============================
            pred_df = pd.DataFrame({
                "Date": future_dates,
                "Predicted Price": preds
            })

            # =============================
            # METRICS
            # =============================
            st.subheader("📊 Forecast Insights")

            col1, col2, col3 = st.columns(3)

            change = (
                (preds[-1] - preds[0]) / preds[0]
            ) * 100

            with col1:
                st.metric(
                    "Expected Change",
                    f"{change:.2f}%"
                )

            with col2:
                st.metric(
                    "Maximum Price",
                    f"${max(preds):.2f}"
                )

            with col3:
                st.metric(
                    "Minimum Price",
                    f"${min(preds):.2f}"
                )

            # =============================
            # RECOMMENDATION
            # =============================
            st.subheader("💡 Recommendation")

            if change > 1:
                st.success("✅ BUY")

            elif change < -1:
                st.error("❌ SELL")

            else:
                st.warning("⚠ HOLD")

            # =============================
            # VISUALIZATION
            # =============================
            st.subheader("📈 Forecast Chart")

            actual_df = df[["Date", "Close"]].copy()

            actual_df.columns = ["Date", "Price"]
            actual_df["Type"] = "Actual"

            forecast_df = pred_df.copy()
            forecast_df.columns = ["Date", "Price"]
            forecast_df["Type"] = "Forecast"

            combined = pd.concat([
                actual_df.tail(100),
                forecast_df
            ])

            fig = px.line(
                combined,
                x="Date",
                y="Price",
                color="Type",
                title="Stock Price Forecast"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =============================
            # FORECAST TABLE
            # =============================
            st.subheader("📅 Forecast Table")

            st.dataframe(pred_df)

            # =============================
            # DOWNLOAD BUTTON
            # =============================
            csv = pred_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇ Download Predictions",
                data=csv,
                file_name="stock_predictions.csv",
                mime="text/csv"
            )

else:
    st.info("👆 Upload a CSV file to begin forecasting")