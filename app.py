from flask import Flask, render_template, request
import openai
import os
import sys
import requests
import re
from web import run  # for internet search

print(f"Starting FloodFactorApp in process id: {os.getpid()}, args: {sys.argv}")

app = Flask(__name__)

# Your OpenAI API key setup
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

def clean_markdown(text):
    if not text:
        return ""
    # Remove markdown syntax: ###, **, *, -, etc.
    text = re.sub(r'###\s*', '', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n\n', text)  # Clean up excessive spacing
    return text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    explanation = None
    error = None
    likelihood_rating = None
    likelihood_explanation = None

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

        # Get FEMA flood data
        fema_data = get_fema_flood_data(lat, lon)

        # Generate flood facts explanation prompt
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

        # Use web search to find historical flood events nearby for better likelihood rating
        try:
            search_results = run({
                "search_query": [
                    {
                        "q": f"historical flood events near {lat},{lon}",
                        "recency": 3650,  # approx 10 years
                    }
                ]
            })

            titles = [res["title"] for res in search_results.get("search_query_results", [])]
            unique_titles = list(set(titles[:10]))
            event_count = len(unique_titles)

            likelihood_prompt = (
                f"A user at latitude {lat} and longitude {lon} is concerned about a flood depth of {user_depth} feet.\n"
                f"FEMA flood zone: {fema_data['flood_zone'] if fema_data else 'unknown'}.\n"
                f"Base Flood Elevation (BFE): {fema_data['bfe'] if fema_data else 'unknown'} feet.\n"
                f"Special Flood Hazard Area: {'Yes' if fema_data and fema_data['sfha'] == 'T' else 'No or unknown'}.\n\n"
                f"Below are {event_count} recent flood-related news article titles near this location:\n"
                + "\n".join(f"- {title}" for title in unique_titles) +
                "\n\nBased on these events and the flood depth, rate the likelihood of such a flood occurring from 0 (Highly unlikely) to 5 (Definitive).\n"
                "Return ONLY the number rating and a brief explanation.\n"
                "Format:\nRating: X\nExplanation: your text here"
            )

            response2 = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": likelihood_prompt}],
                temperature=0,
                max_tokens=150,
            )

            rating_text = response2.choices[0].message.content.strip()
            rating_match = re.search(r"Rating:\s*([0-5])", rating_text)
            explanation_match = re.search(r"Explanation:\s*(.*)", rating_text, re.DOTALL)

            if rating_match:
                likelihood_rating = int(rating_match.group(1))
            if explanation_match:
                likelihood_explanation = clean_markdown(explanation_match.group(1).strip())

        except Exception as e:
            error = f"OpenAI API error (likelihood): {e}"

    return render_template(
        "index.html",
        explanation=explanation,
        error=error,
        likelihood_rating=likelihood_rating,
        likelihood_explanation=likelihood_explanation,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Running app on 0.0.0.0:{port} in process id: {os.getpid()}")
    app.run(host="0.0.0.0", port=port)
