import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Port to Warehouse Mapper", layout="wide")

st.title("Port to Warehouse Mapper")

uploaded_file = st.file_uploader("Upload CSV with Port Coordinates and Warehouse Zip (Lat in A, Lon in B, Warehouse Zip in C)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    if df.shape[1] < 3:
        st.error("CSV must have at least three columns: Latitude, Longitude, Warehouse Zip Code.")
    else:
        df.columns = ["Latitude", "Longitude", "WarehouseZip"] + list(df.columns[3:])  # Ensure naming
        
        # Let user pick colors for each port
        st.subheader("Customize Port Colors")
        colors = []
        for i in range(len(df)):
            color = st.color_picker(f"Pick color for Port {i+1} (Lat: {df['Latitude'][i]}, Lon: {df['Longitude'][i]}, Warehouse: {df['WarehouseZip'][i]})", "#FF0000")
            rgb = tuple(int(color.lstrip("#")[j:j+2], 16) for j in (0, 2, 4))
            colors.append(rgb)
        df["color"] = colors

        # Plot using pydeck
        st.subheader("Port Map")
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=df["Latitude"].mean(),
                longitude=df["Longitude"].mean(),
                zoom=3,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position="[Longitude, Latitude]",
                    get_color="color",
                    get_radius=50000,
                ),
                pdk.Layer(
                    "TextLayer",
                    data=df,
                    get_position="[Longitude, Latitude]",
                    get_text="WarehouseZip",
                    get_color=[0, 0, 0],
                    get_size=16,
                ),
            ],
        ))

        st.write("Uploaded Data", df)
