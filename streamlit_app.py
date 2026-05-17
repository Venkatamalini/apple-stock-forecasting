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
# CUSTOM UI COLORS
# =========================================
PRIMARY = "#ADADDE"
SECONDARY = "#DEADAD"
ACCENT = "#ADDEAD"

# =========================================
# CUSTOM STYLING
# =========================================
st.markdown(f"""
<style>

html, body, [class*="css"] {{
    background-color: #0F1117;
    color: white;
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: #0F1117;
}}

[data-testid="stSidebar"] {{
    background-color: #161A23;
    border-right: 1px solid rgba(255,255,255,0.1);
}}

h1 {{
    color: {PRIMARY};
    font-size: 42px !important;
    font-weight: 800 !important;
}}

h2, h3 {{
    color: white;
}}

div[data-testid="metric-container"] {{
    background: #161A23;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 18px;
}}

.stButton>button {{
    background-color: {PRIMARY};
    color: black;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}}

.stDownloadButton>button {{
    background-color: {ACCENT};
    color: black;
    border-radius: 10px;
    border: none;
    font-weight: 700;
}}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Price Forecasting")
st.markdown(
    "### Modern AI-Based Stock Prediction Dashboard"
)

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("⚙ Forecast Settings")

forecast_days = st.sidebar.slider(
    "Forecast Days",
    7,
    90,
    30
)

# =========================================
# FILE UPLOADER
# =========================================
uploaded_file = st.file_uploader(
    "📂 Upload Stock CSV File",
    type=["csv"]
)

# =========================================
# MAIN APP
# =========================================
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
    if "Close" not in df.columns:

        st.error("CSV must contain a Close column")

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
            # FORECAST LOGIC
            # =================================
            last_price = close_prices[-1]

            trend = (
                close_prices[-1]
                - close_prices[-2]
            )

            preds = []

            next_price = last_price

            for _ in range(forecast_days):

                next_price += trend

                preds.append(
                    round(next_price, 2)
                )

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
                (preds[-1] - preds[0])
                / preds[0]
            ) * 100

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Expected Change",
                    f"{change:.2f}%"
                )

            with col2:

                st.metric(
                    "Highest Price",
                    f"${max(preds):.2f}"
                )

            with col3:

                st.metric(
                    "Lowest Price",
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
            # MODERN STOCK GRAPH
            # =================================
            st.subheader("📈 Stock Forecast Chart")

            fig = go.Figure()

            # ---------------------------------
            # HISTORICAL STOCK PRICE
            # ---------------------------------
            fig.add_trace(go.Scatter(

                x=df["Date"],
                y=df["Close"],

                mode="lines",

                name="Historical Price",

                line=dict(
                    color=PRIMARY,
                    width=3
                ),

                fill='tozeroy',

                fillcolor='rgba(173,173,222,0.08)',

                hovertemplate=
                "<b>Historical Price</b><br>" +
                "Date: %{x}<br>" +
                "Price: $%{y:.2f}<extra></extra>"
            ))

            # ---------------------------------
            # FORECAST LINE
            # ---------------------------------
            fig.add_trace(go.Scatter(

                x=pred_df["Date"],
                y=pred_df["Predicted Price"],

                mode="lines+markers",

                name="Forecast",

                line=dict(
                    color=ACCENT,
                    width=4,
                    dash="dash"
                ),

                marker=dict(
                    size=7,
                    color=ACCENT
                ),

                hovertemplate=
                "<b>Forecast Price</b><br>" +
                "Date: %{x}<br>" +
                "Forecast: $%{y:.2f}<extra></extra>"
            ))

            # ---------------------------------
            # SPLIT LINE
            # ---------------------------------
            fig.add_vline(
                x=pred_df["Date"].iloc[0],
                line_width=2,
                line_dash="dot",
                line_color=SECONDARY
            )

            # =================================
            # LAYOUT
            # =================================
            fig.update_layout(

                paper_bgcolor="#0F1117",
                plot_bgcolor="#161A23",

                height=700,

                title=dict(
                    text="Apple Stock Forecast Trend",
                    x=0.5,
                    font=dict(
                        size=26,
                        color="white"
                    )
                ),

                xaxis=dict(
                    title="Date",
                    showgrid=False,
                    color="white"
                ),

                yaxis=dict(
                    title="Stock Price ($)",
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.06)",
                    color="white"
                ),

                hovermode="x unified",

                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0)"
                ),

                font=dict(
                    color="white",
                    size=14
                )
            )

            # =================================
            # DISPLAY GRAPH
            # =================================
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
            # DOWNLOAD BUTTON
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

    st.info(
        "⬆ Upload a stock CSV file to begin forecasting"
    )