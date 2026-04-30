import pandas as pd
import folium
import json

df = pd.read_csv("geocoded_power4.csv")

school_col = "School"
city_cols = ["City 1", "City 2", "City 3"]

radius_meters = 60 * 1609.34

m = folium.Map(
    location=[39.5, -98.35],
    zoom_start=4,
    tiles="CartoDB positron"
)

circle_data = []

for _, row in df.iterrows():
    school = row[school_col]
    
    for i, city_col in enumerate(city_cols):   # i = 0,1,2
        lat_col = f"{city_col}_lat"
        lon_col = f"{city_col}_lon"

        if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
            circle_data.append({
                "school": school,
                "city": row[city_col],
                "lat": float(row[lat_col]),
                "lon": float(row[lon_col]),
                "level": i + 1   # 1, 2, or 3
            })

circle_json = json.dumps(circle_data)

school_options = "".join(
    sorted([f'<option value="{school}">{school}</option>' for school in df[school_col].dropna().unique()])
)

dropdown_html = f"""
<div style="
    position: fixed;
    top: 20px;
    left: 50px;
    z-index: 9999;
    background: white;
    padding: 10px;
    border: 2px solid gray;
    border-radius: 5px;
">
    <label><b>Select School:</b></label><br>
    <select id="schoolSelect" style="width: 220px;">
        <option value="all">All Schools</option>
        {school_options}
    </select>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {{

    var mapObj = {m.get_name()};
    var circles = [];
    var cityData = {circle_json};

    function getStyle(level) {{
        if (level === 1) {{
            return {{ color: "#08306b", fillColor: "#08306b", fillOpacity: 0.45 }};
        }}
        if (level === 2) {{
            return {{ color: "#2171b5", fillColor: "#2171b5", fillOpacity: 0.30 }};
        }}
        return {{ color: "#6baed6", fillColor: "#6baed6", fillOpacity: 0.20 }};
    }}

    function drawCircles(selectedSchool) {{
        circles.forEach(function(circle) {{
            mapObj.removeLayer(circle);
        }});
        circles = [];

        cityData.forEach(function(item) {{
            if (selectedSchool === "all" || item.school === selectedSchool) {{

                var style = getStyle(item.level);

                var circle = L.circle([item.lat, item.lon], {{
                    radius: {radius_meters},
                    color: style.color,
                    fillColor: style.fillColor,
                    fillOpacity: style.fillOpacity,
                    weight: 2
                }}).addTo(mapObj);

                circle.bindTooltip(item.school + " - " + item.city);
                circles.push(circle);
            }}
        }});
    }}

    document.getElementById("schoolSelect").addEventListener("change", function() {{
        drawCircles(this.value);
    }});

    setTimeout(function() {{
        drawCircles("all");
    }}, 500);

}});
</script>
"""
m.get_root().html.add_child(folium.Element(dropdown_html))

print("Number of circles:", len(circle_data))

m.save("school_city_radius_map.html")

print("Done! Saved as school_city_radius_map.html")