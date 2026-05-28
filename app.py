import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="M&A Accretion/Dilution Modeling",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# FINANCIAL MODEL ENGINE
# =========================

def calculate_transaction(
    buyer_net_income,
    buyer_shares,
    buyer_share_price,
    target_net_income,
    purchase_price,
    debt_pct,
    equity_pct,
    interest_rate,
    synergies,
    tax_rate
):

    # Financing calculations
    debt_raised = purchase_price * debt_pct
    equity_issued = purchase_price * equity_pct

    # Shares issued
    new_shares = equity_issued / buyer_share_price

    # Interest expense
    interest_expense = debt_raised * interest_rate
    after_tax_interest = interest_expense * (1 - tax_rate)

    # EPS calculations
    buyer_eps = buyer_net_income / buyer_shares

    pro_forma_net_income = (
        buyer_net_income
        + target_net_income
        + synergies
        - after_tax_interest
    )

    pro_forma_shares = buyer_shares + new_shares

    pro_forma_eps = pro_forma_net_income / pro_forma_shares

    accretion_dilution = (
        (pro_forma_eps - buyer_eps) / buyer_eps
    )

    return {
        "buyer_eps": buyer_eps,
        "debt_raised": debt_raised,
        "equity_issued": equity_issued,
        "new_shares": new_shares,
        "interest_expense": interest_expense,
        "after_tax_interest": after_tax_interest,
        "pro_forma_net_income": pro_forma_net_income,
        "pro_forma_shares": pro_forma_shares,
        "pro_forma_eps": pro_forma_eps,
        "accretion_dilution": accretion_dilution
    }


# =========================
# SIDEBAR INPUTS
# =========================

st.sidebar.title("Transaction Assumptions")

st.sidebar.subheader("Buyer Information")

buyer_net_income = st.sidebar.number_input(
    "Buyer Net Income",
    value=500.0,
    step=10.0
)

buyer_shares = st.sidebar.number_input(
    "Buyer Shares Outstanding",
    value=100.0,
    step=1.0
)

buyer_share_price = st.sidebar.number_input(
    "Buyer Share Price",
    value=50.0,
    step=1.0
)

st.sidebar.subheader("Target Information")

target_net_income = st.sidebar.number_input(
    "Target Net Income",
    value=80.0,
    step=5.0
)

purchase_price = st.sidebar.number_input(
    "Purchase Price",
    value=1200.0,
    step=50.0
)

st.sidebar.subheader("Deal Assumptions")

debt_pct = st.sidebar.slider(
    "Debt Financing %",
    min_value=0,
    max_value=100,
    value=60
) / 100

equity_pct = 1 - debt_pct

interest_rate = st.sidebar.slider(
    "Interest Rate %",
    min_value=0.0,
    max_value=15.0,
    value=6.0
) / 100

synergies = st.sidebar.number_input(
    "Synergies",
    value=20.0,
    step=5.0
)

tax_rate = st.sidebar.slider(
    "Tax Rate %",
    min_value=0.0,
    max_value=50.0,
    value=25.0
) / 100


# =========================
# RUN MODEL
# =========================

results = calculate_transaction(
    buyer_net_income,
    buyer_shares,
    buyer_share_price,
    target_net_income,
    purchase_price,
    debt_pct,
    equity_pct,
    interest_rate,
    synergies,
    tax_rate
)


# =========================
# MAIN DASHBOARD
# =========================

st.title("M&A Accretion/Dilution Model")
st.caption("Excel Financial Modeling + Python Transaction Analysis")


# =========================
# KPI METRICS
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Buyer EPS",
        f"{results['buyer_eps']:.2f}"
    )

with col2:
    st.metric(
        "Pro Forma EPS",
        f"{results['pro_forma_eps']:.2f}"
    )

with col3:
    st.metric(
        "Accretion/Dilution",
        f"{results['accretion_dilution'] * 100:.2f}%"
    )

with col4:
    st.metric(
        "Interest Expense",
        f"{results['interest_expense']:.2f}"
    )

st.divider()


# =========================
# TRANSACTION SUMMARY
# =========================

summary_col1, summary_col2 = st.columns([1, 1])

with summary_col1:

    st.subheader("Transaction Summary")

    summary_df = pd.DataFrame({
        "Metric": [
            "Debt Raised",
            "Equity Issued",
            "New Shares Issued",
            "Pro Forma Net Income",
            "Pro Forma Shares"
        ],
        "Value": [
            results['debt_raised'],
            results['equity_issued'],
            results['new_shares'],
            results['pro_forma_net_income'],
            results['pro_forma_shares']
        ]
    })

    st.dataframe(summary_df, use_container_width=True)


