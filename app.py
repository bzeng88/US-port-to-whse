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
    # Load CSV or Excel
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

        # Create line data
        line_data = pd.DataFrame({
            "path": [[ [row["PortLon"], row["PortLat"]], [row["WhseLon"], row["WhseLat"]] ] for _, row in df.iterrows()],
            "color": df["color"]
        })

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
                    get_position="[PortLon, PortLat]",
                    get_color="color",
                    get_radius=50000,
                    pickable=True,
                    tooltip=True
                ),
                # Warehouses
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position="[WhseLon, WhseLat]",
                    get_color=[0, 0, 0],
                    get_radius=30000,
                    pickable=True,
                    tooltip=True
                ),
                # Lines connecting port to warehouse
                pdk.Layer(
                    "LineLayer",
                    data=line_data,
                    get_source_position="path[0]",
                    get_target_position="path[1]",
                    get_color="color",
                    get_width=5,
                ),
            ],
        ))

        st.write("Uploaded Data", df)

