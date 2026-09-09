import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.integrate import solve_ivp


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"

PARAMETER_PATH = PROCESSED_PATH / "fitted_parameters.csv"
REAL_CADET_OUTLET_PATH = PROCESSED_PATH / "cadet_capture_outlet.csv"
REAL_CADET_METRICS_PATH = PROCESSED_PATH / "cadet_capture_metrics.csv"
DEMO_CADET_OUTLET_PATH = PROCESSED_PATH / "demo_cadet_capture_outlet.csv"
DEMO_CADET_METRICS_PATH = PROCESSED_PATH / "demo_cadet_capture_metrics.csv"
OPTIMAL_PROCESS_PATH = PROCESSED_PATH / "optimal_process.csv"


# ============================================================
# Page setup
# ============================================================

st.set_page_config(
    page_title="Integrated Bioprocess Digital Twin",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 Integrated Bioprocess Digital Twin")
st.markdown(
    """
    **Mechanistic upstream + downstream process simulation**

    This portfolio application combines a custom SciPy fed-batch mammalian-cell
    model with a downstream chromatography workflow designed for CADET-Core /
    CADET-Process output.
    """
)

mode = st.sidebar.radio(
    "Digital Twin Module",
    ["Upstream Reactor", "Downstream CADET Purification"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Upstream: SciPy ODE model\n\n"
    "Downstream: CADET-Core / CADET-Process results"
)


# ============================================================
# Upstream model
# ============================================================

def bioreactor_model(t, y, params):
    Xv, Xd, G, L, P, V = y

    mu_max = params["mu_max"]
    K_G = params["K_G"]
    kd = params["kd"]
    qG = params["qG"]
    qL = params["qL"]
    qP = params["qP"]
    F = params["F"]
    G_feed = params["G_feed"]

    G_eff = max(G, 0.0)
    V_eff = max(V, 1e-9)

    mu = mu_max * G_eff / (K_G + G_eff)
    dXv_dt = (mu - kd) * Xv
    dXd_dt = kd * max(Xv, 0.0)

    glucose_limitation = G_eff / (K_G + G_eff)
    dG_dt = -qG * max(Xv, 0.0) * glucose_limitation + (F / V_eff) * (G_feed - G)
    dL_dt = qL * max(Xv, 0.0) - (F / V_eff) * L
    dP_dt = qP * max(Xv, 0.0) - (F / V_eff) * P
    dV_dt = F

    return [dXv_dt, dXd_dt, dG_dt, dL_dt, dP_dt, dV_dt]


@st.cache_data
def load_parameters():
    defaults = {
        "mu_max": 0.03,
        "K_G": 1.0,
        "kd": 0.003,
        "qG": 0.05,
        "qP": 0.01,
    }

    if PARAMETER_PATH.exists():
        table = pd.read_csv(PARAMETER_PATH)
        if {"parameter", "fitted_value"}.issubset(table.columns):
            defaults.update(dict(zip(table["parameter"], table["fitted_value"])))

    defaults["F"] = 0.01
    defaults["G_feed"] = 50.0
    defaults["qL"] = 0.02
    return defaults


@st.cache_data
def run_simulation(parameter_values, total_time):
    parameters = dict(parameter_values)
    time = np.linspace(0, total_time, 500)

    solution = solve_ivp(
        bioreactor_model,
        (0, total_time),
        [1.0, 0.0, 20.0, 0.0, 0.0, 1.0],
        args=(parameters,),
        t_eval=time,
        method="LSODA",
        rtol=1e-6,
        atol=1e-8,
    )

    if not solution.success:
        raise RuntimeError(solution.message)

    return solution


# ============================================================
# Upstream view
# ============================================================

if mode == "Upstream Reactor":
    st.header("Upstream Reactor Digital Twin")
    st.write(
        "Explore a mechanistic fed-batch model and observe how biological and "
        "process parameters affect cells, metabolites, product, and reactor volume."
    )

    base = load_parameters()

    st.sidebar.header("Upstream Process Controls")
    simulation_time = st.sidebar.slider("Simulation time (hours)", 24, 240, 120, 12)
    feed_rate = st.sidebar.slider(
        "Feed rate F", 0.002, 0.030, float(base["F"]), 0.001, format="%.3f"
    )
    feed_glucose = st.sidebar.slider(
        "Feed glucose concentration", 10.0, 100.0, float(base["G_feed"]), 5.0
    )

    st.sidebar.header("Biological Parameters")
    mu_max = st.sidebar.slider(
        "Maximum growth rate μmax", 0.005, 0.10, float(base["mu_max"]), 0.001, format="%.3f"
    )
    K_G = st.sidebar.slider(
        "Glucose half-saturation K_G", 0.1, 10.0, float(base["K_G"]), 0.1
    )
    kd = st.sidebar.slider(
        "Cell death rate kd", 0.0001, 0.03, float(base["kd"]), 0.001, format="%.4f"
    )
    qG = st.sidebar.slider(
        "Glucose consumption qG", 0.005, 0.20, float(base["qG"]), 0.005
    )
    qL = st.sidebar.slider(
        "Lactate production qL", 0.001, 0.10, float(base["qL"]), 0.005
    )
    qP = st.sidebar.slider(
        "Product formation qP", 0.001, 0.05, float(base["qP"]), 0.001
    )

    parameters = {
        "mu_max": mu_max,
        "K_G": K_G,
        "kd": kd,
        "qG": qG,
        "qL": qL,
        "qP": qP,
        "F": feed_rate,
        "G_feed": feed_glucose,
    }

    try:
        sol = run_simulation(tuple(sorted(parameters.items())), simulation_time)
    except Exception as error:
        st.error(f"Simulation failed: {error}")
        st.stop()

    time = sol.t
    Xv, Xd, G, L, P, V = sol.y

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Product", f"{P[-1]:.2f}")
    c2.metric("Max Viable Cells", f"{np.max(Xv):.2f}")
    c3.metric("Final Glucose", f"{G[-1]:.2f}")
    c4.metric("Final Lactate", f"{L[-1]:.2f}")

    fig_cells = go.Figure()
    fig_cells.add_trace(go.Scatter(x=time, y=Xv, mode="lines", name="Viable cells"))
    fig_cells.add_trace(go.Scatter(x=time, y=Xd, mode="lines", name="Dead cells"))
    fig_cells.update_layout(
        title="Cell Growth",
        xaxis_title="Time (hours)",
        yaxis_title="Cell concentration",
        hovermode="x unified",
    )
    st.plotly_chart(fig_cells, use_container_width=True)

    fig_met = go.Figure()
    fig_met.add_trace(go.Scatter(x=time, y=G, mode="lines", name="Glucose"))
    fig_met.add_trace(go.Scatter(x=time, y=L, mode="lines", name="Lactate"))
    fig_met.update_layout(
        title="Metabolic Profile",
        xaxis_title="Time (hours)",
        yaxis_title="Concentration",
        hovermode="x unified",
    )
    st.plotly_chart(fig_met, use_container_width=True)

    fig_product = go.Figure()
    fig_product.add_trace(go.Scatter(x=time, y=P, mode="lines", name="Product"))
    fig_product.update_layout(
        title="Product Formation",
        xaxis_title="Time (hours)",
        yaxis_title="Product concentration",
        hovermode="x unified",
    )
    st.plotly_chart(fig_product, use_container_width=True)

    simulation_data = pd.DataFrame(
        {
            "time_hr": time,
            "viable_cells": Xv,
            "dead_cells": Xd,
            "glucose": G,
            "lactate": L,
            "product": P,
            "volume": V,
        }
    )
    st.download_button(
        "Download Upstream Simulation",
        data=simulation_data.to_csv(index=False),
        file_name="upstream_digital_twin_simulation.csv",
        mime="text/csv",
    )


# ============================================================
# Downstream CADET view
# ============================================================

else:
    st.header("Downstream CADET Purification")

    use_real_results = REAL_CADET_OUTLET_PATH.exists() and REAL_CADET_METRICS_PATH.exists()

    if use_real_results:
        outlet_path = REAL_CADET_OUTLET_PATH
        metrics_path = REAL_CADET_METRICS_PATH
        st.success("Displaying CADET-generated results from the deployed data files.")
    else:
        outlet_path = DEMO_CADET_OUTLET_PATH
        metrics_path = DEMO_CADET_METRICS_PATH
        st.warning(
            "Portfolio preview mode: the displayed downstream curves are an "
            "illustrative demonstration dataset, not a CADET-Core execution on "
            "the Streamlit server. Replace the demo files with "
            "`cadet_capture_outlet.csv` and `cadet_capture_metrics.csv` generated "
            "by the CADET notebook to display real CADET results."
        )

    if not outlet_path.exists() or not metrics_path.exists():
        st.error("Downstream result files are missing from data/processed.")
        st.stop()

    outlet = pd.read_csv(outlet_path)
    metrics = pd.read_csv(metrics_path)
    m = metrics.iloc[0]

    harvest = None
    if OPTIMAL_PROCESS_PATH.exists():
        optimal = pd.read_csv(OPTIMAL_PROCESS_PATH)
        if "optimal_final_product" in optimal.columns:
            harvest = float(optimal.loc[0, "optimal_final_product"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Upstream Harvest Signal", f"{harvest:.2f}" if harvest is not None else "N/A")
    c2.metric("Apparent Product Purity", f"{100 * float(m['apparent_product_purity']):.1f}%")
    c3.metric("Product Peak Time", f"{float(m['product_peak_time_s']):.0f} s")
    c4.metric("Peak Separation", f"{float(m['peak_separation_s']):.0f} s")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=outlet["time_s"], y=outlet["Product"], mode="lines", name="Product"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=outlet["time_s"], y=outlet["Impurity"], mode="lines", name="Impurity"
        )
    )
    fig.update_layout(
        title="Capture Column Outlet Chromatogram",
        xaxis_title="Time (s)",
        yaxis_title="Outlet concentration / normalized signal",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    summary = pd.DataFrame(
        {
            "Metric": [
                "Product integrated signal",
                "Impurity integrated signal",
                "Apparent product purity",
                "Product peak time (s)",
                "Impurity peak time (s)",
                "Peak separation (s)",
            ],
            "Value": [
                m["product_integrated_signal"],
                m["impurity_integrated_signal"],
                m["apparent_product_purity"],
                m["product_peak_time_s"],
                m["impurity_peak_time_s"],
                m["peak_separation_s"],
            ],
        }
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)

    with st.expander("What this module demonstrates"):
        st.markdown(
            """
            - CADET-compatible downstream result handling
            - Multi-component chromatography visualization
            - Product / impurity peak analysis
            - Separation and apparent-purity metrics
            - Integration with an upstream mechanistic digital twin

            **Scientific note:** the included preview dataset is illustrative.
            For a portfolio claim of executed CADET-Core simulation, deploy the
            CSV outputs generated by the accompanying CADET notebook.
            """
        )

    st.download_button(
        "Download Chromatogram",
        data=outlet.to_csv(index=False),
        file_name="capture_outlet.csv",
        mime="text/csv",
    )


st.markdown("---")
st.caption(
    "Integrated mechanistic bioprocess digital twin | "
    "Python • SciPy • CADET-Core / CADET-Process workflow • Streamlit • Plotly"
)