with summary_col2:

    st.subheader("Sources & Uses")

    financing_df = pd.DataFrame({
        "Category": ["Debt", "Equity"],
        "Amount": [
            results['debt_raised'],
            results['equity_issued']
        ]
    })

    pie_chart = px.pie(
        financing_df,
        names="Category",
        values="Amount",
        title="Transaction Financing Mix"
    )

    st.plotly_chart(pie_chart, use_container_width=True)


st.divider()


# =========================
# EPS BRIDGE CHART
# =========================

st.subheader("EPS Bridge Analysis")

bridge_labels = [
    "Buyer EPS",
    "Target Contribution",
    "Synergies",
    "Interest Expense",
    "Pro Forma EPS"
]

bridge_values = [
    results['buyer_eps'],
    target_net_income / buyer_shares,
    synergies / buyer_shares,
    -results['after_tax_interest'] / buyer_shares,
    results['pro_forma_eps']
]

bridge_fig = go.Figure(go.Waterfall(
    name="EPS Bridge",
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "total"],
    x=bridge_labels,
    y=bridge_values
))

bridge_fig.update_layout(
    title="EPS Impact Analysis"
)

st.plotly_chart(bridge_fig, use_container_width=True)


# =========================
# SENSITIVITY ANALYSIS
# =========================

st.subheader("Sensitivity Analysis")

premium_range = [0.10, 0.20, 0.30, 0.40, 0.50]
synergy_range = [0, 10, 20, 30, 40]

heatmap_data = []

for synergy in synergy_range:

    row = []

    for premium in premium_range:

        adjusted_purchase_price = purchase_price * (1 + premium)

        sensitivity_results = calculate_transaction(
            buyer_net_income,
            buyer_shares,
            buyer_share_price,
            target_net_income,
            adjusted_purchase_price,
            debt_pct,
            equity_pct,
            interest_rate,
            synergy,
            tax_rate
        )

        row.append(sensitivity_results['accretion_dilution'] * 100)

    heatmap_data.append(row)

heatmap_df = pd.DataFrame(
    heatmap_data,
    index=[f"{x}" for x in synergy_range],
    columns=[f"{int(x*100)}%" for x in premium_range]
)

heatmap = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto",
    labels=dict(
        x="Purchase Premium",
        y="Synergies",
        color="Accretion/Dilution %"
    ),
    title="Accretion/Dilution Sensitivity Matrix"
)

st.plotly_chart(heatmap, use_container_width=True)


# =========================
# SCENARIO ANALYSIS
# =========================

st.subheader("Scenario Analysis")

scenario_df = pd.DataFrame({
    "Scenario": ["Bear", "Base", "Bull"],
    "Synergies": [10, 20, 40],
    "Interest Rate": [0.08, 0.06, 0.04]
})

scenario_outputs = []

for _, row in scenario_df.iterrows():

    scenario_result = calculate_transaction(
        buyer_net_income,
        buyer_shares,
        buyer_share_price,
        target_net_income,
        purchase_price,
        debt_pct,
        equity_pct,
        row['Interest Rate'],
        row['Synergies'],
        tax_rate
    )

    scenario_outputs.append(
        scenario_result['accretion_dilution'] * 100
    )

scenario_df['Accretion/Dilution %'] = scenario_outputs

scenario_chart = px.bar(
    scenario_df,
    x="Scenario",
    y="Accretion/Dilution %",
    title="Scenario Analysis"
)

st.plotly_chart(scenario_chart, use_container_width=True)


# =========================
# MODEL ASSUMPTIONS
# =========================

with st.expander("Model Assumptions and Methodology"):

    st.markdown("""
    ### Core Assumptions

    - Financing structure directly impacts EPS through interest expense and share dilution.
    - Debt financing increases leverage and financing costs.
    - Equity financing increases shares outstanding.
    - Synergies are treated as incremental earnings contributions.
    - Interest expense is tax-adjusted.

    ### Financial Logic

    Pro Forma Net Income = Buyer NI + Target NI + Synergies - After-Tax Interest

    Pro Forma EPS = Pro Forma Net Income / Pro Forma Shares

    Accretion/Dilution % = (Pro Forma EPS - Buyer EPS) / Buyer EPS
    """)


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "Built using Python, Streamlit, Pandas, NumPy, and Plotly | "
    
)
