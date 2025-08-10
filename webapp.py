import streamlit as st
import pandas as pd
import io

# Import our other modules
from financial_engine import run_financial_model
from ui_components import render_bowtie
from narrative_engine import generate_narrative
from ai_analyst import query_analyst

# --- Page & State Config ---
st.set_page_config(layout="wide", page_title="ExitPath | Pro Forma Builder")

# --- State Management Initialization ---
if 'inputs' not in st.session_state: st.session_state['inputs'] = {}
if 'run_scenario' not in st.session_state: st.session_state['run_scenario'] = False
if 'results' not in st.session_state: st.session_state['results'] = None

# --- Custom CSS ---
st.markdown("""<style> .stButton>button { width: 100%; } .sidebar-divider { margin-top: 1rem; margin-bottom: 1rem; border-top: 1px solid #337CA0; } .dashboard-container { padding: 1.5rem; background-color: #161B22; border: 1px solid #337CA0; border-radius: 0.5rem; height: 100%; } </style>""", unsafe_allow_html=True)

# --- HEADER & LOGO ---
try:
    st.image("assets/exitpath_logo_white.png", width=250)
except Exception:
    st.error("Logo not found. Ensure `exitpath_logo_white.png` is in `/assets` folder.")

st.title("ExitPath Pro Forma Builder")
st.subheader("Your interactive co-pilot for strategic financial modeling.")
st.write("---")

# --- SIDEBAR - THE CONTROL PANEL ---
st.sidebar.title("Control Panel")

st.sidebar.header("Model Inputs")
with st.sidebar.expander("📈 Go-To-Market & Funnel", expanded=True):
    st.session_state['inputs']['sdr_per_ae'] = st.slider("SDRs per AE", 1, 5, 2, help="The number of SDRs supporting each AE.")
    st.session_state['inputs']['leads_per_sdr'] = st.slider("Leads Generated per SDR per Month", 0, 100, 40, help="Number of qualified leads a fully-ramped SDR generates each month.")
    st.session_state['inputs']['lead_to_marketfit_pct'] = st.slider("Lead to MarketFit (%)", 0, 100, 50)
    st.session_state['inputs']['marketfit_to_companyfit_pct'] = st.slider("MarketFit to CompanyFit (%)", 0, 100, 30)
    st.session_state['inputs']['companyfit_to_ready_pct'] = st.slider("CompanyFit to Ready (%)", 0, 100, 20)
    st.session_state['inputs']['ready_to_go_pct'] = st.slider("Ready to Go (%)", 0, 100, 10)

with st.sidebar.expander("🤖 Product, Pricing & AI", expanded=True):
    st.session_state['inputs']['price_market_fit'] = st.number_input("Price Market Fit ($)", value=500)
    st.session_state['inputs']['price_company_fit'] = st.number_input("Price Company Fit ($)", value=15000)
    st.session_state['inputs']['price_ready'] = st.number_input("Price Ready ($)", value=50000)
    st.session_state['inputs']['fee_pct_go'] = st.number_input("Fee Pct Go (%)", value=1.5)
    st.session_state['inputs']['avg_deal_size_go'] = st.number_input("Avg Deal Size Go ($)", value=75000000)
    st.session_state['inputs']['analyst_hours_start'] = st.slider("Analyst Hours per Report (Start)", 5, 40, 20, help="Initial manual human hours required.")
    st.session_state['inputs']['analyst_efficiency_gain_pct'] = st.slider("Quarterly Efficiency Gain (%)", 0, 25, 10, help="AI-driven reduction in analyst hours.")
    st.session_state['inputs']['additional_hours_go'] = st.slider("Additional Hours for Go Product", 0, 20, 10)
    st.session_state['inputs']['analyst_hourly_cost'] = st.number_input("Analyst Hourly Cost ($)", value=75)

with st.sidebar.expander("💸 Investor Platform & Team", expanded=True):
    st.session_state['inputs']['investor_license_start_mrr'] = st.number_input("Platform Starting MRR ($)", value=1000)
    st.session_state['inputs']['new_investor_licenses_q'] = st.slider("New Investor Licenses per Q", 0, 20, 5)
    st.session_state['inputs']['investor_license_price'] = st.number_input("Investor License Price per Month ($)", value=2500)
    st.session_state['inputs']['platform_churn_pct'] = st.slider("Platform Annual Churn (%)", 0.0, 30.0, 10.0)
    st.session_state['inputs']['platform_expansion_pct'] = st.slider("Platform Annual Expansion (%)", 0.0, 50.0, 15.0)
    st.session_state['inputs']['ae_ote'] = st.number_input("AE OTE ($)", value=150000)
    st.session_state['inputs']['cs_salary'] = st.number_input("CS Rep Annual Salary ($)", value=80000)
    st.session_state['inputs']['benefits_tax_pct'] = st.slider("Benefits & Tax Burden (%)", 15, 40, 25)
    st.session_state['inputs']['sales_commission_pct'] = st.slider("Sales Commission (%)", 5, 20, 10)
    st.session_state['inputs']['ga_overhead_pct'] = st.slider("G&A Overhead (% of Rev)", 5, 25, 15)
    st.session_state['inputs']['capex_per_new_hire'] = st.number_input("CapEx per New Hire ($)", value=3000)
    st.session_state['inputs']['ar_days'] = st.number_input("Accounts Receivable Days", value=45)
    st.session_state['inputs']['ap_days'] = st.number_input("Accounts Payable Days", value=30)
    st.session_state['inputs']['tax_rate_pct'] = st.slider("Effective Tax Rate (%)", 0, 50, 21)

