# Energy Market Optimizer

A portfolio project to develop and showcase Python skills for **energy market modeling, optimization, and forecasting** — inspired by real-world roles in distributed energy systems, flexibility modeling, and market participation.

## 📌 Project Overview
This repository contains a series of incremental projects that build towards a **mini Energy Management System (EMS)** capable of:
- Forecasting electricity demand and prices
- Optimizing the operation of distributed energy resources (DERs) such as batteries and solar
- Simulating participation in day-ahead and intraday energy markets

The final goal is to integrate **optimization (LP/MILP)**, **forecasting**, and **simulation** into one polished, deployable tool.

## 📂 Project Structure
energy-market-optimizer/
│
├── data/ # Datasets for optimization & forecasting
├── notebooks/ # Optional: Jupyter notebooks for exploration
├── src/ # Source code
│ ├── stage1_lp_example.py # Intro to LP optimization
│ ├── stage2_pyomo_battery.py # Battery scheduling with Pyomo
│ ├── stage3_forecasting.py # Forecasting & market simulation
│ └── stage4_final_project.py # Integrated EMS system
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation

bash
Copy
Edit

## 🚀 Installation
1. Clone the repository:
```bash
git clone https://github.com/<your-username>/energy-market-optimizer.git
cd energy-market-optimizer
Create a virtual environment (recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🛠 Technologies Used
Python — Core programming language

PuLP — Linear & Mixed Integer optimization

Pyomo — Advanced optimization modeling

pandas, numpy — Data analysis

matplotlib, plotly — Data visualization

scikit-learn, statsmodels — Forecasting

SimPy — Simulation

📅 Project Stages
Stage 1: Intro to LP optimization (PuLP) — supply/demand cost minimization

Stage 2: Battery scheduling & DER optimization (Pyomo)

Stage 3: Price & demand forecasting + market simulation

Stage 4: Final integrated EMS project with dashboards

📊 Example Output (Stage 1)
vbnet
Copy
Edit
Status: Optimal
Total Cost =  13150.0
Electricity from Coal to A: 80.0 MWh
Electricity from Coal to B: 70.0 MWh
Electricity from Coal to C: 0.0 MWh
Electricity from Wind to A: 0.0 MWh
Electricity from Wind to B: 0.0 MWh
Electricity from Wind to C: 60.0 MWh
📜 License
This project is open-source and available under the MIT License.

Author: Akeem Mustapha
LinkedIn: https://www.linkedin.com/in/akeem-mustapha-724272160/
GitHub: https://github.com/AkkyMusty/energy
