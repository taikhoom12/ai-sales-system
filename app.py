import streamlit as st
import pandas as pd
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Sales Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# CUSTOM CSS (UI MAGIC)
# =========================
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: 600;
}
.card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
}
.small-text {
    color: #9ca3af;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("🚀 AI Sales Intelligence Dashboard")
st.markdown("Generate **target companies, roles, and outreach messages** with AI")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Campaign Settings")

industry = st.sidebar.selectbox(
    "Industry",
    ["Pharma", "Food", "Textile", "Oil & Gas", "Chemical", "Cement"]
)

num_companies = st.sidebar.slider("Companies", 3, 10, 5)

tone = st.sidebar.selectbox(
    "Tone",
    ["Professional", "Friendly", "Direct"]
)

# =========================
# AI FUNCTIONS
# =========================
def generate_companies(industry, n):
    prompt = f"""
    List {n} real companies in Pakistan in the {industry} industry.
    Only return names.
    """

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return [
        c.strip("- ").strip()
        for c in res.choices[0].message.content.split("\n")
        if c.strip()
    ]


def generate_leads(company, industry, tone):
    prompt = f"""
    For {company} in {industry}:

    Give 2 roles responsible for procurement.
    For each role write a short {tone.lower()} outreach message.

    Format:
    Role: ...
    Message: ...
    """

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# TABS (CLEAN UX)
# =========================
tab1, tab2 = st.tabs(["📊 Generate Leads", "📁 Results"])

# =========================
# TAB 1 — GENERATE
# =========================
with tab1:

    st.markdown("### Generate AI Leads")

    if st.button("🔥 Run AI Campaign"):

        with st.spinner("AI researching..."):
            companies = generate_companies(industry, num_companies)

        results = []

        progress = st.progress(0)

        for i, company in enumerate(companies):

            st.markdown(f"<div class='card'>🔍 {company}</div>", unsafe_allow_html=True)

            output = generate_leads(company, industry, tone)

            results.append({
                "Company": company,
                "Output": output
            })

            progress.progress((i + 1) / len(companies))

        st.session_state["results"] = pd.DataFrame(results)

        st.success("✅ Campaign Completed")

# =========================
# TAB 2 — RESULTS
# =========================
with tab2:

    if "results" in st.session_state:

        df = st.session_state["results"]

        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("Companies Generated", len(df))
        col2.metric("Total Messages", len(df) * 2)

        st.markdown("---")

        # Search
        search = st.text_input("🔍 Search company")

        if search:
            df = df[df["Company"].str.contains(search, case=False)]

        # Display cards instead of ugly table
        for i, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4>{row['Company']}</h4>
                <p class="small-text">{row['Output']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "leads.csv")

    else:
        st.info("No data yet. Run a campaign first.")
