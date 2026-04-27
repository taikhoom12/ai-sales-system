import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Sales Intelligence", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🚀 AI Sales Intelligence (Stable Mode)")
st.caption("Single-company AI generation (rate-limit safe)")

# =========================
# STATIC COMPANY LIST (SAFE MODE)
# =========================
companies = [
    "Nestlé Pakistan",
    "Engro Foods",
    "GSK Pakistan",
    "Searle Company",
    "Nishat Mills",
    "Gul Ahmed",
    "OGDCL",
    "Pakistan State Oil"
]

# =========================
# UI
# =========================
company = st.selectbox("Select Company", companies)

industry = st.selectbox(
    "Industry",
    ["Pharma", "Food", "Textile", "Oil & Gas", "Chemical"]
)

tone = st.selectbox(
    "Tone",
    ["Professional", "Friendly", "Direct"]
)

# =========================
# SINGLE AI CALL (IMPORTANT FIX)
# =========================
def generate_output(company, industry, tone):

    prompt = f"""
    Company: {company}
    Industry: {industry}

    Do the following:

    1. Identify 2 procurement-related roles
    2. Write 1 short {tone.lower()} outreach message for each role

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
# BUTTON
# =========================
if st.button("🔥 Generate Outreach"):

    with st.spinner("Generating AI response..."):
        output = generate_output(company, industry, tone)

    st.success("Done!")

    st.subheader(f"📊 Results for {company}")

    st.code(output)
