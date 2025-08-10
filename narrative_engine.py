import pandas as pd
import numpy as np

def generate_narrative(results: dict):
    """
    Analyzes the financial results to produce a Collins/Dalio-style strategic narrative.
    """
    pnl = results['pnl']
    bs = results['bs']
    kpis = results['kpis']

    # --- Analysis ---
    # 1. Cash Runway
    last_12m_cfo = pnl['EBITDA'].iloc[-12:].mean() if 'EBITDA' in pnl.columns else 0 # Simplified burn
    ending_cash = bs['Cash'].iloc[-1] if not bs.empty else 0
    cash_runway_months = (ending_cash / abs(last_12m_cfo)) if last_12m_cfo < 0 else 999

    # 2. Profitability
    try:
        breakeven_month = pnl[pnl['EBITDA'] > 0].index[0]
    except IndexError:
        breakeven_month = "Not within forecast"

    # 3. Capital Efficiency
    final_ltv_cac = kpis['LTV/CAC'].iloc[-1] if not kpis.empty else 0
    final_payback = kpis['Payback Period (Months)'].iloc[-1] if not kpis.empty else 0

    # --- Narrative Generation ---
    flywheel_points = []
    brutal_facts_points = []

    # Flywheel Analysis
    if final_ltv_cac > 3:
        flywheel_points.append(f"**Strong Capital Efficiency:** The model projects a final LTV/CAC ratio of **{final_ltv_cac:.1f}x**, which is above the 3.0x benchmark for a healthy, scalable GTM motion.")
    if final_payback > 0 and final_payback < 18:
        flywheel_points.append(f"**Fast Sales Velocity:** With a payback period of **{final_payback:.1f} months**, new customers become profitable quickly, allowing for rapid reinvestment in growth.")
    if breakeven_month != "Not within forecast":
        flywheel_points.append(f"**Path to Profitability:** The business is projected to reach EBITDA breakeven in **{breakeven_month}**, demonstrating a clear path to self-sustainability.")

    # Brutal Facts Analysis
    if cash_runway_months <= 12:
        brutal_facts_points.append(f"**Limited Cash Runway:** The current burn rate results in a cash runway of only **{cash_runway_months:.0f} months**, creating significant near-term financing risk.")
    if final_ltv_cac < 2:
        brutal_facts_points.append(f"**Inefficient Growth Engine:** The LTV/CAC ratio of **{final_ltv_cac:.1f}x** is below the 2.0x survival benchmark. The business is spending too much to acquire customers relative to their lifetime value.")
    if final_payback > 24:
        brutal_facts_points.append(f"**Slow Capital Recovery:** A payback period of **{final_payback:.1f} months** means capital is tied up for over two years for each new customer, severely constraining growth without external funding.")
    if not flywheel_points:
         flywheel_points.append("The model does not currently indicate a strong, self-sustaining growth flywheel. Key metrics for efficiency and profitability are below standard benchmarks.")
    if not brutal_facts_points:
        brutal_facts_points.append("The model does not indicate any immediate critical risks based on standard financial benchmarks. The primary focus should be on scaling the existing strengths.")

    # Crossroads Synthesis
    crossroads = "Based on this forecast, the primary strategic decision is whether to **optimize the current model** for efficiency or to **aggressively fund the existing GTM motion** to capture market share."
    if cash_runway_months < 12 and final_ltv_cac > 3:
        crossroads = "The primary strategic decision is clear: **Secure funding immediately** to fuel your highly efficient growth engine before you run out of capital."
    elif final_ltv_cac < 2:
        crossroads = "The primary strategic decision is to **pause aggressive growth** and fundamentally re-evaluate the GTM strategy to fix the underlying issues with capital efficiency."


    return {
        "flywheel": "\n".join(f"- {point}" for point in flywheel_points),
        "brutal_facts": "\n".join(f"- {point}" for point in brutal_facts_points),
        "crossroads": crossroads
    }
