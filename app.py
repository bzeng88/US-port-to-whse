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
        # Rename columns
        df.columns = ["PortLat", "PortLon", "WhseLat", "WhseLon"] + list(df.columns[4:])

        # Convert to numeric and drop invalid values
        for col in ["PortLat", "PortLon", "WhseLat", "WhseLon"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows with NaNs
        df = df.dropna(subset=["PortLat", "PortLon", "WhseLat", "WhseLon"])

        # Clamp coordinates to US bounds
        df = df[
            (df["PortLat"] >= 24.5) & (df["PortLat"] <= 49.5) &
            (df["WhseLat"] >= 24.5) & (df["WhseLat"] <= 49.5) &
            (df["PortLon"] >= -125) & (df["PortLon"] <= -66.5) &
            (df["WhseLon"] >= -125) & (df["WhseLon"] <= -66.5)
        ]

        if df.empty:
            st.error("No valid US coordinates found in the uploaded file.")
        else:
            # Warn if any rows were dropped
            dropped = len(df) - len(df)
            if dropped > 0:
                st.warning(f"Dropped {dropped} rows outside US bounds or with invalid coordinates.")

            # Auto-generate distinct colors
            cmap = plt.cm.get_cmap("tab20", len(df))
            df["color"] = [list((cmap(i)[:3])) for i in range(len(df))]
            df["color"] = df["color"].apply(lambda x: [int(v*255) for v in x])

            # Prepare LineLayer data
            line_df = pd.DataFrame({
                "src_lon": df["PortLon"],
                "src_lat": df["PortLat"],
                "tgt_lon": df["WhseLon"],
                "tgt_lat": df["WhseLat"],
                "color": df["color"]
            })

            # Compute map center and zoom
            min_lat, max_lat = min(df["PortLat"].min(), df["WhseLat"].min()), max(df["PortLat"].max(), df["WhseLat"].max())
            min_lon, max_lon = min(df["PortLon"].min(), df["WhseLon"].min()), max(df["PortLon"].max(), df["WhseLon"].max())

            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2

            # Zoom level based on spread
            lat_span = max_lat - min_lat
            lon_span = max_lon - min_lon
            max_span = max(lat_span, lon_span)
            if max_span < 0.01:
                zoom_level = 13
            elif max_span < 0.05:
                zoom_level = 11
            elif max_span < 0.2:
                zoom_level = 10
            elif max_span < 1:
                zoom_level = 8
            else:
                zoom_level = 5

            st.subheader("Port to Warehouse Map")
            st.pydeck_chart(pdk.Deck(
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                initial_view_state=pdk.ViewState(
                    latitude=center_lat,
                    longitude=center_lon,
                    zoom=zoom_level,
                    pitch=0,
                ),
                layers=[
                    # Ports
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df,
                        get_position=["PortLon", "PortLat"],
                        get_color="color",
                        get_radius=5000,
                        pickable=True,
                    ),
                    # Warehouses
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=df,
                        get_position=["WhseLon", "WhseLat"],
                        get_color=[0, 0, 0],
                        get_radius=3000,
                        pickable=True,
                    ),
                    # Lines connecting each port to its warehouse
                    pdk.Layer(
                        "LineLayer",
                        data=line_df,
                        get_source_position=["src_lon", "src_lat"],
                        get_target_position=["tgt_lon", "tgt_lat"],
                        get_color="color",
                        get_width=2,
                    ),
                ],
            ))

            st.write("Uploaded Data", df)
