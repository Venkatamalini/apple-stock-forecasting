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
# PROFESSIONAL STOCK MARKET THEME
# =========================================
PRIMARY = "#2563EB"
SECONDARY = "#059669"
ACCENT = "#DC2626"

BG = "#FAFAFA"
TEXT = "#1F2937"

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
    background-color: #F3F4F6;
    border-right: 1px solid #D1D5DB;
}}

h1 {{
    color: {PRIMARY} !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}}

h2, h3 {{
    color: {TEXT} !important;
}}

p, label, div, span {{
    color: {TEXT} !important;
}}

section[data-testid="stFileUploader"] {{
    background-color: white;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #D1D5DB;
}}

section[data-testid="stFileUploader"] * {{
    color: {TEXT} !important;
}}

button[kind="primary"] {{
    background-color: {PRIMARY} !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 10px !important;
}}

.stDownloadButton button {{
    background-color: {SECONDARY} !important;
    color: white !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    height: 50px;
    width: 100%;
    font-size: 16px !important;
}}

div[data-testid="metric-container"] {{
    background-color: white;
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Prediction")

st.markdown(
    "### AI-Powered Financial Forecast Dashboard"
)

# =========================================
# SIDEBAR SETTINGS
# =========================================
st.sidebar.title("⚙️ Forecast Settings")

# =========================================
# FORECAST DAYS
# =========================================
st.sidebar.markdown("### Forecast Days")

forecast_days = st.sidebar.slider(
    "",
    min_value=7,
    max_value=120,
    value=60,
    key="forecast_slider"
)

st.sidebar.markdown("---")

# =========================================
# HISTORICAL DATA DAYS
# =========================================
st.sidebar.markdown("### Historical Data Days")

historical_days = st.sidebar.slider(
    "",
    min_value=1,
    max_value=3650,
    value=180,
    key="historical_slider"
)

st.sidebar.markdown(
    f"Showing last **{historical_days} days** of historical stock data."
)

# =========================================
# FILE UPLOAD
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
    # READ CSV
    # =====================================
    df = pd.read_csv(uploaded_file)

    # =====================================
    # DATASET PREVIEW
    # =====================================
    with st.expander(
        "📄 Click to View Dataset Preview"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )

    # =====================================
    # VALIDATION
    # =====================================
    if "Close" not in df.columns:

        st.error(
            "CSV must contain a Close column"
        )

    else:

        # =================================
        # DATE COLUMN
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

        # =================================
        # CLEAN DATA
        # =================================
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date")

        # =================================
        # CLOSE PRICE DATA
        # =================================
        close_prices = df["Close"].dropna().values

        if len(close_prices) < 2:

            st.error(
                "Not enough data for forecasting"
            )

        else:

            # =================================
            # FORECAST CALCULATION
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
            # STOCK MARKET GRAPH
            # =================================
            st.subheader("📈 Apple Stock Prediction")

            fig = go.Figure()

            historical_df = df.tail(historical_days)

            # =================================
            # HISTORICAL LINE
            # =================================
            fig.add_trace(go.Scatter(

                x=historical_df["Date"],

                y=historical_df["Close"],

                mode="lines",

                name="Historical Price",

                line=dict(
                    color="#2563EB",
                    width=2.5,
                    shape="linear"
                ),

                hovertemplate=
                "<b>Historical Price</b><br>" +
                "Date: %{x}<br>" +
                "Price: $%{y:.2f}<extra></extra>"
            ))

            # =================================
            # FORECAST LINE
            # =================================
            fig.add_trace(go.Scatter(

                x=pred_df["Date"],

                y=pred_df["Predicted Price"],

                mode="lines",

                name="Forecast Price",

                line=dict(
                    color="#059669",
                    width=3,
                    dash="dot",
                    shape="linear"
                ),

                hovertemplate=
                "<b>Forecast Price</b><br>" +
                "Date: %{x}<br>" +
                "Forecast: $%{y:.2f}<extra></extra>"
            ))

            # =================================
            # FORECAST START POINT
            # =================================
            fig.add_trace(go.Scatter(

                x=[pred_df["Date"].iloc[0]],

                y=[pred_df["Predicted Price"].iloc[0]],

                mode="markers",

                marker=dict(
                    color="#DC2626",
                    size=10
                ),

                name="Forecast Start"
            ))

            # =================================
            # GRAPH LAYOUT
            # =================================
            fig.update_layout(

                paper_bgcolor="#FAFAFA",

                plot_bgcolor="#FFFFFF",

                height=650,

                hovermode="x unified",

                title=dict(
                    text="Apple Inc. (AAPL)",
                    x=0.02,
                    font=dict(
                        size=26,
                        color="#111827"
                    )
                ),

                xaxis=dict(

                    title="Date",

                    showgrid=False,

                    color="#374151",

                    rangeslider=dict(
                        visible=False
                    )
                ),

                yaxis=dict(

                    title="Stock Price ($)",

                    color="#374151",

                    gridcolor="rgba(0,0,0,0.06)"
                ),

                legend=dict(

                    orientation="h",

                    y=1.12,

                    x=0.18,

                    bgcolor="rgba(255,255,255,0.85)",

                    bordercolor="#D1D5DB",

                    borderwidth=1,

                    font=dict(
                        size=12,
                        color="#111827"
                    )
                ),

                margin=dict(
                    l=40,
                    r=40,
                    t=150,
                    b=40
                ),

                font=dict(
                    family="Arial",
                    size=14,
                    color="#111827"
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
            with st.expander(
                "📅 Click to View Detailed Forecast Data"
            ):

                st.dataframe(

                    pred_df,

                    height=500,

                    use_container_width=True,

                    column_config={

                        "Date": st.column_config.DateColumn(
                            "Forecast Date",
                            format="DD-MM-YYYY"
                        ),

                        "Predicted Price": st.column_config.NumberColumn(
                            "Predicted Stock Price ($)",
                            format="$ %.2f"
                        )
                    }
                )

            # =================================
            # DOWNLOAD CSV
            # =================================
            csv = pred_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇ DOWNLOAD FORECAST CSV",
                data=csv,
                file_name="forecast.csv",
                mime="text/csv"
            )

else:

    st.info(
        "⬆ Upload a stock CSV file to begin forecasting"
    )