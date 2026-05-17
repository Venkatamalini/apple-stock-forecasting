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
PRIMARY = "#2563EB"      # Professional Blue
SECONDARY = "#059669"    # Market Green
ACCENT = "#DC2626"       # Financial Red

BG = "#FAFAFA"           # Off-White / Cream
CARD = "#FFFFFF"         # White Cards
TEXT = "#1F2937"         # Dark Gray Text

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

small {{
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

[data-testid="stDataFrame"] {{
    background-color: white !important;
}}

[data-testid="stDataFrame"] * {{
    color: {TEXT} !important;
}}

.ag-root-wrapper {{
    background-color: white !important;
}}

.ag-header {{
    background-color: #E5E7EB !important;
}}

.ag-header-cell-label {{
    color: {TEXT} !important;
    font-weight: bold !important;
}}

.ag-cell {{
    color: {TEXT} !important;
    background-color: white !important;
}}

.ag-menu {{
    background-color: white !important;
    color: {TEXT} !important;
}}

.ag-menu-option {{
    color: {TEXT} !important;
}}

.ag-menu-option:hover {{
    background-color: #F3F4F6 !important;
}}

.js-plotly-plot .plotly .legendtext {{
    fill: {TEXT} !important;
}}

.js-plotly-plot .plotly .xtick text {{
    fill: {TEXT} !important;
}}

.js-plotly-plot .plotly .ytick text {{
    fill: {TEXT} !important;
}}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================
st.title("📈 Apple Stock Price Forecasting")

st.markdown(
    "### AI-Powered Financial Forecast Dashboard"
)

# =========================================
# SIDEBAR
# =========================================
st.sidebar.title("⚙ Forecast Settings")

forecast_days = st.sidebar.slider(
    "Forecast Days",
    7,
    120,
    60
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
    # READ DATA
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
            "CSV must contain Close column"
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
            # STOCK GRAPH
            # =================================
            st.subheader(
                "📈 Historical vs Forecast Prices"
            )

            fig = go.Figure()

            # =================================
            # HISTORICAL PRICE
            # =================================
            fig.add_trace(go.Scatter(

                x=df["Date"],
                y=df["Close"],

                mode="lines",

                name="Historical Stock Price",

                line=dict(
                    color=PRIMARY,
                    width=3
                ),

                fill='tozeroy',

                fillcolor='rgba(37,99,235,0.08)',

                hovertemplate=
                "<b>Historical Stock Price</b><br>" +
                "Date: %{x}<br>" +
                "Price: $%{y:.2f}<extra></extra>"
            ))

            # =================================
            # FORECAST GRAPH
            # =================================
            fig.add_trace(go.Scatter(

                x=pred_df["Date"],
                y=pred_df["Predicted Price"],

                mode="lines",

                name="Predicted Stock Price",

                line=dict(
                    color=SECONDARY,
                    width=4,
                    dash="dash"
                ),

                hovertemplate=
                "<b>Predicted Stock Price</b><br>" +
                "Date: %{x}<br>" +
                "Forecast: $%{y:.2f}<extra></extra>"
            ))

            # =================================
            # FORECAST START MARKER
            # =================================
            fig.add_trace(go.Scatter(

                x=[pred_df["Date"].iloc[0]],
                y=[pred_df["Predicted Price"].iloc[0]],

                mode="markers+text",

                text=["Forecast Starts"],

                textposition="top center",

                marker=dict(
                    color=ACCENT,
                    size=12
                ),

                showlegend=False
            ))

            # =================================
            # LAYOUT
            # =================================
            fig.update_layout(

                paper_bgcolor="#FAFAFA",
                plot_bgcolor="#FFFFFF",

                height=700,

                hovermode="x unified",

                title=dict(
                    text="Apple Stock Price Forecast",
                    x=0.5,
                    font=dict(
                        size=28,
                        color=TEXT
                    )
                ),

                xaxis=dict(
                    title="Date",
                    color=TEXT,
                    showgrid=False
                ),

                yaxis=dict(
                    title="Stock Price ($)",
                    color=TEXT,
                    gridcolor="rgba(0,0,0,0.08)"
                ),

                legend=dict(
                    orientation="h",
                    y=1.02,
                    x=0.2,
                    font=dict(
                        color=TEXT,
                        size=14
                    ),
                    bgcolor="rgba(0,0,0,0)"
                ),

                font=dict(
                    color=TEXT,
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
            # CLICK-VIEW FORECAST TABLE
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
            # DOWNLOAD BUTTON
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