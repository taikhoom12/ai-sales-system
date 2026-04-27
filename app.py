import streamlit as st
import openai
import pandas as pd
import time

# =========================
# CONFIG
# =========================
openai.api_key = "YOUR_OPENAI_API_KEY"

st.set_page_config(page_title="AI Sales System", layout="wide")

st.title("🚀 AI B2B Sales Generator")

# =========================
# INPUTS
# =========================
industry = st.selectbox(
    "Select Industry",
    ["Pharma", "Food", "Textile", "Oil & Gas", "Chemical", "Cement"]
)

num_companies = st.slider("Number of Companies", 5, 30, 10)

# =========================
# AI FUNCTIONS
# =========================

def generate_companies(industry, n):
    prompt = f"""
    List {n} real companies in Pakistan in the {industry} industry.
    Only return names in a clean list.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response['choices'][0]['message']['content']
    companies = [line.strip("- ").strip() for line in text.split("\n") if line.strip()]
    
    return companies


def generate_roles(company):
    prompt = f"""
    List 3 job roles responsible for procurement in {company}.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response['choices'][0]['message']['content']
    roles = [r.strip("- ").strip() for r in text.split("\n") if r.strip()]
    
    return roles


def generate_message(name, company, industry, role):
    prompt = f"""
    Write a short professional cold outreach message.

    Person: {name}
    Role: {role}
    Company: {company}
    Industry: {industry}

    Context:
    We supply stainless steel pipes, fittings, valves.

    Keep it concise, natural, not spammy.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']


# =========================
# GENERATE BUTTON
# =========================
if st.button("🔥 Generate Leads"):

    st.write("Generating companies...")
    companies = generate_companies(industry, num_companies)

    data = []

    progress = st.progress(0)

    for i, company in enumerate(companies):
        st.write(f"Processing: {company}")

        roles = generate_roles(company)

        for role in roles:
            name = "Procurement Manager"

            message = generate_message(name, company, industry, role)

            data.append({
                "Company": company,
                "Role": role,
                "Contact": name,
                "Email": f"info@{company.replace(' ', '').lower()}.com",
                "Message": message
            })

            time.sleep(1)

        progress.progress((i + 1) / len(companies))

    df = pd.DataFrame(data)

    st.success("✅ Done!")

    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download CSV",
        csv,
        "leads.csv",
        "text/csv"
    )