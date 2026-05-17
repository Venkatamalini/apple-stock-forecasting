import streamlit as st
import pandas as pd
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
# COLORS
# =========================================
PRIMARY = "#ADADDE"
SECONDARY = "#DEADAD"
ACCENT = "#ADDEAD"

BG = "#0B0F19"
CARD = "#141A26"
TEXT = "#FFFFFF"

# =========================================
# CUSTOM CSS
# =========================================
st.markdown(f"""
<style>

html, body, [class*="css"] {{
    background-color: {BG};
    color: {TEXT};
}}

.stApp {{
    background-color: {BG};
}}

[data-testid="stSidebar"] {{
    background-color: {CARD};
}}

h1 {{
    color: {PRIMARY} !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}}

h2, h3 {{
    color: white !important;
}}

p, label, div {{
    color: white !important;
}}

div[data-testid="metric-container"] {{
    background-color: {CARD};
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 16px;
}}

.stDataFrame {{
    background-color: {CARD};
}}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Price Forecasting")
st.markdown(
    "### Modern AI-Powered Stock Prediction Dashboard"
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

        st.error(
            "CSV must contain a Close column"
        )

    else:

        # =================================
        # DATE HANDLING
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
            # MODERN GRAPH
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
                    width=4,
                    shape="spline"
                ),

                hovertemplate=
                "<b>Historical Price</b><br>" +
                "Date: %{x}<br>" +
                "Price: $%{y:.2f}<extra></extra>"
            ))

            # ---------------------------------
            # FORECAST PRICE
            # ---------------------------------
            fig.add_trace(go.Scatter(

                x=pred_df["Date"],
                y=pred_df["Predicted Price"],

                mode="lines+markers",

                name="Forecast",

                line=dict(
                    color=ACCENT,
                    width=4,
                    dash="dot",
                    shape="spline"
                ),

                marker=dict(
                    color=ACCENT,
                    size=7
                ),

                hovertemplate=
                "<b>Forecast</b><br>" +
                "Date: %{x}<br>" +
                "Forecast Price: $%{y:.2f}<extra></extra>"
            ))

            # ---------------------------------
            # FORECAST START MARKER
            # ---------------------------------
            fig.add_trace(go.Scatter(

                x=[pred_df["Date"].iloc[0]],
                y=[pred_df["Predicted Price"].iloc[0]],

                mode="markers+text",

                text=["Forecast Start"],

                textposition="top center",

                marker=dict(
                    color=SECONDARY,
                    size=12
                ),

                showlegend=False
            ))

            # =================================
            # LAYOUT
            # =================================
            fig.update_layout(

                paper_bgcolor=BG,
                plot_bgcolor=CARD,

                height=700,

                hovermode="x unified",

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
                    color="white",
                    showgrid=False
                ),

                yaxis=dict(
                    title="Stock Price ($)",
                    color="white",
                    gridcolor="rgba(255,255,255,0.08)"
                ),

                legend=dict(
                    bgcolor="rgba(0,0,0,0)",
                    orientation="h",
                    y=1.02,
                    x=0.3
                ),

                font=dict(
                    color="white",
                    size=14
                )
            )

            # =================================
            # SHOW GRAPH
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