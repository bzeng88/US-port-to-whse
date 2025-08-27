import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(page_title="Port to Warehouse Mapper", layout="wide")

st.title("Port to Warehouse Mapper")

uploaded_file = st.file_uploader(
    "Upload CSV/Excel with Port Coordinates and Warehouse Zip (Lat in A, Lon in B, Warehouse Zip in C)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    # Handle CSV or Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if df.shape[1] < 3:
        st.error("File must have at least three columns: Latitude, Longitude, Warehouse Zip Code.")
    else:
        df.columns = ["Latitude", "Longitude", "WarehouseZip"] + list(df.columns[3:])  # Ensure naming

        # Auto-generate distinct colors
        cmap = plt.cm.get_cmap("tab20", len(df))
        df["color"] = [list((cmap(i)[:3])) for i in range(len(df))]
        df["color"] = df["color"].apply(lambda x: [int(v*255) for v in x])  # scale to 0-255

        # Plot using pydeck with free OSM/Carto basemap
        st.subheader("Port Map")
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
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
