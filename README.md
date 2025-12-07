# 🌊 FloodFactorApp

FloodFactorApp is a real-time flood risk checker that combines geolocation, National Weather Service alerts, and environmental data to help users assess flood threats in their area. Built for public awareness and emergency preparedness, the app offers both automatic and manual location input, along with live alert streaming.

---

## 🚀 Features

- 🌐 **Live NWS Alerts** — Displays active flood and wind warnings with severity and expiration  
- 📍 **Auto-Location Detection** — Users can opt to auto-fill their latitude and longitude  
- 🧭 **Manual Location Input** — Enter coordinates manually for privacy or precision  
- 📊 **Flood Depth Analysis** — Returns estimated flood depth in feet  
- 📰 **Nationwide Alert Marquee** — Scrolls active warnings across the top of the page  

---

## 📦 Tech Stack

- **Frontend**: HTML templates  
- **Backend**: Python (Flask)  
- **APIs**: Google Search API, NWS Alert Feeds  
- **Hosting**: Render.com  

---

### 📁 Repository Structure

```plaintext
FloodFactorApp/
├── Configs/           # Environmental configs, API keys (excluded), and jurisdictional routing logic
├── Diagrams/          # Flood modeling diagrams, overlay flowcharts, and system architecture visuals
├── Docs/              # Civic documentation, SOPs, and public safety alignment guides
├── Evidence/          # Screenshots, logs, and validation artifacts from flood analysis runs
├── Images/            # Visual assets used in dashboards and overlays
├── Pages/             # Public-facing HTML pages and civic dashboard mockups
├── Scripts/           # Python scripts for flood modeling, data ingestion, and overlay generation
├── __pycache__/       # Auto-generated Python cache files (ignored via .gitignore)
├── backup/            # Archived versions of templates and dashboards
├── templates/         # Jinja2 HTML templates for dynamic rendering
├── .gitignore         # Excludes sensitive and platform-specific clutter
├── LICENSE            # MIT license for public use and adaptation
└── README.md          # Project overview, usage instructions, and recruiter-facing notes

---

### ✅ Live Demo:

Visit the live app: [https://floodfactorapp.onrender.com/](https://floodfactorapp.onrender.com/)

### Step-by-Step Instructions:

1. **Open the link** in your browser.
2. On the homepage, choose:
   - ✅ “Yes, get my location” to auto-fill your coordinates.
   - ❌ “No, I’ll enter it myself” to manually input latitude and longitude.
3. Click the **“Get Flood Facts Now!”** button.
4. View your **estimated flood depth** and any **active NWS alerts**.
5. Watch the **nationwide alert marquee** for broader updates.

## 🔐 Legal Notice

FloodFactorApp™ is a proprietary environmental risk tool developed by **Jessica S. Marosi**.  
All code and content are protected under copyright.  
Trademark pending. Do not reproduce without permission.

## 🙋‍♀️ About the Creator

Jessica S. Marosi is the founder of Bytelock™ and inventor of ChainLogic™ and the FloodFactor™ app, a forensic-grade digital chain-of-custody system.  
FloodFactorApp is part of her mission to build defensible, scalable platforms for public safety and environmental awareness.
