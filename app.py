from flask import Flask, render_template, request
import openai
import os
import sys
import requests
import re

print(f"Starting FloodFactorApp in process id: {os.getpid()}, args: {sys.argv}")

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "your-google-api-key-here"
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID") or "your-google-cse-id-here"

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
                "sfha": attributes.get("SFHA_TF")
            }
        else:
            return None
    except Exception as e:
        print(f"Error fetching FEMA flood data: {e}")
        return None

def get_weather_alerts(lat, lon):
    try:
        url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
        headers = {"User-Agent": "FloodFactorApp (example@example.com)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        alerts = [
            {
                "title": alert.get("properties", {}).get("headline"),
                "description": alert.get("properties", {}).get("description"),
                "severity": alert.get("properties", {}).get("severity"),
                "area": alert.get("properties", {}).get("areaDesc"),
            }
            for alert in data.get("features", [])
            if "Flood" in alert.get("properties", {}).get("event", "")
        ]
        return alerts
    except Exception as e:
        print(f"Error fetching weather alerts: {e}")
        return []

def clean_markdown(text):
    if not text:
        return ""
    text = re.sub(r'###\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

def google_search(query, num_results=10):
    try:
        resp = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CSE_ID,
                "q": query,
                "num": num_results,
            }
        )
        results = resp.json()
        items = results.get("items", [])
        return [item.get("title") for item in items if "title" in item]
    except Exception as e:
        print(f"Google Search API error: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    explanation = None
    error = None
    likelihood_rating = None
    alerts = []

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
        alerts = get_weather_alerts(lat, lon)

        if not fema_data:
            base_prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet, "
                "but no FEMA zone data was found for this location. "
                "Please explain what a flood depth of this magnitude might typically mean in simple terms, "
                "including potential impacts on homes, safety, and travel."
            )
        else:
            base_prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet.\n"
                f"The FEMA flood zone for this area is {fema_data['flood_zone']}.\n"
                f"Base Flood Elevation (BFE): {fema_data['bfe']} ft.\n"
                f"Special Flood Hazard Area (SFHA): {'Yes' if fema_data['sfha'] == 'T' else 'No'}.\n\n"
                "Explain what this means in simple terms, including impacts on homes, safety, and how serious this flood depth would be in this area."
            )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": base_prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            explanation_raw = response.choices[0].message.content.strip()
            explanation = clean_markdown(explanation_raw)
        except Exception as e:
            error = f"OpenAI API error (explanation): {e}"
            return render_template("index.html", explanation=None, error=error)

        try:
            search_query = f"historical flood events near {lat},{lon}"
            titles = google_search(search_query, num_results=10)
            unique_titles = list(set(titles[:10]))

            likelihood_prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet.\n"
                f"FEMA flood zone: {fema_data['flood_zone'] if fema_data else 'unknown'}.\n"
                f"Base Flood Elevation (BFE): {fema_data['bfe'] if fema_data else 'unknown'} feet.\n"
                f"Special Flood Hazard Area: {'Yes' if fema_data and fema_data['sfha'] == 'T' else 'No or unknown'}.\n\n"
                f"Below are {len(unique_titles)} historical flood-related news articles about this location:\n"
                + "\n".join(f"- {title}" for title in unique_titles) +
                "\n\nBased on this, return ONLY the number rating (0–5) of flood likelihood at this location. Format: Rating: X"
            )

            response2 = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": likelihood_prompt}],
                temperature=0,
                max_tokens=50,
            )

            rating_text = response2.choices[0].message.content.strip()
            match = re.search(r"Rating:\s*([0-5])", rating_text)
            if match:
                likelihood_rating = int(match.group(1))

        except Exception as e:
            error = f"OpenAI API error (likelihood): {e}"

    return render_template(
        "index.html",
        explanation=explanation,
        error=error,
        likelihood_rating=likelihood_rating,
        alerts=alerts
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Running app on 0.0.0.0:{port} in process id: {os.getpid()}")
    app.run(host="0.0.0.0", port=port)
