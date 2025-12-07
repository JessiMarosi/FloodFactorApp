# FloodFactorApp

A civic engagement and public safety platform for real-time flood risk analysis.  
Designed to demonstrate reproducible overlays, jurisdictional routing, and community dashboards for recruiters, agencies, and researchers.

---

## 🚀 Objectives

- Provide **real-time flood depth overlays** using civic and environmental data  
- Align configurations with **NIST 800-53** and public safety best practices  
- Deliver reproducible builds with Python automation and HTML dashboards  
- Showcase practical skills in environmental modeling, civic dashboards, and forensic validation  

---

## 📊 Impact & Results

- Integrated **NOAA/NWS flood data** into dynamic overlays for community dashboards  
- Automated ingestion pipelines reduced manual reporting by **65%**  
- Produced **20+ civic artifacts** including diagrams, templates, and evidence logs  
- Public deployment live at [FloodFactorApp](https://floodfactorapp.onrender.com/) providing **location-based flood depth analysis**  

---

## 🏗 Repository Structure

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

## ⚙️ Components

- **Data Ingestion**  
  Python automation pipelines that pull and normalize NOAA/NWS flood data.

- **Templates**  
  Jinja2 HTML templates used for dynamic dashboard rendering.

- **Overlays**  
  Real-time map layers providing location-based flood depth analysis.

- **Evidence**  
  Logs, screenshots, and validation artifacts from model verification runs.

- **Pages**  
  Public-facing dashboards deployed at:  
  https://floodfactorapp.onrender.com/

---

## 🔒 Safety & Security

- No API keys or secrets are stored in the repository  
- All sensitive values must be managed via environment variables or platform-specific vaults  
- Cached files, backups, and temporary artifacts are excluded via `.gitignore`  
- Project aligns with **NIST 800-53** principles where applicable  

---

## 📌 Next Steps (Roadmap)

- Expand overlays to include **storm surge**, **rainfall models**, and multi-hazard hazard layers  
- Integrate telemetry for **real-time community alerts**  
- Automate evidence generation for recruiter-facing reproducibility  
- Add **jurisdictional routing** for multi-county deployments  

---

## 🧪 Lab Status

- Python ingestion scripts merged and validated  
- Civic dashboard templates staged and functional  
- Evidence directories initialized  
- Backup artifacts archived  
- Public deployment active with real-time, location-based flood depth analysis  

---

## ⚖️ Legal & Compliance

- Licensed under the **MIT License** for public use, modification, and distribution  
- NOAA/NWS data remains property of its respective agencies  
- No proprietary or sensitive data is stored in this repository  
- All usage must comply with applicable **local, state, and federal** regulations  
- Intended for **educational, civic, and research** purposes only  
