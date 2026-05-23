# Tamil Nadu Assembly Elections (2021 vs. 2026) Analysis Dashboard

An interactive, premium-designed web application built to analyze and compare the political landscape of the Tamil Nadu Legislative Assembly Elections between **2021** and **2026**. 

This application visualizes a historic political disruption in 2026: the debut of the newly formed **Tamizhaga Vettri Kazhagam (TVK)** alliance led by actor-politician C. Joseph Vijay, which won **108 seats** and emerged as the single largest party, breaking the decades-old DMK+ and ADMK+ Dravidian duopoly.

---

## 📂 Project Structure

```
elec_analysis/
├── app.py                      # Main Streamlit application containing UI & logic
├── constituency_master.csv     # Master lookup for assembly constituency metadata
├── election_results_2021.csv   # Granular candidate-wise results for 2021
├── election_results_2026.csv   # Granular candidate-wise results for 2026
├── requirements.txt            # Python dependencies (Streamlit, Pandas, Plotly, etc.)
├── Dockerfile                  # Configuration for containerized deployment
└── .dockerignore               # Patterns to exclude from Docker build context
```

---

## 📊 Dataset Schema Reference

The dashboard dynamically loads and merges three CSV datasets to build its analysis models:

### 1. `constituency_master.csv`
Contains geographical and categorization metadata for all 234 Assembly Constituencies (AC) in Tamil Nadu.
* **`ac_number`**: (Integer) Unique identifier of the constituency (1 to 234).
* **`constituency`**: (String) Official constituency name.
* **`district`**: (String) District name under which the constituency falls.
* **`region`**: (String) Geographical region classification (*Chennai Metro, North, Central, Kongu, Delta, South*).
* **`reserved`**: (String) Seat reservation category (*GEN* for General, *SC* for Scheduled Castes, *ST* for Scheduled Tribes).

### 2. `election_results_2021.csv` & `election_results_2026.csv`
Provide candidate-level statistics for each election.
* **`ac_no`**: (Integer) Matches `ac_number` in master data.
* **`ac_name`**: (String) Constituency name.
* **`candidate_name`**: (String) Candidate name.
* **`gender`**: (String) Candidate gender (*MALE, FEMALE, THIRD*).
* **`age`**: (Integer) Age of candidate.
* **`category`**: (String) Candidate reservation category.
* **`party`**: (String) Candidate's political party abbreviation (e.g., *TVK, DMK, ADMK, INC, NTK*).
* **`general`**: (Integer) EVM/General votes polled for candidate.
* **`postal`**: (Integer) Postal votes polled.
* **`total`**: (Integer) Total votes polled (General + Postal).
* **`pct_votes`**: (Float) Candidate's vote percentage share in that constituency.
* **`total_electors`**: (Integer) Total registered voters in that constituency.
* **`party_group`**: (String) Political alliance categorization (*TVK+, DMK+, ADMK+, NTK, MNM, Others*).
* **`rank`**: (Integer) Candidate's final placement (rank `1` denotes the winning candidate).

---

## 🎛️ Key Features & Views

The application offers two distinct navigation views, selectable from the sidebar:

### 1. 📽️ Slide Deck Presentation Mode
Designed for storytelling, this mode presents a structured narrative across 7 slides:
* **Executive Summary**: High-level metrics showing TVK's debut, voter turnout surge (+12.45%), MLA rejuvenation (-3.9 years average age), and doubled female representation.
* **Seat & Vote Share Swings**: Interactive side-by-side donut charts for seat share, and grouped bar charts comparing popular vote shares.
* **Seat Transitions Matrix**: An analysis of where TVK's 108 seats came from. Features an interactive toggle between a **Sankey Flow Diagram** (visualizing candidate streams) and a **Heatmap crosstab Matrix**.
* **Regional & District Performance**: Bar charts displaying regional wins, stacked bars for reservation categories (GEN/SC/ST), and a detailed district-wise breakdown.
* **Victory Margins & Contests**: Analysis of the closest contests (lowest margins) and landslide victories (highest margins) with built-in data export.
* **Demographic Shifts**: Deep dive into MLA ages using interactive histograms and box-plots, alongside gender ratios.
* **Constituency Explorer**: A side-by-side search tool that allows users to compare candidate performance, margins, and turnout for any of the 234 constituencies.

### 2. 📊 PowerBI-Style Unified Dashboard
A comprehensive dashboard featuring multi-level filtering designed for custom explorations:
* **Interactive Filters**: Filter entire dataset by Year, Region, District, Reservation Category, Winner Gender, and Candidate Age Range.
* **Dynamic KPI Cards**: Instantly recalculate filtered seat counts, voter turnout %, average winner age, and female winner count.
* **Sub-Level Visualizations**: Render donut breakdown of seats, bar chart of vote shares, margin analysis, and age distributions matching the selected filters.
* **Exportable Reports**: Includes a structured data table of the filtered winners with an option to download the report as a CSV.

---

## 🎨 Design & Theme

To ensure a modern and premium interface, the application overrides Streamlit defaults with custom CSS:
* **Typography**: Uses the Google Font **Outfit** for sleek, clean headings and text.
* **Theme**: Deep dark glassmorphism styling (`#0c0f17` background with `#1b2030` gradients for cards).
* **Visual FX**: Hover animations on metrics cards, customized button layouts, and clear colored text blocks.
* **Alliance Branding**: Colors mapped directly to regional political alliances:
  - **TVK+**: Purple (`#7A1FA2`)
  - **DMK+**: Red (`#E30613`)
  - **ADMK+**: Green (`#008000`)
  - **NTK**: Yellow (`#FFEB3B`)
  - **MNM**: Cyan (`#00BCD4`)
  - **Others/NOTA/IND**: Grayscale (`#757575`, `#9E9E9E`, `#BDBDBD`)

---

## ⚡ Getting Started

### Prerequisites
* Python 3.10+
* pip package manager

### Running Locally
1. Clone the repository and navigate into it:
   ```bash
   cd elec_analysis
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit server:
   ```bash
   streamlit run app.py
   ```
5. Open your browser and navigate to `http://localhost:8501`.

---

## 🐳 Docker Deployment

The project is fully containerized and configured for cloud environment deployments (e.g., Google Cloud Run, AWS ECS).

### 1. Build the Docker Image
```bash
docker build -t tn-elec-analysis .
```

### 2. Run the Container locally
```bash
docker run -p 8080:8080 tn-elec-analysis
```
*Access the app on `http://localhost:8080`*

### ⚙️ Container Configuration Details
* **Base Image**: `python:3.11-slim` for faster build times and minimal package sizes.
* **Exposed Port**: `8080` (Standard for cloud hosting environments).
* **Environment Variables**:
  - `STREAMLIT_SERVER_PORT=8080`
  - `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
  - `STREAMLIT_SERVER_HEADLESS=true`
* **Exclusions**: `.dockerignore` filters out `venv/`, `.streamlit/`, `.git/`, caching files (`__pycache__/`, `*.pyc`), and local development files to keep build contexts clean.
