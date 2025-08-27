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
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        df = pd.read_excel(uploaded_file, header=None)

    if df.shape[1] < 4:
        st.error("File must have at least 4 columns: PortLat, PortLon, WhseLat, WhseLon")
    else:
        # Map columns
        df.columns = ["PortLat", "PortLon", "WhseLat", "WhseLon"] + list(df.columns[4:])

        # Ensure numeric
        for col in ["PortLat", "PortLon", "WhseLat", "WhseLon"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["PortLat", "PortLon", "WhseLat", "WhseLon"])

        if df.empty:
            st.error("No valid data found.")
        else:
            # Auto-generate colors for ports
            cmap = plt.cm.get_cmap("tab20", len(df))
            df["color"] = [list((cmap(i)[:3])) for i in range(len(df))]
            df["color"] = df["color"].apply(lambda x: [int(v*255) for v in x])

            # Build LineLayer as list of dicts
            line_data = [
                {
                    "source": [row["PortLon"], row["PortLat"]],
                    "target": [row["WhseLon"], row["WhseLat"]],
                    "color": row["color"]
                }
                for _, row in df.iterrows()
            ]

            # Map center & zoom
            center_lat = (df["PortLat"].mean() + df["WhseLat"].mean()) / 2
            center_lon = (df["PortLon"].mean() + df["WhseLon"].mean()) / 2

            st.subheader("Port to Warehouse Map")
            st.pydeck_chart(pdk.Deck(
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",  # free basemap
                initial_view_state=pdk.ViewState(
                    latitude=center_lat,
                    longitude=center_lon,
                    zoom=4,
                    pitch=0,
                ),
                layers=[
                    # Ports
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df,
                        get_position=["PortLon", "PortLat"],  # [lon, lat]
                        get_color="color",
                        get_radius=5000,
                        pickable=True,
                    ),
                    # Warehouses
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df,
                        get_position=["WhseLon", "WhseLat"],  # [lon, lat]
                        get_color=[0, 0, 0],
                        get_radius=3000,
                        pickable=True,
                    ),
                    # Lines connecting ports to warehouses
                    pdk.Layer(
                        "LineLayer",
                        data=line_data,
                        get_source_position="source",
                        get_target_position="target",
                        get_color="color",
                        get_width=2,
                    ),
                ],
            ))

            st.write("Uploaded Data", df)
