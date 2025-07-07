from flask import Flask, render_template, request
import openai
import os
import sys
import requests

print(f"Starting FloodFactorApp in process id: {os.getpid()}, args: {sys.argv}")

app = Flask(__name__)

# Your OpenAI API key setup (set as env variable or replace below)
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

def get_fema_flood_data(lat, lon):
    try:
        url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/0/query"
        params = {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("features"):
            attributes = data["features"][0]["attributes"]
            return {
                "flood_zone": attributes.get("FLD_ZONE"),
                "bfe": attributes.get("STATIC_BFE"),
                "sfha": attributes.get("SFHA_TF")  # "T" or "F"
            }
        else:
            return None
    except Exception as e:
        print(f"Error fetching FEMA flood data: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    explanation = None
    error = None

    if request.method == "POST":
        lat_str = request.form.get("latitude", "").strip()
        lon_str = request.form.get("longitude", "").strip()
        depth_str = request.form.get("depth", "").strip()

        try:
            lat = float(lat_str)
            lon = float(lon_str)
            user_depth = float(depth_str)
        except ValueError:
            error = "Please enter valid numbers for latitude, longitude, and flood depth."
            return render_template("index.html", explanation=None, error=error)

        fema_data = get_fema_flood_data(lat, lon)

        if not fema_data:
            prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet, "
                "but no FEMA zone data was found for this location. "
                "Please explain what a flood depth of this magnitude might typically mean in simple terms, "
                "including potential impacts on homes, safety, and travel."
            )
        else:
            prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet.\n"
                f"The FEMA flood zone for this area is {fema_data['flood_zone']}.\n"
                f"Base Flood Elevation (BFE): {fema_data['bfe']} ft.\n"
                f"Special Flood Hazard Area (SFHA): {'Yes' if fema_data['sfha'] == 'T' else 'No'}.\n\n"
                "Explain what this means in simple terms, including impacts on homes, safety, and how serious this flood depth would be in this area."
            )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            explanation = response.choices[0].message.content.strip()
        except Exception as e:
            error = f"OpenAI API error: {e}"

    return render_template("index.html", explanation=explanation, error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Running app on 0.0.0.0:{port} in process id: {os.getpid()}")
    app.run(host="0.0.0.0", port=port)
