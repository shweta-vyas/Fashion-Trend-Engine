import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import time
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Fashion Trend Forecasting Engine",
    page_icon="✨"
)

# --- Custom CSS for Aesthetics ---
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #F0F2F6;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
    /* Metric card styling */
    .css-1r6slb0 {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    /* Chart and Dataframe container styling */
    .stPlotlyChart, .stDataFrame {
        border-radius: 10px;
        padding: 10px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border: 1px solid #E0E0E0;
    }
    /* Main title */
    h1 {
        color: #1E1E1E;
        font-weight: 600;
    }
    /* Section headers */
    h2, h3 {
        color: #333333;
        font-weight: 500;
    }
    /* Custom button style */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 10px 0;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- Keyword Data ---
TREND_CATEGORIES = {
    "Women's Fashion": {
        "Core Aesthetics": ["Cottagecore", "Quiet Luxury", "Y2K Fashion", "Balletcore", "Old Money Aesthetic"],
        "Apparel Pieces": ["Cargo Pants", "Wide Leg Jeans", "Blazer", "Slip Dress", "Corset Top"],
        "Brands": ["Skims", "Reformation", "Ganni", "Aritzia", "With Jean"],
        "Luxury Brands": ["Gucci", "Chanel", "Dior", "Prada", "Louis Vuitton", "Hermes"],
        "Accessories": ["Tote Bag", "Ballet Flats", "Statement Necklace", "Chunky Loafers", "Claw Clip"],
        "Colors": ["Hot Pink", "Lilac", "Chocolate Brown", "Sage Green", "Beige"],
    },
    "Men's Fashion": {
        "Core Aesthetics": ["Gorpcore", "Workwear", "Streetwear", "Classic Menswear", "Minimalism"],
        "Apparel Pieces": ["Cargo Shorts", "Linen Shirt", "Overshirt", "Pleated Trousers", "Polo Shirt"],
        "Brands": ["Carhartt", "Aimé Leon Dore", "Patagonia", "Fear of God", "Stone Island"],
        "Luxury Brands": ["Rolex", "Audemars Piguet", "Patek Philippe", "Gucci", "Louis Vuitton"],
        "Accessories": ["Tote Bag", "Crossbody Bag", "New Balance 550", "Vintage Watch", "Beanie"],
        "Colors": ["Olive Green", "Navy Blue", "Cream", "Burnt Orange", "Gray"],
    }
}

# --- Functions ---

@st.cache_data(ttl=3600)
def fetch_trends_data(keyword):
    """Fetches interest over time and regional interest for a single keyword."""
    print(f"Fetching new data for '{keyword}'...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
        interest_df = pytrends.interest_over_time()
        
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='US', gprop='')
        region_df = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
        
        time.sleep(1)
        
        if interest_df.empty: return None, None
            
        interest_df = interest_df.drop(columns=['isPartial'], errors='ignore')
        interest_df = interest_df.rename(columns={keyword: 'interest'})
        
        return interest_df, region_df.sort_values(by=keyword, ascending=False)
    except Exception as e:
        st.error(f"Could not fetch data for '{keyword}'. This can happen if the term has low search volume or if you've made too many requests recently. Please wait a few minutes and try again.")
        return None, None

def get_lifecycle_stage(data: pd.DataFrame):
    if data.empty or len(data) < 30:
        return "Not Enough Data", "Need at least 30 days of data to analyze."

    analysis_period = data.tail(90) if len(data) >= 90 else data
    last_30_days = data.tail(30)
    peak_value = data['interest'].max()
    current_value = last_30_days['interest'].mean()
    
    if current_value < peak_value * 0.4: stage, emoji = "Fading", "📉"
    elif current_value >= peak_value * 0.85: stage, emoji = "Peaking", "🏔️"
    elif current_value > analysis_period['interest'].mean(): stage, emoji = "Rising", "📈"
    else: stage, emoji = "Stable", "📊"
    
    provisional_note = " (Provisional)" if len(data) < 90 else ""
    return f"{emoji} {stage}{provisional_note}", f"Interest is {stage.lower()}."

def generate_forecast(data: pd.DataFrame):
    if data.empty or len(data) < 10: return None
    model = SimpleExpSmoothing(data['interest'], initialization_method="estimated").fit()
    forecast = model.forecast(4)
    last_date = data.index[-1]
    forecast_dates = pd.date_range(start=last_date, periods=5, freq='W')[1:]
    forecast_df = pd.DataFrame({'date': forecast_dates, 'forecast': forecast}).set_index('date')
    return forecast_df

# --- UI Layout ---

st.title("✨ Fashion Trend Forecasting Engine")

# --- Sidebar ---
st.sidebar.title("Controls")
main_category = st.sidebar.radio(
    "Select Fashion Category:",
    list(TREND_CATEGORIES.keys()),
    horizontal=True
)

sub_category = st.sidebar.selectbox(
    "Select Sub-Category:",
    list(TREND_CATEGORIES[main_category].keys())
)

selected_keyword = st.sidebar.selectbox(
    f"Select a Term from '{sub_category}':",
    TREND_CATEGORIES[main_category][sub_category]
)

# --- UPDATED: Added a button to trigger the analysis ---
if st.sidebar.button("Analyze Trend"):
    # --- Main Content ---
    with st.spinner(f"Fetching and analyzing data for '{selected_keyword}'..."):
        interest_data, region_data = fetch_trends_data(selected_keyword)

    if interest_data is not None:
        st.header(f"Analysis for: **{selected_keyword}**")
        st.markdown(f"Category: `{main_category} > {sub_category}`")

        stage, stage_desc = get_lifecycle_stage(interest_data)
        forecast_data = generate_forecast(interest_data)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Trend Lifecycle Stage", stage, help=stage_desc)
        with col2:
            if forecast_data is not None:
                current_interest = interest_data['interest'].iloc[-1]
                forecast_val = forecast_data['forecast'].iloc[0]
                delta = f"{round(((forecast_val - current_interest) / current_interest) * 100, 1)}%" if current_interest > 0 else "N/A"
                st.metric("Next Week's Forecast", f"{round(forecast_val)}", delta=delta, help="Forecasted change in interest vs. last week.")
        st.markdown("---")

        chart_col, region_col = st.columns([2, 1])

        with chart_col:
            st.subheader("Interest Over Time")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=interest_data.index, y=interest_data['interest'], mode='lines', name='Actual Interest', line=dict(color='#4A90E2', width=3)))
            if forecast_data is not None:
                fig.add_trace(go.Scatter(x=forecast_data.index, y=forecast_data['forecast'], mode='lines', name='Forecast', line=dict(color='#E57373', dash='dash')))

            fig.update_layout(
                title=dict(text="12-Month History & 4-Week Forecast", font=dict(size=16)),
                xaxis_title=None, yaxis_title="Relative Search Interest",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                margin=dict(l=0, r=20, t=40, b=0),
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(color='#333')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with region_col:
            st.subheader("Regional Hotspots")
            if region_data is not None and not region_data.empty:
                top_5_regions = region_data.head(5)
                
                region_fig = go.Figure(go.Bar(
                    x=top_5_regions[selected_keyword],
                    y=top_5_regions.index,
                    orientation='h',
                    marker=dict(color='#4A90E2', opacity=0.8)
                ))
                region_fig.update_layout(
                    title=dict(text="Top 5 US States", font=dict(size=16)),
                    xaxis_title="Relative Interest", yaxis_title=None,
                    margin=dict(l=0, r=0, t=40, b=0),
                    plot_bgcolor='white', paper_bgcolor='white',
                    yaxis=dict(autorange="reversed"),
                    font=dict(color='#333')
                )
                st.plotly_chart(region_fig, use_container_width=True)
            else:
                st.warning("No regional data available.")
else:
    st.info("Select a term and click 'Analyze Trend' to begin.")

