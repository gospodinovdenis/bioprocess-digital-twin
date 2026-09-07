# bioprocess-digital-twin# 🧬 Mechanistic Bioprocess Digital Twin

### Fed-Batch Mammalian Cell Culture Modeling, Calibration, Sensitivity Analysis, and Process Optimization

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![SciPy](https://img.shields.io/badge/SciPy-ODE%20Modeling-orange.svg)](https://scipy.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Digital%20Twin-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Visualization-purple.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

This project develops a **mechanistic bioprocess digital twin** for a fed-batch mammalian cell culture process.

The model integrates biological knowledge, differential equations, numerical simulation, parameter estimation, model validation, sensitivity analysis, and process optimization into an interactive computational framework.

The objective is to demonstrate how mechanistic modeling can be used to move from experimental observations to **process understanding and data-driven operating decisions**.

The project culminates in an interactive **Streamlit dashboard** that allows users to simulate the bioreactor, explore parameter effects, and identify operating conditions that maximize product formation while satisfying process constraints.

### Core workflow

```text
Experimental Data
       │
       ▼
Mechanistic ODE Model
       │
       ▼
Parameter Estimation
       │
       ▼
Model Validation
       │
       ▼
Sensitivity Analysis
       │
       ▼
Process Optimization
       │
       ▼
Interactive Digital Twin
```

---

# Project Objectives

The project was designed to address several questions relevant to bioprocess development and modeling:

* How can biological mechanisms be represented mathematically?
* Can kinetic parameters be estimated from noisy process measurements?
* How accurately can a mechanistic model reproduce experimental observations?
* Which biological parameters have the greatest influence on process performance?
* What operating conditions maximize product formation?
* How can mechanistic models be exposed through an interactive digital-twin interface?

---

# Biological Process Model

The simulated process represents a fed-batch mammalian cell culture system.

The model tracks six state variables:

| State   | Description               |
| ------- | ------------------------- |
| \(X_v\) | Viable cell concentration |
| \(X_d\) | Dead cell concentration   |
| \(G\)   | Glucose concentration     |
| \(L\)   | Lactate concentration     |
| \(P\)   | Product concentration     |
| \(V\)   | Reactor volume            |

The model represents interactions between cell growth, cell death, nutrient consumption, metabolite formation, product formation, and reactor volume.

---

## Growth Kinetics

Cell growth is represented using glucose-limited Monod kinetics:

$$
\mu =
\mu_{max}
\frac{G}{K_G + G}
$$

where:

* \(\mu\) = specific growth rate
* \(\mu_{max}\) = maximum specific growth rate
* \(G\) = glucose concentration
* \(K_G\) = glucose half-saturation constant

---

## Viable Cell Dynamics

$$
\frac{dX_v}{dt}
=
(\mu-k_d)X_v
$$

where:

* \(X_v\) = viable cell concentration
* \(k_d\) = cell death rate

---

## Dead Cell Dynamics

$$
\frac{dX_d}{dt}
=
k_dX_v
$$

---

## Glucose Dynamics

Glucose consumption is coupled to cellular growth and glucose availability:

$$
\frac{dG}{dt}
=
-q_GX_v
\left(
\frac{G}{K_G+G}
\right)
+
\frac{F}{V}(G_{feed}-G)
$$

where:

* \(q_G\) = glucose consumption coefficient
* \(F\) = feed rate
* \(G_{feed}\) = glucose concentration in the feed
* \(V\) = reactor volume

---

## Lactate Dynamics

$$
\frac{dL}{dt}
=
q_LX_v
\left(
\frac{G}{K_G+G}
\right)
-
\frac{F}{V}L
$$

where \(q_L\) represents the lactate production coefficient.

---

## Product Formation

$$
\frac{dP}{dt}
=
q_PX_v
-
\frac{F}{V}P
$$

where \(q_P\) represents the product formation coefficient.

---

## Reactor Volume

$$
\frac{dV}{dt}=F
$$

The complete model is implemented in Python and numerically integrated using `scipy.integrate.solve_ivp`.

---

# Project Pipeline

## Phase 8 — Synthetic Experimental Data

The project begins with simulated process observations representing experimental measurements.

Measurements include:

* viable cells
* dead cells
* glucose
* lactate
* product
* reactor volume

Measurement noise is introduced to reproduce realistic experimental variability.

The resulting dataset is stored in:

```text
data/raw/synthetic_experimental_data.csv
```

---

# Phase 9 — Parameter Estimation

The mechanistic model contains biological parameters that are not directly observed.

These include:

* \(\mu_{max}\)
* \(K_G\)
* \(k_d\)
* \(q_G\)
* \(q_P\)

Parameter estimation is used to infer these values from the simulated experimental observations.

The calibrated parameters are stored in:

```text
data/processed/fitted_parameters.csv
```

This establishes a computational workflow analogous to fitting a mechanistic process model to experimental bioprocess data.

---

# Phase 10 — Model Validation

The calibrated model is simulated using the estimated parameters and compared with the experimental observations.

Model performance is evaluated using:

* RMSE
* MAE
* \(R^2\)

The project generates:

```text
data/processed/validation_metrics.csv
data/processed/model_predictions.csv
data/processed/model_residuals.csv
```

and corresponding visualization outputs.

### Validation visualization

The validation analysis compares observed and predicted trajectories for key process variables.

The goal is to determine whether the calibrated model adequately captures the major dynamics represented in the experimental dataset.

> **Note:** Because the current dataset is synthetic and the same observations are used for calibration and fit assessment, this represents model-fit validation rather than independent external validation. A future extension would evaluate the model against a second experimental process condition.

---

# Phase 11 — Sensitivity Analysis

Sensitivity analysis evaluates how strongly model outputs respond to changes in biological parameters.

The current implementation performs a local one-at-a-time perturbation analysis using:

```text
-20%
-10%
+10%
+20%
```

around the calibrated parameter values.

Process outputs evaluated include:

* maximum viable cells
* final product
* final glucose
* IVCD

IVCD is calculated as the integral of viable-cell concentration over time:

$$
IVCD =
\int_0^T X_v(t)\,dt
$$

The analysis produces:

```text
data/processed/sensitivity_results.csv
data/processed/normalized_sensitivity.csv
data/processed/parameter_sensitivity_ranking.csv
```

This identifies which parameters have the greatest influence on modeled process performance.

---

# Phase 12 — Process Optimization

The calibrated model is used to explore process operating conditions.

The primary decision variable is the **feed rate \(F\)**.

A feed-rate sweep evaluates the effect of changing the operating condition on:

* final product
* viable cells
* glucose
* lactate
* reactor volume
* IVCD

The optimization incorporates process constraints such as:

```text
Minimum final viable-cell concentration
Maximum final lactate concentration
```

The objective is:

> **Maximize final product while satisfying process constraints.**

Optimization outputs are stored in:

```text
data/processed/optimization_results.csv
data/processed/optimal_process.csv
```

This converts the model from a descriptive simulation into a **process decision-support tool**.

---

# Phase 13 — Interactive Digital Twin

The final application is implemented using **Streamlit** and **Plotly**.

Launch the application with:

```bash
streamlit run dashboard/app.py
```

The dashboard contains three major components.

---

## 🧬 Digital Twin

The Digital Twin tab allows users to interactively modify process and biological parameters.

### Process variables

* Feed rate
* Feed glucose concentration
* Process duration

### Biological parameters

* Maximum growth rate
* Glucose half-saturation constant
* Cell death rate
* Glucose consumption
* Lactate production
* Product formation

The model is automatically re-simulated when parameters are changed.

The dashboard displays:

* viable-cell trajectory
* dead-cell trajectory
* glucose profile
* lactate profile
* product formation
* reactor volume
* final process KPIs

This provides a **what-if simulation environment** for exploring process behavior.

---

## ⚙️ Optimization

The Optimization tab provides interactive process optimization.

Users can specify:

* minimum viable-cell concentration
* maximum lactate concentration
* process duration
* minimum feed rate
* maximum feed rate
* search resolution

The application evaluates candidate operating conditions and identifies the highest-product feasible condition.

The resulting analysis includes:

* optimal feed rate
* predicted final product
* product improvement relative to baseline
* final viable cells
* final lactate
* final glucose
* final reactor volume

---

## 📊 Sensitivity Analysis

The Sensitivity Analysis tab provides interactive visualization of Phase 11 results.

Users can select individual process outputs and examine parameter influence.

The dashboard provides:

* parameter sensitivity rankings
* overall parameter influence
* parameter-output sensitivity matrix
* interactive heatmap
* underlying sensitivity data

This helps identify the biological parameters that most strongly control process behavior.

---

# Technology Stack

### Programming

* Python
* NumPy
* pandas

### Scientific Computing

* SciPy
* `solve_ivp`
* LSODA
* Numerical integration

### Modeling

* Mechanistic ordinary differential equations
* Monod kinetics
* Parameter estimation
* Sensitivity analysis
* Process optimization

### Visualization

* Matplotlib
* Plotly

### Application

* Streamlit

### Data Analysis

* pandas
* RMSE
* MAE
* \(R^2\)
* Parameter perturbation analysis

---

# Repository Structure

```text
bioprocess-digital-twin/
│
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── synthetic_experimental_data.csv
│   │
│   └── processed/
│       ├── fitted_parameters.csv
│       ├── validation_metrics.csv
│       ├── model_predictions.csv
│       ├── model_residuals.csv
│       ├── sensitivity_results.csv
│       ├── normalized_sensitivity.csv
│       ├── parameter_sensitivity_ranking.csv
│       ├── optimization_results.csv
│       └── optimal_process.csv
│
├── src/
│   ├── model.py
│   ├── calibration.py
│   ├── sensitivity.py
│   └── optimization.py
│
├── notebooks/
│   ├── 01_process_data.ipynb
│   ├── 02_mechanistic_model.ipynb
│   ├── 03_parameter_estimation.ipynb
│   ├── 04_model_validation.ipynb
│   ├── 05_process_optimization.ipynb
│   └── 06_uncertainty_analysis.ipynb
│
├── dashboard/
│   └── app.py
│
├── figures/
│   ├── model_validation.png
│   ├── model_residuals.png
│   ├── observed_vs_predicted.png
│   ├── parameter_sensitivity_ranking.png
│   ├── product_sensitivity.png
│   ├── optimization_product_vs_feed.png
│   ├── optimization_cells_vs_feed.png
│   ├── optimization_lactate_vs_feed.png
│   └── feasible_operating_region.png
│
└── docs/
    └── technical_report.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/bioprocess-digital-twin.git
cd bioprocess-digital-twin
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Run the mechanistic model

```bash
python src/model.py
```

## Generate synthetic experimental data

```bash
python src/generate_data.py
```

## Estimate model parameters

```bash
python src/calibration.py
```

## Validate the model

```bash
python src/validation.py
```

## Run sensitivity analysis

```bash
python src/sensitivity.py
```

## Run process optimization

```bash
python src/optimization.py
```

## Launch the digital twin

```bash
streamlit run dashboard/app.py
```

---

# Example Questions the Digital Twin Can Answer

The application can be used to explore questions such as:

### What happens if feed rate increases?

Increasing feed rate changes substrate availability and reactor dilution, which can alter cell growth, metabolite accumulation, and product formation.

### Which biological parameter has the largest effect on product?

The sensitivity analysis identifies the parameters producing the largest changes in final product and other process outputs.

### What feed rate maximizes product?

The optimization module searches the defined operating range and selects the highest-product condition that satisfies the process constraints.

### How does increased cell death affect productivity?

Changing \(k_d\) allows the user to observe the resulting effects on viable cells, dead cells, and product formation.

---

# Key Modeling Concepts Demonstrated

This project demonstrates practical experience with:

* Mechanistic modeling
* Ordinary differential equations
* Biological kinetics
* Numerical integration
* Parameter estimation
* Model calibration
* Model validation
* Residual analysis
* Sensitivity analysis
* Process optimization
* Constraint-based decision making
* Interactive scientific computing
* Digital-twin concepts

---

# Limitations

This project is intentionally designed as a portfolio and modeling demonstration rather than a validated industrial bioprocess model.

Important limitations include:

1. The experimental dataset is synthetic.
2. The model represents a simplified mammalian cell culture system.
3. The current model does not explicitly represent oxygen transfer.
4. pH and dissolved oxygen are not modeled.
5. Metabolism is represented using simplified kinetic relationships.
6. The current sensitivity analysis is local rather than global.
7. Model validation currently uses the same synthetic process condition used for calibration.

These limitations provide opportunities for future development.

---

# Future Development

Potential extensions include:

### 1. Global Sensitivity Analysis

Implement:

* Latin Hypercube Sampling
* Sobol sensitivity indices
* Morris screening

to quantify parameter importance across the full parameter space.

### 2. Uncertainty Quantification

Use Monte Carlo simulation to propagate parameter uncertainty through the model and produce prediction intervals for:

* viable cells
* glucose
* lactate
* product

### 3. Hybrid Mechanistic + Machine Learning Model

Add a machine-learning residual model:

```text
Mechanistic prediction
        ↓
Residual
        ↓
Machine Learning Model
        ↓
Hybrid prediction
```

This would combine mechanistic interpretability with data-driven correction.

### 4. Dynamic Feed Control

Extend the optimization from a constant feed rate to a time-dependent feed strategy:

$$
F = F(t)
$$

This would allow optimization of feeding trajectories rather than a single operating parameter.

### 5. Additional Bioprocess States

Potential additions include:

* dissolved oxygen
* pH
* ammonia
* osmolality
* carbon dioxide
* oxygen uptake rate
* specific productivity

### 6. Independent Experimental Validation

Test the model against an independent process condition or experimental dataset.

---

# Why This Project Matters

Bioprocess modeling often requires integrating biological understanding with mathematical modeling, numerical methods, data analysis, and process decision-making.

This project demonstrates that workflow end-to-end:

```text
Biology
   ↓
Mathematical Model
   ↓
Numerical Simulation
   ↓
Parameter Estimation
   ↓
Validation
   ↓
Sensitivity
   ↓
Optimization
   ↓
Digital Twin
```

Rather than treating the problem as a generic machine-learning exercise, the project uses a **mechanistic model as the foundation for process understanding and optimization**.

---

# Skills Demonstrated

**Computational Biology**

* Biological systems modeling
* Quantitative cell culture modeling
* Kinetic modeling
* Systems biology concepts

**Data Science**

* Data preprocessing
* Parameter estimation
* Statistical evaluation
* Sensitivity analysis
* Optimization
* Numerical analysis

**Machine Learning / Modeling**

* Model calibration
* Model comparison
* Future hybrid mechanistic/ML integration

**Software Engineering**

* Modular Python architecture
* Reusable simulation functions
* Data pipelines
* Interactive application development
* Scientific visualization

**Bioprocess Modeling**

* Fed-batch process simulation
* Cell growth and death
* Substrate consumption
* Metabolite formation
* Product formation
* Feed-rate optimization
* Digital-twin concepts

---

# Author

**Denis Gospodinov, PhD**

Computational Biology | Machine Learning | Bioinformatics | Mechanistic Modeling

PhD, University of Houston

---

## Disclaimer

This project is a computational modeling demonstration using synthetic data. It is not intended for direct use in manufacturing, process control, clinical decision-making, or other regulated applications without appropriate experimental validation and qualification.
