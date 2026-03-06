import streamlit as st
import pandas as pd
import folium
import requests
from folium.plugins import AntPath
from streamlit_folium import st_folium

# --- PAGE CONFIG ---
st.set_page_config(page_title="Textile Waste Colonialism", layout="centered")

# Inject CSS for background image and title styling
# Also constrain the main column width to keep the map/controls from expanding too wide.
st.markdown("""
    <style>
    .custom-header {
        position: relative;
        background-image: url('https://as2.ftcdn.net/v2/jpg/03/93/78/39/1000_F_393783937_QcOuNgRBxjxwtvsh0b2K3g253yOND8TU.jpg');
        background-size: cover;
        background-position: center;
        padding: 80px 20px 60px 20px;
        border-radius: 10px;
        margin-bottom: 25px;
    }

    .custom-header::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0, 0, 0, 0.4); /* semi-transparent overlay */
        z-index: 0;
        border-radius: 10px;
    }

    .custom-header h1 {
        position: relative;
        color: white;
        z-index: 1;
        font-size: 3em;
        text-align: center;
    }

    /* Keep the main content centered and prevent it from going too wide */
    section[data-testid="stAppViewContainer"] .main .block-container {
        max-width: 860px;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }
    </style>

    <div class="custom-header">
        <h1>Textile Industry and Fast Fashion</h1>
    </div>
""", unsafe_allow_html=True)

# --- PAGE NAVIGATION ---
# Tabs
tab_names = ["Home", "About", "Explore"]

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
            df.columns = [c.strip() for c in df.columns]
            
            for i in range(1, 6):
                country_col = f'r{i}_country'
                qty_col = f'r{i}_quantity' if f'r{i}_quantity' in df.columns else f'r{i}_uantity'
                
                if country_col in df.columns and qty_col in df.columns:
                    temp_df = df[['Year', country_col, qty_col]].copy()
                    temp_df.columns = ['Year', 'Destination', 'Quantity']
                    temp_df['Origin'] = origin
                    
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
tab1, tab2, tab3 = st.tabs(tab_names)

with tab1:
    # (Header injected above)
    st.markdown("""
    Inspiration for this project lies around 5,000 miles (8,000 kilometers) away from New York City, 
    in one of the oldest and driest deserts in the world – the Atacama Desert in northern Chile. 
    From a distance, mounts of clothing and textile scraps seemingly blend in with the dunes and dry hills in the landscape. 
    From up close, bright colors begin to stand out from discarded ripped jeans, leather boots, heals and old bracelets 
    against the warm desert sand.
    """, unsafe_allow_html=True)

    st.image("https://images.squarespace-cdn.com/content/v1/638a651ad5f9324e20972bf2/a742beba-d894-4432-a253-24581b4a5f5a/Hhl8cBqQ.jpg?format=2500w", caption="Photo by Antonio Cosio")

    st.markdown("""
    The *Cemetery of Clothes*, as the locals refer to it, is a reflection of the effects of overproduction, fast fashion 
    and a lack of policy regulations on the textile industry. An estimated **59,000 tons** of clothing and other textiles 
    are imported to Chile each year, of which almost **40,000** deemed 
    [irrecoverable](https://www.aljazeera.com/gallery/2021/11/8/chiles-desert-dumping-ground-for-fast-fashion-leftovers). 
    The growing piles permeate serious environmental impacts on the land, releasing toxic chemicals, like methane 
    and formaldehyde, and contaminating the ground with imparishable microplastics. Fast fashion clothing is mainly 
    made out of polyester (plastic), which is 
    [non-biodegradable](https://earth.org/fast-fashions-detrimental-effect-on-the-environment/). 
    With no proper management nor supervision, The Cemetery also presents an inevitable fire hazard as it spreads 
    across 741 acres (300 hectares) of arid land.
    """, unsafe_allow_html=True)

with tab2:
    st.header("About")
    st.markdown(
        """This project visualizes global textile waste exports and the connections between major exporters and their destinations.

- The map shows export flows by country and quantity.
- The data comes from public trade statistics and is simplified for visualization.

Use the **Explore** tab to interact with the map and see year-by-year trends.
"""
    )

