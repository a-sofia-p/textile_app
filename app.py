import streamlit as st
import pandas as pd
import folium
from folium.plugins import AntPath
from streamlit_folium import st_folium

# --- PAGE CONFIG ---
st.set_page_config(page_title="Textile Waste Colonialism", layout="wide")

# --- COLOR PALETTE ---
COLORS = {
    'dark_bg': '#22223B',
    'origin': '#D96C06',      # Orange
    'dest_high': '#D98C5F',   # Light Orange
    'dest_mid': '#8A9A5B',    # Olive Green
    'dest_low': '#A3C9A8',    # Light Green
    'lines': '#4062BB'        # Blue
}

# --- HARDCODED COORDINATES ---
COORDS = {
    "United States of America": [37.0902, -95.7129], "Canada": [56.1304, -106.3468],
    "Germany": [51.1657, 10.4515], "China": [35.8617, 104.1954],
    "Korea, Republic of": [35.9078, 127.7669], "Japan": [36.2048, 138.2529],
    "United Kingdom": [55.3781, -3.4360], "India": [20.5937, 78.9629],
    "Kenya": [-1.286389, 36.817223], "Pakistan": [30.3753, 69.3451],
    "Tanzania": [-6.3690, 34.8888], "Ghana": [7.9465, -1.0232],
    "Madagascar": [-18.7669, 46.8691], "Angola": [-11.2027, 17.8739],
    "Nigeria": [9.0820, 8.6753], "Mozambique": [-18.6657, 35.5296],
    "Philippines": [12.8797, 121.7740], "Benin": [9.3077, 2.3158],
    "Guatemala": [15.7835, -90.2308], "Chile": [-35.6751, -71.5430],
    "Honduras": [15.2000, -86.2419], "Poland": [51.9194, 19.1451],
    "United Arab Emirates": [23.4241, 53.8478], "Ukraine": [48.3794, 31.1656],
    "Cambodia": [12.5657, 104.9910], "Malaysia": [4.2105, 101.9758],
    "Iraq": [33.2232, 43.6793]
}

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data():
    files = {
        "United States of America": "data/USA_exports.csv",
        "China": "data/China_exports.csv",
        "Germany": "data/Germany_exports.csv",
        "Korea, Republic of": "data/Korea_exports.csv",
        "Japan": "data/Japan_exports.csv",
        "United Kingdom": "data/UK_exports.csv"   
    }
    
    all_data = []
    
    for origin, filepath in files.items():
        try:
            df = pd.read_csv(filepath)
            
            # Clean column names
            df.columns = [c.strip() for c in df.columns]
            
            # Extract ranks (r1 to r5)
            for i in range(1, 6):
                country_col = f'r{i}_country'
                qty_col = f'r{i}_quantity' if f'r{i}_quantity' in df.columns else f'r{i}_uantity'
                
                if country_col in df.columns and qty_col in df.columns:
                    temp_df = df[['Year', country_col, qty_col]].copy()
                    temp_df.columns = ['Year', 'Destination', 'Quantity']
                    temp_df['Origin'] = origin
                    
                    # Clean data: remove commas, strip spaces, drop NAs
                    temp_df['Destination'] = temp_df['Destination'].astype(str).str.strip()
                    temp_df['Quantity'] = temp_df['Quantity'].astype(str).str.replace(',', '', regex=True)
                    temp_df['Quantity'] = pd.to_numeric(temp_df['Quantity'], errors='coerce')
                    
                    all_data.append(temp_df)
        except Exception as e:
            st.error(f"Error loading {filepath}: {e}")
            
    long_df = pd.concat(all_data, ignore_index=True).dropna()
    return long_df

df_flows = load_and_clean_data()

# --- APP NAVIGATION ---
tab1, tab2 = st.tabs(["🏜️ The Atacama Context", "🌍 Explore Waste Flows"])

with tab1:
    st.title("Textile Waste Colonialism")
    st.markdown("### The Desert of Fast Fashion")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        The Atacama Desert in Chile has become one of the world's most visible dumping grounds for fast fashion. 
        Every year, tens of thousands of tons of unsold or second-hand clothing from the Global North 
        (US, Europe, Asia) arrive in ports, only to be illegally dumped in the desert.
        
        This project tracks the **Top 5 Global Exporters** of worn clothing and maps where their waste flows 
        over a decade (2015-2024). It reveals a stark reality: the burden of textile waste is systematically 
        pushed onto nations in the Global South.
        """)
    with col2:
        # Placeholder for an image of the Atacama dump
        st.image("https://images.unsplash.com/photo-1611288875782-9e906b3a9926?q=80&w=600&auto=format&fit=crop", caption="Textile waste accumulating in natural landscapes.")

with tab2:
    st.title("Global Flow of Worn Clothing")
    
    # Year Slider
    min_year, max_year = int(df_flows['Year'].min()), int(df_flows['Year'].max())
    selected_year = st.slider("Select Year", min_year, max_year, min_year, step=1)
    
    # Filter data by year
    df_year = df_flows[df_flows['Year'] == selected_year]
    
    # Map Initialization
    m = folium.Map(location=[20, 0], zoom_start=2.1, tiles='cartodb dark_matter')
    
    # Draw Flows
    for origin in df_year['Origin'].unique():
        origin_coord = COORDS.get(origin)
        
        if origin_coord:
            # Origin Marker
            folium.CircleMarker(
                location=origin_coord, radius=6, color=COLORS['origin'],
                fill=True, fill_color=COLORS['origin'], fill_opacity=0.9,
                popup=f"<b>{origin}</b>"
            ).add_to(m)
            
            # Destinations for this origin
            dest_df = df_year[df_year['Origin'] == origin]
            for idx, row in dest_df.iterrows():
                dest = row['Destination']
                qty = row['Quantity']
                dest_coord = COORDS.get(dest)
                
                if dest_coord:
                    # AntPath for flow animation
                    AntPath(
                        locations=[origin_coord, dest_coord],
                        color=COLORS['lines'], weight=max(2, qty / 20000),
                        dash_array=[10, 20], pulse_color='white', delay=800
                    ).add_to(m)
                    
                    # Destination Marker
                    folium.CircleMarker(
                        location=dest_coord, radius=4, color=COLORS['dest_high'],
                        fill=True, fill_color=COLORS['dest_high'], fill_opacity=0.8,
                        popup=f"<b>{dest}</b><br>Imported: {qty:,.0f} Tons"
                    ).add_to(m)
    
    # Render Map
    st_folium(m, width=1000, height=600)
    
    # Data Table underneath
    st.markdown(f"### Top Flows in {selected_year}")
    st.dataframe(df_year.sort_values('Quantity', ascending=False).reset_index(drop=True))
