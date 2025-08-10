import streamlit as st
import streamlit.components.v1 as components # <-- NEW, MORE POWERFUL IMPORT

def render_bowtie(funnel_data, pnl_data, inputs):
    """
    Renders the upgraded, interactive Strategic Bowtie Funnel.
    Visualizes the full customer journey from acquisition to expansion.
    """
    if funnel_data is None or funnel_data.empty or pnl_data is None or pnl_data.empty:
        st.info("The Bowtie Funnel will be visualized here once the model is run.")
        return

    # (All the data calculation logic from before remains exactly the same)
    timeframe = st.selectbox(
        "Select Funnel Timeframe:",
        ["Year 1", "Year 2", "Full Forecast"],
        key="bowtie_timeframe",
        label_visibility="collapsed"
    )

    if timeframe == "Year 1": start_idx, end_idx = 0, 12
    elif timeframe == "Year 2": start_idx, end_idx = 12, 24
    else: start_idx, end_idx = 0, len(funnel_data)
    
    period_funnel = funnel_data.iloc[start_idx:end_idx].sum()
    leads = period_funnel.get("Leads Generated", 0)
    market_fit = period_funnel.get("Market Fit Deals", 0)
    ready = period_funnel.get("Ready Deals", 0)
    rev_market_fit = market_fit * inputs.get('price_market_fit', 0)
    rev_ready = ready * inputs.get('price_ready', 0)
    platform_mrr_series = pnl_data['Revenue']
    churn_rate_monthly = inputs.get('platform_churn_pct', 0) / 100 / 12
    expansion_rate_monthly = inputs.get('platform_expansion_pct', 0) / 100 / 12
    churned_mrr = (platform_mrr_series.shift(1) * churn_rate_monthly).iloc[start_idx:end_idx].sum()
    expansion_mrr = (platform_mrr_series.shift(1) * expansion_rate_monthly).iloc[start_idx:end_idx].sum()
    lead_to_mf_pct = inputs.get('lead_to_marketfit_pct', 0)

    # --- Custom HTML & CSS for the Upgraded Bowtie ---
    bowtie_html = f"""
    <html>
    <head>
    <style>
        body {{ background-color: #161B22; color: #F0F7F4; }} /* Match container background */
        .bowtie-container {{ display: flex; justify-content: center; align-items: stretch; gap: 10px; }}
        .bowtie-col {{ flex: 1; text-align: center; display: flex; flex-direction: column; justify-content: center; }}
        .bowtie-stage {{
            background-color: #0E1428; border: 1px solid #337CA0; border-radius: 8px;
            padding: 8px; margin-bottom: 8px; min-height: 90px;
        }}
        .bowtie-stage-center {{
            background-color: #0E1428; border: 2px solid #EF6500; border-radius: 8px;
            padding: 15px; font-weight: bold; min-height: 90px;
            display: flex; flex-direction: column; justify-content: center;
        }}
        .bowtie-label {{ font-size: 1rem; font-weight: 600; color: #F0F7F4; }}
        .bowtie-value-count {{ font-size: 1.3rem; font-weight: bold; color: #EF6500; }}
        .bowtie-value-revenue {{ font-size: 0.9rem; color: #C1BDB3; margin-top: 4px;}}
        .conversion-arrow {{ color: #337CA0; font-size: 1.2rem; margin-bottom: 8px;}}
        .conversion-rate {{ font-size: 0.8rem; color: #F0F7F4; font-weight: bold; }}
    </style>
    </head>
    <body>
    <div class="bowtie-container">
        <!-- Left Arm: Convert -->
        <div class="bowtie-col">
            <div class="bowtie-stage">
                <div class="bowtie-label">Leads</div>
                <div class="bowtie-value-count">{leads:,.0f}</div>
            </div>
            <div class="conversion-arrow">▼ <span class="conversion-rate">{lead_to_mf_pct}%</span></div>
            <div class="bowtie-stage">
                <div class="bowtie-label">Market Fit</div>
                <div class="bowtie-value-count">{market_fit:,.0f}</div>
                <div class="bowtie-value-revenue">${rev_market_fit:,.0f}</div>
            </div>
        </div>
        
        <!-- Center: Commit -->
        <div class="bowtie-col">
             <div class="bowtie-stage-center">
                <div class="bowtie-label">Ready Deals</div>
                <div class="bowtie-value-count">{ready:,.0f}</div>
                <div class="bowtie-value-revenue">${rev_ready:,.0f}</div>
            </div>
        </div>
        
        <!-- Right Arm: Expand -->
        <div class="bowtie-col">
            <div class="bowtie-stage">
                <div class="bowtie-label">Expansion Revenue</div>
                <div class="bowtie-value-count">${expansion_mrr:,.0f}</div>
            </div>
             <div class="conversion-arrow" style="color:#D22B2B;">▼</div>
            <div class="bowtie-.stage">
                <div class="bowtie-label">Churned Revenue</div>
                <div class="bowtie-value-count">${churned_mrr:,.0f}</div>
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    
    # --- THIS IS THE CRITICAL CHANGE ---
    # We are using components.html to force rendering in a dedicated iframe.
    components.html(bowtie_html, height=250)
