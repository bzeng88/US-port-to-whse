import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Port to Warehouse Mapper", layout="wide")

st.title("Port to Warehouse Mapper")

uploaded_file = st.file_uploader("Upload CSV with Port Coordinates (Lat in Column A, Lon in Column B)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    if df.shape[1] < 2:
        st.error("CSV must have at least two columns: Latitude and Longitude.")
    else:
        df.columns = ["Latitude", "Longitude"] + list(df.columns[2:])  # Ensure naming
        
        # Let user pick colors for each port
        st.subheader("Customize Port Colors")
        colors = []
        for i in range(len(df)):
            color = st.color_picker(f"Pick color for Port {i+1} (Lat: {df['Latitude'][i]}, Lon: {df['Longitude'][i]})", "#FF0000")
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
            ],
        ))

        st.write("Uploaded Data", df)
