import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(page_title="Port to Warehouse Mapper", layout="wide")
st.title("Port to Warehouse Mapper")

uploaded_file = st.file_uploader(
    "Upload CSV/Excel with Port Lat, Port Lon, Warehouse Lat, Warehouse Lon",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if df.shape[1] < 4:
        st.error("File must have at least four columns: PortLat, PortLon, WhseLat, WhseLon")
    else:
        df.columns = ["PortLat", "PortLon", "WhseLat", "WhseLon"] + list(df.columns[4:])

        # Auto-generate distinct colors
        cmap = plt.cm.get_cmap("tab20", len(df))
        df["color"] = [list((cmap(i)[:3])) for i in range(len(df))]
        df["color"] = df["color"].apply(lambda x: [int(v*255) for v in x])

        # Precompute positions for LineLayer
        df["source"] = df.apply(lambda row: [row["PortLon"], row["PortLat"]], axis=1)
        df["target"] = df.apply(lambda row: [row["WhseLon"], row["WhseLat"]], axis=1)

        st.subheader("Port to Warehouse Map")
        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(
                latitude=df["PortLat"].mean(),
                longitude=df["PortLon"].mean(),
                zoom=3,
                pitch=0,
            ),
            layers=[
                # Ports
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position="source",
                    get_color="color",
                    get_radius=50000,
                    pickable=True,
                ),
                # Warehouses
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position="target",
                    get_color=[0, 0, 0],
                    get_radius=30000,
                    pickable=True,
                ),
                # Lines connecting each port to its warehouse
                pdk.Layer(
                    "LineLayer",
                    data=df,
                    get_source_position="source",
                    get_target_position="target",
                    get_color="color",
                    get_width=5,
                ),
            ],
        ))

        st.write("Uploaded Data", df)
