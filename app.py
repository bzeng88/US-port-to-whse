import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        df.columns = ["PortLat", "PortLon", "WhseLat", "WhseLon"]

        # Ensure numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna()

        if df.empty:
            st.error("No valid data found.")
        else:
            # Generate colors for each port
            cmap = plt.cm.get_cmap("tab20", len(df))
            df["color"] = [f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)})" for c in cmap.colors[:len(df)]]

            # Create Plotly figure
            fig = go.Figure()

            # Plot ports
            fig.add_trace(go.Scattermapbox(
                lat=df["PortLat"],
                lon=df["PortLon"],
                mode="markers",
                marker=dict(size=10, color=df["color"]),
                name="Ports"
            ))

            # Plot warehouses
            fig.add_trace(go.Scattermapbox(
                lat=df["WhseLat"],
                lon=df["WhseLon"],
                mode="markers",
                marker=dict(size=10, color="black"),
                name="Warehouses"
            ))

            # Draw lines for each port → warehouse
            for i, row in df.iterrows():
                fig.add_trace(go.Scattermapbox(
                    lat=[row["PortLat"], row["WhseLat"]],
                    lon=[row["PortLon"], row["WhseLon"]],
                    mode="lines",
                    line=dict(width=2, color=row["color"]),
                    showlegend=False
                ))

            # Set layout
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=4,
                mapbox_center={"lat": df["PortLat"].mean(), "lon": df["PortLon"].mean()},
                margin={"l":0,"r":0,"t":0,"b":0}
            )

            st.subheader("Port to Warehouse Map")
            st.plotly_chart(fig, use_container_width=True)
            st.write("Uploaded Data", df)
