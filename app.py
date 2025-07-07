from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

# Cache dictionary to store AI responses: key is (zip, depth), value is explanation text
cache = {}

def generate_flood_risk_text(zip_code, depth):
    prompt = (
        f"Explain in simple, clear terms what a flood depth of {depth} feet means for residents living in ZIP code {zip_code}. "
        "Describe how high the water would reach indoors and outdoors, the types of damage likely to occur, "
        "impact on travel and infrastructure, and advice on how residents can prepare. "
        "Avoid exaggeration but be informative and helpful."
    )
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    explanation = None
    error = None
    if request.method == "POST":
        zip_code = request.form.get("zip_code", "").strip()
        depth_str = request.form.get("depth", "").strip()
        
        # Basic validation
        if not zip_code or not depth_str:
            error = "Please enter both ZIP code and flood depth."
        else:
            try:
                depth = float(depth_str)
                key = (zip_code, depth)
                
                if key in cache:
                    explanation = cache[key]
                else:
                    explanation = generate_flood_risk_text(zip_code, depth)
                    cache[key] = explanation  # Save in cache
                
            except ValueError:
                error = "Flood depth must be a number."
    
    return render_template("index.html", explanation=explanation, error=error)

if __name__ == "__main__":
    app.run(debug=True)
