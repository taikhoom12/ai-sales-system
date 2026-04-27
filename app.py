import streamlit as st
import pandas as pd
import time
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Sales System", layout="wide")

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =========================
# HEADER
# =========================
st.title("🚀 AI B2B Sales Generator")
st.caption("Generate companies, roles & outreach messages instantly")

# =========================
# SIDEBAR (Controls)
# =========================
st.sidebar.header("⚙️ Controls")

industry = st.sidebar.selectbox(
    "Select Industry",
    ["Pharma", "Food", "Textile", "Oil & Gas", "Chemical", "Cement"]
)

num_companies = st.sidebar.slider("Number of Companies", 5, 25, 10)

tone = st.sidebar.selectbox(
    "Message Tone",
    ["Professional", "Friendly", "Direct"]
)

# =========================
# AI FUNCTIONS
# =========================

def generate_companies(industry, n):
    prompt = f"""
    List {n} real companies in Pakistan in the {industry} industry.
    Only return names in a clean bullet list.
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    return [line.strip("- ").strip() for line in text.split("\n") if line.strip()]


def generate_roles(company):
    prompt = f"""
    List 3 job roles responsible for procurement in {company}.
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    return [r.strip("- ").strip() for r in text.split("\n") if r.strip()]


def generate_message(name, company, industry, role, tone):
    prompt = f"""
    Write a {tone.lower()} cold outreach message.

    Person: {name}
    Role: {role}
    Company: {company}
    Industry: {industry}

    Context:
    We supply stainless steel pipes, fittings, valves.

    Keep it short, human, and not spammy.
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# =========================
# GENERATE BUTTON
# =========================
if st.button("🔥 Generate Leads"):

    with st.spinner("Generating companies..."):
        companies = generate_companies(industry, num_companies)

    data = []
    progress_bar = st.progress(0)

    for i, company in enumerate(companies):

        st.write(f"🔍 Processing: {company}")

        roles = generate_roles(company)

        for role in roles:
            name = "Procurement Manager"

            message = generate_message(name, company, industry, role, tone)

            data.append({
                "Company": company,
                "Role": role,
                "Contact": name,
                "Email": f"info@{company.replace(' ', '').lower()}.com",
                "Message": message
            })

            time.sleep(0.5)

        progress_bar.progress((i + 1) / len(companies))

    df = pd.DataFrame(data)

    st.success("✅ Leads Generated!")

    # =========================
    # FILTER + SEARCH
    # =========================
    search = st.text_input("🔍 Search Company")

    if search:
        df = df[df["Company"].str.contains(search, case=False)]

    # =========================
    # TABLE VIEW
    # =========================
    st.dataframe(df, use_container_width=True)

    # =========================
    # EXPANDABLE MESSAGE VIEW
    # =========================
    st.subheader("📩 Messages")

    for i, row in df.iterrows():
        with st.expander(f"{row['Company']} — {row['Role']}"):
            st.write(row["Message"])

            st.code(row["Message"])

            st.button(
                f"📋 Copy Message {i}",
                on_click=lambda msg=row["Message"]: st.write("Copied!")
            )

    # =========================
    # DOWNLOAD
    # =========================
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇️ Download CSV",
        csv,
        "leads.csv",
        "text/csv"
    )
