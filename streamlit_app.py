import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Apple Stock Forecast",
    page_icon="📈",
    layout="wide"
)

# =========================================
# CUSTOM BLACK & WHITE THEME
# =========================================
st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #000000;
    color: white;
}

.stApp {
    background-color: #000000;
}

[data-testid="stSidebar"] {
    background-color: #111111;
}

h1, h2, h3 {
    color: white;
}

.metric-box {
    background-color: #111111;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #333333;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Price Forecasting")
st.markdown("### AI-Based Future Stock Prediction Dashboard")

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("⚙ Forecast Settings")

forecast_days = st.sidebar.slider(
    "Select Forecast Days",
    7,
    90,
    30
)

# =========================================
# FILE UPLOAD
# =========================================
uploaded_file = st.file_uploader(
    "Upload Stock CSV File",
    type=["csv"]
)

# =========================================
# MAIN LOGIC
# =========================================
if uploaded_file:

    # =====================================
    # READ DATA
    # =====================================
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head())

    # =====================================
    # VALIDATION
    # =====================================
    if "Close" not in df.columns:
        st.error("CSV must contain 'Close' column")

    else:

        # =================================
        # DATE PROCESSING
        # =================================
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

        df = df.dropna(subset=["Date"])

        # =================================
        # CLOSE PRICE
        # =================================
        close_prices = df["Close"].dropna().values

        if len(close_prices) < 2:
            st.error("Not enough data")

        else:

            # =================================
            # SIMPLE TREND FORECAST
            # =================================
            last_price = close_prices[-1]

            trend = close_prices[-1] - close_prices[-2]

            preds = []

            next_price = last_price

            for _ in range(forecast_days):
                next_price += trend
                preds.append(round(next_price, 2))

            # =================================
            # FUTURE DATES
            # =================================
            last_date = df["Date"].iloc[-1]

            future_dates = pd.date_range(
                start=last_date,
                periods=forecast_days + 1
            )[1:]

            # =================================
            # FORECAST DATAFRAME
            # =================================
            pred_df = pd.DataFrame({
                "Date": future_dates,
                "Predicted Price": preds
            })

            # =================================
            # METRICS
            # =================================
            st.subheader("📊 Forecast Insights")

            change = (
                (preds[-1] - preds[0]) / preds[0]
            ) * 100

            col1, col2, col3 = st.columns(3)

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

            # =================================
            # RECOMMENDATION
            # =================================
            st.subheader("💡 Recommendation")

            if change > 1:
                st.success("BUY SIGNAL")

            elif change < -1:
                st.error("SELL SIGNAL")

            else:
                st.warning("HOLD POSITION")

            # =================================
            # CHART
            # =================================
            st.subheader("📈 Stock Forecast Chart")

            fig = go.Figure()

            # Actual prices
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Close"],
                mode="lines",
                name="Actual Price",
                line=dict(
                    color="white",
                    width=3
                )
            ))

            # Forecast prices
            fig.add_trace(go.Scatter(
                x=pred_df["Date"],
                y=pred_df["Predicted Price"],
                mode="lines",
                name="Forecast Price",
                line=dict(
                    color="#00FFAA",
                    width=3,
                    dash="dash"
                )
            ))

            # Layout
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="black",
                plot_bgcolor="black",
                font=dict(color="white"),
                xaxis_title="Date",
                yaxis_title="Stock Price",
                hovermode="x unified",
                height=600,
                legend=dict(
                    bgcolor="black"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================
            # FORECAST TABLE
            # =================================
            st.subheader("📅 Forecast Table")

            st.dataframe(pred_df)

            # =================================
            # DOWNLOAD
            # =================================
            csv = pred_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇ Download Forecast CSV",
                data=csv,
                file_name="forecast.csv",
                mime="text/csv"
            )

else:
    st.info("⬆ Upload a stock CSV file to start forecasting")