with st.sidebar.expander("💵 Capital Strategy (Fundraise)", expanded=True):
    st.session_state['inputs']['starting_cash'] = st.number_input("Starting Cash Balance ($)", value=50000)
    st.session_state['inputs']['seed_amount'] = st.number_input("Seed Round Amount ($)", value=750000)
    st.session_state['inputs']['seed_month'] = st.slider("Seed Round Closing Month", 1, 60, 1)
    st.session_state['inputs']['series_a_amount'] = st.number_input("Series A Amount ($)", value=1250000)
    st.session_state['inputs']['series_a_month'] = st.slider("Series A Closing Month", 1, 60, 18)

# --- ACTION BUTTONS ---
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
if st.sidebar.button("🚀 Run Scenario", type="primary"):
    st.session_state['results'] = run_financial_model(st.session_state['inputs'])
    st.session_state['run_scenario'] = True
    st.rerun()
if st.sidebar.button("🔄 Reset Inputs"):
    st.session_state.clear()
    st.rerun()
if st.session_state.get('results'):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        st.session_state['results']['pnl'].to_excel(writer, sheet_name='Income Statement')
        st.session_state['results']['bs'].to_excel(writer, sheet_name='Balance Sheet')
        st.session_state['results']['cfs'].to_excel(writer, sheet_name='Cash Flow Statement')
        st.session_state['results']['kpis'].to_excel(writer, sheet_name='KPIs')
    st.sidebar.download_button(
        label="📥 Download Pro Forma (.xlsx)", data=excel_buffer.getvalue(),
        file_name="ExitPath_Pro_Forma.xlsx", mime="application/vnd.ms-excel"
    )

# --- MAIN DASHBOARD AREA ---
if st.session_state.get('run_scenario') and st.session_state.get('results'):
    results = st.session_state['results']
    pnl, bs, kpis = results['pnl'], results['bs'], results['kpis']
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"CEO Dashboard")
    with col2:
        with st.popover("🤖 Ask AI Co-Pilot"):
            st.markdown("Ask a follow-up question about this scenario:")
            user_query = st.text_input("e.g., 'Why is my cash runway so short?'", key="ai_popover_query")
            if user_query:
                with st.spinner("Analyzing..."):
                    response = query_analyst(user_query, results)
                    st.markdown(response)

    st.subheader("Strategic Command Dashboard")
    projection_year = st.selectbox("Select Year for Projections:", [1, 2, 3, 4, 5], index=4)
    start_idx, end_idx = (projection_year - 1) * 12, projection_year * 12
    year_revenue = pnl['Revenue'].iloc[start_idx:end_idx].sum()
    year_ebitda = pnl['EBITDA'].iloc[start_idx:end_idx].sum()
    ending_cash = bs['Cash'].iloc[end_idx - 1] if end_idx <= len(bs) else bs['Cash'].iloc[-1]
    final_ltv_cac, final_payback, final_ndr = (kpis.iloc[-1] if not kpis.empty else [0,0,0])[['LTV/CAC', 'Payback Period (Months)', 'Net Dollar Retention']]
    grade = "B"
    if final_ltv_cac >= 3 and 0 < final_payback <= 18 and final_ndr >= 1.0: grade = "A"
    elif final_ltv_cac < 2 or final_payback > 24 or final_ndr < 0.9: grade = "F"
    grade_rationale = f"""- **LTV/CAC:** {final_ltv_cac:.1f}x\n- **Payback Period:** {final_payback:.1f} months\n- **Net Dollar Retention:** {final_ndr:.1%}"""
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(f"Revenue (Y{projection_year})", f"${year_revenue:,.0f}")
    with col2: st.metric(f"EBITDA (Y{projection_year})", f"${year_ebitda:,.0f}")
    with col3: st.metric(f"Ending Cash (Y{projection_year})", f"${ending_cash:,.0f}")
    with col4: st.metric("Scenario Grade", grade, help=grade_rationale)
    
    st.write("---")
    with st.expander("✨ Supercharge with Your ExitPath EEP Report"):
        # (EEP uploader/manual entry section is unchanged)
        st.info("This is a placeholder for the EEP Report integration.")

    st.write("---")
    narrative = generate_narrative(results)
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("The 'Brutal Facts' Narrative")
        with st.container(border=True):
            st.markdown("##### The Flywheel (Core Strengths)"); st.success(narrative['flywheel'])
            st.markdown("##### The Brutal Facts (Core Weaknesses)"); st.warning(narrative['brutal_facts'])
            st.markdown("##### The Strategic Crossroads"); st.info(narrative['crossroads'])
    with col2:
        st.subheader("Strategic Bowtie Funnel")
        with st.container(border=True):
            # --- CORRECTED BOWTIE CALL ---
            render_bowtie(funnel_data=results['funnel'], pnl_data=pnl, inputs=st.session_state['inputs'])
            
    st.write("---")
    st.subheader("Financial Statements")
    tab1, tab2, tab3, tab4 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow", "KPIs"])
    with tab1: st.dataframe(results['pnl'].transpose().style.format(lambda x: f"${x:,.0f}"))
    with tab2: st.dataframe(results['bs'].transpose().style.format(lambda x: f"${x:,.0f}"))
    with tab3: st.dataframe(results['cfs'].transpose().style.format(lambda x: f"${x:,.0f}"))
    with tab4: st.dataframe(results['kpis'].transpose().style.format("{:,.2f}"))
else:
    st.info("Configure inputs and click 'Run Scenario' to generate your forecast.")
