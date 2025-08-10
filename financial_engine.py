import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def run_financial_model(inputs: dict):
    MONTHS = 60
    start_date = datetime.now()
    months = [d.strftime('%b-%y') for d in (start_date + relativedelta(months=i) for i in range(MONTHS))]
    
    # --- FUNNEL & GTM ENGINE ---
    sdr_headcount = np.zeros(MONTHS); ae_headcount = np.zeros(MONTHS)
    ae_hires = np.zeros(MONTHS); ae_headcount[0] = 1 # Start with 1 AE
    sdr_headcount.fill(ae_headcount[0] * inputs.get('sdr_per_ae', 0)) # simplified for now
    
    leads = sdr_headcount * inputs.get('leads_per_sdr', 0)
    market_fit_sales = leads * (inputs.get('lead_to_marketfit_pct', 0) / 100)
    company_fit_sales = np.roll(market_fit_sales, 1) * (inputs.get('marketfit_to_companyfit_pct', 0) / 100)
    ready_sales = np.roll(company_fit_sales, 1) * (inputs.get('companyfit_to_ready_pct', 0) / 100)
    go_transactions = np.roll(ready_sales, 1) * (inputs.get('ready_to_go_pct', 0) / 100)
    
    funnel_df = pd.DataFrame({
        "Leads Generated": leads, "Market Fit Deals": market_fit_sales,
        "Company Fit Deals": company_fit_sales, "Ready Deals": ready_sales,
        "Go Transactions": go_transactions
    }, index=months)

    # --- REVENUE & COSTS ---
    rev_market_fit = market_fit_sales * inputs.get('price_market_fit', 0)
    rev_company_fit = company_fit_sales * inputs.get('price_company_fit', 0)
    rev_ready = ready_sales * inputs.get('price_ready', 0)
    rev_go = go_transactions * inputs.get('avg_deal_size_go', 0) * (inputs.get('fee_pct_go', 0) / 100)
    
    platform_mrr = np.zeros(MONTHS)
    platform_mrr[0] = inputs.get('investor_license_start_mrr', 1000)
    for t in range(1, MONTHS):
        new_licenses_mrr = (inputs.get('new_investor_licenses_q', 0) * inputs.get('investor_license_price', 0)) if (t % 3 == 0) else 0
        churn_mrr_val = platform_mrr[t-1] * (inputs.get('platform_churn_pct', 0) / 100 / 12)
        expansion_mrr_val = platform_mrr[t-1] * (inputs.get('platform_expansion_pct', 0) / 100 / 12)
        platform_mrr[t] = platform_mrr[t-1] + new_licenses_mrr - churn_mrr_val + expansion_mrr_val
        
    total_revenue = rev_market_fit + rev_company_fit + rev_ready + rev_go + platform_mrr

    quarters = np.floor(np.arange(MONTHS) / 3)
    efficiency_multiplier = (1 - (inputs.get('analyst_efficiency_gain_pct', 0) / 100)) ** quarters
    hours_per_report = inputs.get('analyst_hours_start', 0) * efficiency_multiplier
    cogs_delivery = (market_fit_sales + company_fit_sales + ready_sales) * hours_per_report * inputs.get('analyst_hourly_cost', 0)
    cogs_go = go_transactions * inputs.get('additional_hours_go', 0) * inputs.get('analyst_hourly_cost', 0)
    total_cogs = cogs_delivery + cogs_go

    cs_headcount = np.zeros(MONTHS); cs_headcount.fill(ae_headcount[0] * inputs.get('cs_per_ae', 0))
    sdr_salary = inputs.get('ae_ote', 0) * 0.5 / 12
    ae_salary = inputs.get('ae_ote', 0) / 12
    cs_salary = inputs.get('cs_salary', 0) / 12
    base_payroll = (sdr_headcount * sdr_salary) + (ae_headcount * ae_salary) + (cs_headcount * cs_salary)
    tax_burden = base_payroll * (inputs.get('benefits_tax_pct', 0) / 100)
    total_payroll = base_payroll + tax_burden
    commissions = (rev_market_fit + rev_company_fit + rev_ready + rev_go) * (inputs.get('sales_commission_pct', 0) / 100)
    g_and_a = total_revenue * (inputs.get('ga_overhead_pct', 0) / 100)
    total_opex = total_payroll + commissions + g_and_a

    # --- 3-STATEMENT MODEL ---
    pnl = pd.DataFrame(index=months)
    pnl["Revenue"] = total_revenue
    pnl["COGS"] = total_cogs
    pnl["Gross Profit"] = pnl["Revenue"] - pnl["COGS"]
    pnl["Operating Expenses"] = total_opex
    pnl["EBITDA"] = pnl["Gross Profit"] - pnl["Operating Expenses"]
    pnl["Net Income"] = pnl["EBITDA"] # Simplified

    bs = pd.DataFrame(0, index=months, columns=['Cash', 'Accounts Receivable', 'Total Assets', 'Accounts Payable', 'Equity', 'Total Liabilities & Equity'])
    cfs = pd.DataFrame(0, index=months, columns=['Net Income', 'Change in AR', 'Change in AP', 'CFO', 'CapEx', 'CFI', 'Funding', 'CFF', 'Net Change in Cash'])

    funding = np.zeros(MONTHS)
    seed_month = inputs.get('seed_month', 1) - 1
    series_a_month = inputs.get('series_a_month', 1) - 1
    if 0 <= seed_month < MONTHS: funding[seed_month] = inputs.get('seed_amount', 0)
    if 0 <= series_a_month < MONTHS: funding[series_a_month] = inputs.get('series_a_amount', 0)
    
    bs.loc[months[0], 'Cash'] = funding[0] + inputs.get('starting_cash', 50000)
    bs.loc[months[0], 'Equity'] = funding[0] + inputs.get('starting_cash', 50000)
    
    for t in range(1, MONTHS):
        ar_t = total_revenue[t] * (inputs.get('ar_days', 45) / 30.4)
        ar_t_minus_1 = bs.loc[months[t-1], 'Accounts Receivable']
        change_in_ar = -(ar_t - ar_t_minus_1)
        
        ap_t = total_opex[t] * (inputs.get('ap_days', 30) / 30.4)
        ap_t_minus_1 = bs.loc[months[t-1], 'Accounts Payable']
        change_in_ap = ap_t - ap_t_minus_1
        
        cfs.loc[months[t], 'Net Income'] = pnl.loc[months[t], 'Net Income']
        cfs.loc[months[t], 'Change in AR'] = change_in_ar
        cfs.loc[months[t], 'Change in AP'] = change_in_ap
        cfs.loc[months[t], 'CFO'] = cfs.loc[months[t], 'Net Income'] + change_in_ar + change_in_ap
        
        capex = -inputs.get('capex_per_new_hire', 0) * (ae_hires[t])
        cfs.loc[months[t], 'CFI'] = capex
        cfs.loc[months[t], 'CFF'] = funding[t]
        
        net_cash_change = cfs.loc[months[t], 'CFO'] + cfs.loc[months[t], 'CFI'] + cfs.loc[months[t], 'CFF']
        cfs.loc[months[t], 'Net Change in Cash'] = net_cash_change
        
        bs.loc[months[t], 'Cash'] = bs.loc[months[t-1], 'Cash'] + net_cash_change
        bs.loc[months[t], 'Accounts Receivable'] = ar_t
        bs.loc[months[t], 'Accounts Payable'] = ap_t
        bs.loc[months[t], 'Equity'] = bs.loc[months[t-1], 'Equity'] + pnl.loc[months[t], 'Net Income'] + funding[t]
        bs.loc[months[t], 'Total Assets'] = bs.loc[months[t], 'Cash'] + bs.loc[months[t], 'Accounts Receivable']
        bs.loc[months[t], 'Total Liabilities & Equity'] = bs.loc[months[t], 'Accounts Payable'] + bs.loc[months[t], 'Equity']

    # --- KPI CALCULATIONS ---
    kpis = pd.DataFrame(index=months)
    
    monthly_churn = inputs.get('platform_churn_pct', 0) / 100 / 12
    monthly_expansion = inputs.get('platform_expansion_pct', 0) / 100 / 12
    kpis['Net Dollar Retention'] = 1 - monthly_churn + monthly_expansion
    
    # CAC: Simplified as total payroll + commissions / number of new deals
    new_deals_count = market_fit_sales # Use this as the proxy for 'new customers'
    kpis['CAC'] = np.divide(total_payroll + commissions, new_deals_count, out=np.zeros_like(total_payroll), where=new_deals_count!=0)

    # LTV: Avg Monthly Rev per new deal * Gross Margin % * Customer Lifetime
    avg_monthly_rev_per_deal = np.divide(rev_market_fit, new_deals_count, out=np.zeros_like(rev_market_fit), where=new_deals_count!=0)
    gross_margin_pct = np.divide(pnl['Gross Profit'], pnl['Revenue'], out=np.zeros_like(pnl['Gross Profit']), where=pnl['Revenue']!=0)
    customer_lifetime_months = 1 / max(monthly_churn, 0.001) # Avoid division by zero
    kpis['LTV'] = avg_monthly_rev_per_deal * gross_margin_pct * customer_lifetime_months
    
    kpis['LTV/CAC'] = np.divide(kpis['LTV'], kpis['CAC'], out=np.zeros_like(kpis['LTV']), where=kpis['CAC']!=0)
    
    # Payback Period (Months) = CAC / (Avg Monthly Rev per Deal * Gross Margin %)
    monthly_profit_per_deal = avg_monthly_rev_per_deal * gross_margin_pct
    kpis['Payback Period (Months)'] = np.divide(kpis['CAC'], monthly_profit_per_deal, out=np.zeros_like(kpis['CAC']), where=monthly_profit_per_deal!=0)

    return {
        "pnl": pnl.round(0), "bs": bs.round(0), "cfs": cfs.round(0),
        "kpis": kpis.round(2), "funnel": funnel_df.round(0)
    }