with tab3:
    st.title("Global Flow of Worn Clothing")
    
    # UI Controls
    min_year, max_year = int(df_flows['Year'].min()), int(df_flows['Year'].max())
    year_options = sorted(list(range(min_year, max_year + 1)), reverse=True)

    # Default to 2024 if available, otherwise default to the latest year.
    default_year = 2024 if 2024 in year_options else year_options[0]
    selected_year = st.selectbox("Select Year", options=year_options, index=year_options.index(default_year))

    # Filter Data
    df_year = df_flows[df_flows['Year'] == selected_year]
    origin_country_names = sorted(df_year['Origin'].unique().tolist())

    origin_options = ["All"] + origin_country_names
    selected_origin = st.selectbox("Select origin country", options=origin_options, index=0)

    # Apply origin filter for table + map
    if selected_origin != "All":
        df_year = df_year[df_year['Origin'] == selected_origin]
        origin_country_names = [selected_origin]

    # Initialize Map
    # Zoom out slightly to ensure the full globe fits well in the centered layout.
    m = folium.Map(location=[20, 0], zoom_start=1.7, tiles='cartodb positron')
    
    # Helper to color lines by quantity
    def get_color(qty):
        if qty > 100000: return "#22223B"
        elif qty > 40000: return "#D98C5F"
        else: return '#8A9A5B'

    # GeoJSON overlay for origin country shading
    url = 'https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json'
    try:
        world_geo = requests.get(url).json()
        def style_function(feature):
            country_name = feature['properties']['name']
            if country_name in origin_country_names or country_name == "South Korea" and "Korea, Republic of" in origin_country_names:
                return {'fillColor': '#4062BB', 'color': 'none', 'weight': 0, 'fillOpacity': 0.6}
            else:
                return {'fillColor': 'none', 'color': 'none', 'weight': 0, 'fillOpacity': 0}

        folium.GeoJson(world_geo, style_function=style_function).add_to(m)
    except:
        pass # Silently fail if GitHub JSON is temporarily unreachable

    # Draw Nodes and Edges
    for origin in origin_country_names:
        origin_coords = COORDS.get(origin)
        dest_df = df_year[df_year['Origin'] == origin]
        
        if origin_coords:
            # 🚢 Origin marker
            total_qty = dest_df['Quantity'].sum()
            popup_html = folium.Popup(
                f"<div style='font-size:11px'><b>{origin}</b><br>Total Exported: {total_qty:,.0f} Tons 🚢</div>",
                max_width=200
            )
            marker_color = '#2F6690' if selected_origin != 'All' else '#D96C06'
            folium.CircleMarker(
                location=origin_coords, radius=7.5, color=marker_color, weight=2,
                fill=True, fill_color=marker_color, fill_opacity=0.9, popup=popup_html
            ).add_to(m)
            
            # Lines and destination markers
            # Using enumerate to create an idx for the offset logic
            for idx, row in enumerate(dest_df.itertuples()):
                dest_country = row.Destination
                qty = row.Quantity
                dest_coords_raw = COORDS.get(dest_country)
                
                if dest_coords_raw:
                    # Apply Offset / Jitter
                    offset_lat = 0.5 * ((idx % 3) - 1)
                    offset_lon = 0.5 * (((idx + 1) % 3) - 1)
                    dest_coords = [
                        dest_coords_raw[0] + offset_lat,
                        dest_coords_raw[1] + offset_lon
                    ]
                    
                    # AntPath Flow Line
                    AntPath(
                        locations=[origin_coords, dest_coords],
                        color=get_color(qty),
                        weight=3,
                        delay=800,
                        dash_array=[8, 20],
                        pulse_color='white'
                    ).add_to(m)

                    # Destination Marker
                    dest_color = '#2F6690' if selected_origin != 'All' else '#A3C9A8'
                    popup_html_dest = f"<div style='font-size:11px'><b>{dest_country}</b>: {qty:,.0f} Tons ⚠️"
                    folium.CircleMarker(
                        location=dest_coords, radius=4, color=dest_color,
                        fill=True, fill_color=dest_color, fill_opacity=0.7,
                        popup=folium.Popup(popup_html_dest, max_width=200)
                    ).add_to(m)

    # HTML Legend (responsive + styled)
    legend_html = """
    <div style="
        position: absolute;
        bottom: 24px; left: 24px;
        max-width: 240px;
        background: rgba(255,255,255,0.95);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        font-family: system-ui, sans-serif;
        font-size: 13px;
        line-height: 1.4;
        color: #222;
        z-index: 9999;
    ">
    <div style="font-weight: 700; margin-bottom: 8px;">Export Quantity</div>
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        <span style="width:14px; height:14px; border-radius:3px; background:#22223B; display:inline-block;"></span>
        <span>> 100,000 Tons</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        <span style="width:14px; height:14px; border-radius:3px; background:#D98C5F; display:inline-block;"></span>
        <span>40,000–100,000 Tons</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
        <span style="width:14px; height:14px; border-radius:3px; background:#8A9A5B; display:inline-block;"></span>
        <span>< 40,000 Tons</span>
    </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Map size
    st_folium(m, width=700, height=580)
    
    # Data Table
    st.markdown(f"### Flow Data for {selected_year}")
    st.dataframe(df_year.sort_values('Quantity', ascending=False).reset_index(drop=True), use_container_width=True)
