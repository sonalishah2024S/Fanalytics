import pandas as pd
import folium
import json

df = pd.read_csv("geocoded_power4.csv")

school_col = "School"
city_cols = ["City 1", "City 2", "City 3"]

# IMPORTANT: make sure this column exists from your clustering step
genotype_col = "Archetype"

m = folium.Map(
    location=[39.5, -98.35],
    zoom_start=4,
    tiles="CartoDB positron"
)

circle_data = []

for _, row in df.iterrows():
    school = row[school_col]
    genotype = row.get(genotype_col, "Unknown")

    for i, city_col in enumerate(city_cols):
        lat_col = f"{city_col}_lat"
        lon_col = f"{city_col}_lon"

        if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
            circle_data.append({
                "school": school,
                "city": row[city_col],
                "lat": float(row[lat_col]),
                "lon": float(row[lon_col]),
                "level": i + 1,
                "genotype": genotype
            })

circle_json = json.dumps(circle_data)

school_options = "".join(
    sorted([f'<option value="{school}">{school}</option>' 
            for school in df[school_col].dropna().unique()])
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

    function getColor(genotype) {{
        if (genotype === "National Powerhouses") return "#d73027";
        if (genotype === "Regional Loyalists") return "#1a9850";
        if (genotype === "Spectator Fans") return "#4575b4";
        if (genotype === "Selective Affluents") return "#fdae61";
        if (genotype === "Debbie Downers") return "#984ea3";
        return "#999999";
    }}

    function getRadius(level) {{
        if (level === 1) return 120000;
        if (level === 2) return 80000;
        return 50000;
    }}

    function drawCircles(selectedSchool) {{
        circles.forEach(function(circle) {{
            mapObj.removeLayer(circle);
        }});
        circles = [];

        cityData.forEach(function(item) {{
            if (selectedSchool === "all" || item.school === selectedSchool) {{

                var color = getColor(item.genotype);

                var circle = L.circle([item.lat, item.lon], {{
                    radius: getRadius(item.level),
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.35,
                    weight: 2
                }}).addTo(mapObj);

                circle.bindPopup(
                    "<b>" + item.school + "</b><br>" +
                    "City: " + item.city + "<br>" +
                    "Rank: " + item.level + "<br>" +
                    "Fanbase Type: " + item.genotype
                );

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
    var legend = L.control({{position: 'bottomright'}});
    legend.onAdd = function () {{
        var div = L.DomUtil.create('div', 'info legend');
        div.style.background = "white";
        div.style.padding = "10px";
        div.style.border = "2px solid gray";

        div.innerHTML += "<b>Fanbase Types</b><br>";
        div.innerHTML += "<i style='background:#d73027;width:10px;height:10px;display:inline-block;'></i> Powerhouses<br>";
        div.innerHTML += "<i style='background:#1a9850;width:10px;height:10px;display:inline-block;'></i> Regional Loyalists<br>";
        div.innerHTML += "<i style='background:#4575b4;width:10px;height:10px;display:inline-block;'></i> Spectator Fans<br>";
        div.innerHTML += "<i style='background:#fdae61;width:10px;height:10px;display:inline-block;'></i> Selective Affluents<br>";
        div.innerHTML += "<i style='background:#984ea3;width:10px;height:10px;display:inline-block;'></i> Debbie Downers<br>";

        return div;
    }};
    legend.addTo(mapObj);

}});
</script>
"""

m.get_root().html.add_child(folium.Element(dropdown_html))

m.save("school_city_radius_map_improved.html")

print("Done! Improved map saved.")
