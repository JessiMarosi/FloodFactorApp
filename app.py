from flask import Flask, render_template, request
import openai
import os
import sys
import re

print(f"Starting FloodFactorApp in process id: {os.getpid()}, args: {sys.argv}")

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

# Example data - you can expand this
flood_data = {
    "34609": {"depth": 4.5, "probability": 0.01},
    "33625": {"depth": 2.3, "probability": 0.05},
}

def clean_redundant_phrases(text):
    """
    Removes repeated or redundant sentences/phrases.
    """
    patterns = [
        r"(Residents.*?evacuate.*?) Residents.*?evacuate.*?\.",
        r"(Homes.*?damage.*?) Homes.*?damage.*?\.",
    ]
    for pattern in patterns:
        text = re.sub(pattern, r"\1", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()

def probability_to_score(prob):
    """
    Convert flood annual probability to a 0-5 likelihood score.
    """
    if prob < 0.001:
        return 0
    elif prob < 0.005:
        return 1
    elif prob < 0.01:
        return 2
    elif prob < 0.02:
        return 3
    elif prob < 0.05:
        return 4
    else:
        return 5

def generate_flood_risk_text(zip_code, user_depth, probability, likelihood_score):
    prompt = (
        f"You are a flood risk expert. The user asks about a flood depth of {user_depth} feet "
        f"in ZIP code {zip_code}. The flood has a likelihood score of {likelihood_score} out of 5 "
        f"based on historical data.\n\n"
        "Describe the likely impact of flooding at this depth on residents, homes, and travel. "
        "Avoid redundant phrasing. Be concise but informative."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )

    raw_output = response.choices[0].message.content.strip()
    return clean_redundant_phrases(raw_output)

@app.route("/", methods=["GET", "POST"])
def index():
    explanation = None
    error = None
    adjusted_depth = False  # Keep for compatibility; not used in prompt anymore

    if request.method == "POST":
        zip_code = request.form.get("zip_code", "").strip()
        requested_depth = request.form.get("depth", "").strip()

        try:
            requested_depth = float(requested_depth)
        except (ValueError, TypeError):
            error = "Please enter a valid number for flood depth."
            return render_template("index.html", explanation=explanation, error=error, adjusted_depth=adjusted_depth)

        data = flood_data.get(zip_code)
        if data:
            adjusted_depth = requested_depth > data["depth"]  # Optional to keep
            likelihood_score = probability_to_score(data["probability"])
            explanation = generate_flood_risk_text(
                zip_code, requested_depth, data["probability"], likelihood_score
            )
        else:
            error = f"No flood data available for ZIP code {zip_code}."

    return render_template("index.html", explanation=explanation, error=error, adjusted_depth=adjusted_depth)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Running app on 0.0.0.0:{port} in process id: {os.getpid()}")
    app.run(host="0.0.0.0", port=port)
