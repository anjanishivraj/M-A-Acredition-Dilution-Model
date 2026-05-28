import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="M&A Accretion/Dilution Model",
    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("Institutional M&A Accretion/Dilution Platform")

st.markdown("""
Interactive transaction modeling dashboard built using Python and Streamlit.
""")

# ---------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------

st.sidebar.header("Transaction Assumptions")

buyer_net_income = st.sidebar.slider(
    "Buyer Net Income ($M)",
    100,
    10000,
    2500
)

buyer_shares = st.sidebar.slider(
    "Buyer Shares Outstanding (M)",
    10,
    5000,
    1000
)

target_net_income = st.sidebar.slider(
    "Target Net Income ($M)",
    10,
    5000,
    800
)

purchase_price = st.sidebar.slider(
    "Purchase Price ($M)",
    100,
    50000,
    12000
)

debt_percentage = st.sidebar.slider(
    "Debt Financing %",
    0,
    100,
    60
)

interest_rate = st.sidebar.slider(
    "Interest Rate %",
    1.0,
    15.0,
    6.0
)

tax_rate = st.sidebar.slider(
    "Tax Rate %",
    0,
    50,
    25
)

synergies = st.sidebar.slider(
    "Annual Synergies ($M)",
    0,
    2000,
    300
)

share_price = st.sidebar.slider(
    "Buyer Share Price ($)",
    10,
    1000,
    100
)

# ---------------------------------------------------
# CORE CALCULATIONS
# ---------------------------------------------------

buyer_eps = buyer_net_income / buyer_shares

debt_financing = purchase_price * (debt_percentage / 100)

equity_financing = purchase_price - debt_financing

interest_expense = debt_financing * (interest_rate / 100)

after_tax_interest = interest_expense * (1 - tax_rate / 100)

new_shares_issued = equity_financing / share_price

pro_forma_net_income = (
    buyer_net_income
    + target_net_income
    + synergies
    - after_tax_interest
)

pro_forma_shares = buyer_shares + new_shares_issued

pro_forma_eps = pro_forma_net_income / pro_forma_shares

accretion_dilution = (
    (pro_forma_eps - buyer_eps)
    / buyer_eps
) * 100

# ---------------------------------------------------
# KPI METRICS
# ---------------------------------------------------

st.subheader("Transaction Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Buyer EPS",
    f"${buyer_eps:.2f}"
)

col2.metric(
    "Pro Forma EPS",
    f"${pro_forma_eps:.2f}"
)

col3.metric(
    "Accretion / Dilution %",
    f"{accretion_dilution:.2f}%"
)

# ---------------------------------------------------
# FINANCING STRUCTURE CHART
# ---------------------------------------------------

st.subheader("Financing Structure")

fig_financing = go.Figure(
    data=[
        go.Pie(
            labels=["Debt", "Equity"],
            values=[debt_financing, equity_financing],
            hole=0.4
        )
    ]
)

st.plotly_chart(fig_financing, use_container_width=True)

# ---------------------------------------------------
# EPS BRIDGE CHART
# ---------------------------------------------------

st.subheader("EPS Bridge Analysis")

bridge_labels = [
    "Buyer NI",
    "Target NI",
    "Synergies",
    "Interest Expense"
]

bridge_values = [
    buyer_net_income,
    target_net_income,
    synergies,
    -after_tax_interest
]

fig_bridge = go.Figure()

fig_bridge.add_trace(
    go.Bar(
        x=bridge_labels,
        y=bridge_values
    )
)

st.plotly_chart(fig_bridge, use_container_width=True)

# ---------------------------------------------------
# SENSITIVITY ANALYSIS
# ---------------------------------------------------

st.subheader("Sensitivity Analysis")

premium_range = np.arange(-10, 31, 5)
synergy_range = np.arange(0, 601, 100)

sensitivity_matrix = []

for synergy in synergy_range:

    row = []

    for premium in premium_range:

        adjusted_purchase_price = (
            purchase_price * (1 + premium / 100)
        )

        adjusted_debt = (
            adjusted_purchase_price
            * (debt_percentage / 100)
        )

        adjusted_equity = (
            adjusted_purchase_price
            - adjusted_debt
        )

        adjusted_interest = (
            adjusted_debt
            * (interest_rate / 100)
        )

        adjusted_after_tax_interest = (
            adjusted_interest
            * (1 - tax_rate / 100)
        )

        adjusted_new_shares = (
            adjusted_equity / share_price
        )

        adjusted_net_income = (
            buyer_net_income
            + target_net_income
            + synergy
            - adjusted_after_tax_interest
        )

        adjusted_shares = (
            buyer_shares
            + adjusted_new_shares
        )

        adjusted_eps = (
            adjusted_net_income
            / adjusted_shares
        )

        adjusted_acc_dil = (
            (adjusted_eps - buyer_eps)
            / buyer_eps
        ) * 100

        row.append(round(adjusted_acc_dil, 2))

    sensitivity_matrix.append(row)

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=sensitivity_matrix,
        x=premium_range,
        y=synergy_range
    )
)

fig_heatmap.update_layout(
    xaxis_title="Purchase Premium %",
    yaxis_title="Synergies ($M)"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------------------------------
# SCENARIO ANALYSIS
# ---------------------------------------------------

st.subheader("Scenario Analysis")

scenario_df = pd.DataFrame({
    "Scenario": ["Bear", "Base", "Bull"],
    "Synergies": [100, synergies, 600],
    "Interest Rate": [8, interest_rate, 4]
})

st.dataframe(scenario_df)

# ---------------------------------------------------
# EXPORTABLE EXCEL MODEL
# ---------------------------------------------------

def create_excel_file():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine='xlsxwriter'
    ) as writer:

        assumptions_df = pd.DataFrame({
            "Metric": [
                "Buyer Net Income",
                "Buyer Shares",
                "Target Net Income",
                "Purchase Price",
                "Debt Financing %",
                "Interest Rate %",
                "Tax Rate %",
                "Synergies",
                "Share Price"
            ],
            "Value": [
                buyer_net_income,
                buyer_shares,
                target_net_income,
                purchase_price,
                debt_percentage,
                interest_rate,
                tax_rate,
                synergies,
                share_price
            ]
        })

        results_df = pd.DataFrame({
            "Metric": [
                "Buyer EPS",
                "Pro Forma EPS",
                "Accretion/Dilution %",
                "Debt Financing",
                "Equity Financing",
                "New Shares Issued"
            ],
            "Value": [
                buyer_eps,
                pro_forma_eps,
                accretion_dilution,
                debt_financing,
                equity_financing,
                new_shares_issued
            ]
        })

        sensitivity_df = pd.DataFrame(
            sensitivity_matrix,
            columns=premium_range,
            index=synergy_range
        )

        assumptions_df.to_excel(
            writer,
            sheet_name="Assumptions",
            index=False
        )

        results_df.to_excel(
            writer,
            sheet_name="Results",
            index=False
        )

        sensitivity_df.to_excel(
            writer,
            sheet_name="Sensitivity"
        )

    processed_data = output.getvalue()

    return processed_data

excel_file = create_excel_file()

st.download_button(
    label="Download Excel Financial Model",
    data=excel_file,
    file_name="ma_accretion_dilution_model.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.caption(
    "Built using Python, Streamlit, Pandas, NumPy, and Plotly"
)
