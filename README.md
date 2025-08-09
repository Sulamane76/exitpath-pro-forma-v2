# ExitPath Decision Intelligence Platform

An objective-driven financial intelligence platform for strategic planning, fundraising, and M&A analysis, built on a flexible, hybrid financial modeling engine.

---

## Core Pillars

This platform is architected around four key principles to deliver a market-leading experience:

1.  **Objective-Driven UI:** The interface and analysis adapt to the user's primary goal (e.g., VC Fundraising, M&A, Bank Loan), presenting the most relevant metrics, language, and modules first.

2.  **Hybrid Financial Engine:** The core engine is built with modularity in mind, allowing users to flexibly model both SaaS/Recurring and Consulting/Services business lines simultaneously, with full control over every input.

3.  **AI-Powered Intelligence:** The platform features two core AI components:
    *   **"Brutal Facts" Narrative Engine:** Generates a dynamic, prose-based summary of the strategic situation after each model run.
    *   **"ExitPath Analyst" Co-Pilot:** A conversational AI for interactive deep-dives, diagnostics, and "what-if" scenario exploration.

4.  **Proprietary EEP Integration:** Allows users to "supercharge" forecasts by inputting scores from ExitPath's proprietary Exit Enablement Platform (EEP) reports, which apply context-aware risk and opportunity modifiers to the model.

## Technology Stack

*   **Backend:** Python
*   **Frontend:** Streamlit
*   **Data Handling:** Pandas, NumPy
*   **AI/LLM:** OpenAI API (or similar)

## Local Setup & Execution

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Sulamane76/exitpath-pro-forma-v2.git
    cd exitpath-pro-forma-v2
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    streamlit run webapp.py
    ```
