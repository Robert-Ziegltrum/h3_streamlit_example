import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import pandas as pd
import h3

st.set_page_config(layout="wide")


st.sidebar.title("Contents")

st.sidebar.markdown("The H3 module  in Python is an implementation of Uber's H3 geospatial indexing system, which provides a way to spatially index locations on the Earth's surface. This system divides the world into a hierarchical grid of hexagons, which offers several advantages over traditional square grids for geospatial analysis, such as improved efficiency in spatial queries and better handling of spatial proximity.")
st.sidebar.markdown("See more info on the H3 page: [h3geo.org](https://h3geo.org/)")

st.sidebar.markdown("This app enables to interact with the different options of H3")
st.sidebar.markdown("1) Select a point to see the different hexagons by resolutions. Use the slider to see different granularities")
st.sidebar.markdown("2) Select a geofence to see the different hexagons by resolutions once the geofence is mapped to the hexagons. Use the slider to see different granularities")

st.sidebar.markdown("[Go to github](https://github.com/Robert-Ziegltrum)")

# Streamlit App
st.write("# H3 example app")

choice=st.selectbox("### Select an option",['Points', 'Geofences'])

col1, col2 = st.columns(2)

with col1: 

    st.write("## Select a map input")
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
    draw = Draw(
        draw_options={
            "polyline": False,
            "rectangle": False,
            "circle": False,
            "marker": True if choice=='Points' else False ,
            "circlemarker": False,
            "polygon": True if choice=='Geofences' else False,  
        },
        edit_options={"edit": True},
    )
    draw.add_to(m)
    output = st_folium(m, width=700, height=500)

    st.write("For usage of the app, select a point on the map.")
    with st.expander("Click to see the selected map input", expanded=False):
        st.write(output)


with col2:
    st.write("## H3 examples")
    selected_value = st.slider("Select the resultion", min_value=0, max_value=15, step=1)
    if output["last_active_drawing"] and "geometry" in output["last_active_drawing"]:
        with st.expander("Click to see the used geo data", expanded=False):
            st.json(output["last_active_drawing"]["geometry"])
        if choice=='Points':
            long = output["last_active_drawing"]["geometry"]["coordinates"][0]
            lat = output["last_active_drawing"]["geometry"]["coordinates"][1]

            if selected_value is not None:
                cell = h3.latlng_to_cell(lat, long, int(selected_value))
                st.write(f"## selected h3 cell: {cell}")
                polygon = h3.cell_to_boundary(cell)
                with st.expander("Click to see the geo points for the hexagon", expanded=False):
                    st.write(polygon)
                map_hexagon = folium.Map(location=[37.7749, -122.4194], zoom_start=12)  # Centered near San Francisco
                folium.Polygon(locations=polygon, color='blue', fill=True, fill_opacity=0.4).add_to(map_hexagon)
                folium.Marker([lat, long], popup='Selected Point').add_to(map_hexagon)
                map_hexagon.fit_bounds(polygon)
                st_folium(map_hexagon, width=700, height=500)
                area=h3.cell_area(cell)
                st.write(f"cell area: {area} sqm")
            else:
                st.write("select a hexagon resolution first to see the data")
        else:
            latlng_poly = h3.LatLngPoly([[lat, lon] for lon, lat in output["last_active_drawing"]["geometry"]["coordinates"][0]])
            data = {
                    "type": "Polygon",
                    "coordinates": latlng_poly
                    }
            cells = h3.polygon_to_cells(latlng_poly,selected_value)
            if cells:
                with st.expander("Click to see the hexagons as list", expanded=False):
                    st.write(cells)
            else: 
                st.write("no cells part of the drawn hexagon, select lower resolution")
            st.write("%(number_cells)d cells found in the hexgon with resolution %(resolution)d" % {'number_cells':len(cells), 'resolution':selected_value})
            map_hexagon = folium.Map(location=[37.7749, -122.4194], zoom_start=12)  # Centered near San Francisco
            for cell in cells:
                folium.Polygon(locations=h3.cell_to_boundary(cell), color='blue', fill=True, fill_opacity=0.4).add_to(map_hexagon)
            folium.Polygon(locations=[[lat, lon] for lon, lat in output["last_active_drawing"]["geometry"]["coordinates"][0]], color='red', fill=False).add_to(map_hexagon)
            st_folium(map_hexagon, width=700, height=500, key="unique_map_key")
    