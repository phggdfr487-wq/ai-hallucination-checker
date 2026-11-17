import streamlit as st
import requests
import re

st.set_page_config(page_title="AI Hallucination Risk Meter", page_icon="🛡️", layout="centered")

st.title("🛡️ AI Hallucination Risk Checker")
st.write("Test any claim below. This engine cross-checks statements against **OpenAlex** (a live database of 250M+ peer-reviewed academic papers) and scans for classic AI hallucination triggers.")

with st.sidebar:
    st.header("About This Project")
    st.write("TKS Focus Replicate #1 — Inspired by *Why ChatGPT Can Sound Right While Being Wrong* by Khalifa Tahlak.")
    st.markdown("""
    **Why OpenAlex instead of Wikipedia?**
    Wikipedia can be edited by anyone. OpenAlex checks real peer-reviewed scientific literature to verify if a concept actually exists in published research.
    """)
    threshold = st.slider("Warning Threshold (%)", min_value=10, max_value=90, value=50)

def analyze_claim(text):
    score = 60  # Baseline confidence
    reasons = []
    error_type = "Grounded in Literature"
    lower_text = text.lower()
    
    # 1. Check for training data bias / absolute language
    if any(phrase in lower_text for phrase in ["single-handedly", "100% proven", "always", "never fails", "undisputed"]):
        score -= 25
        error_type = "Training Data Bias / Oversimplification"
        reasons.append("Uses absolute language often absorbed from oversimplified web forums rather than nuanced research.")
        
    # 2. Check for unverified legal citations (Mata v. Avianca pattern)
    if re.search(r"\bv\.\b", text) and any(word in lower_text for word in ["court", "ruling", "case", "precedent", "v."]):
        score -= 30
        error_type = "High-Risk Legal Citation"
        reasons.append("Contains legal case citations—LLMs frequently invent fake judicial precedents when predicting legal text.")

    # 3. Query OpenAlex Academic Paper API (Free, No Key Required)
    words = [w for w in re.findall(r'\b[A-Za-z]{4,}\b', text) if w.lower() not in ["that", "with", "this", "from", "have", "were", "without", "about"]]
    search_query = " ".join(words[:5])
    
    paper_match = None
    if search_query:
        try:
            url = "https://api.openalex.org/works"
            params = {"search": search_query, "per-page": 1}
            headers = {"User-Agent": "mailto:student-research@example.com"}
            res = requests.get(url, params=params, headers=headers, timeout=6).json()
            
            total_count = res.get("meta", {}).get("count", 0)
            results = res.get("results", [])
            
            if total_count > 0 and results:
                score += 20
                top_paper = results[0]
                title = top_paper.get("title", "Untitled Paper")
                year = top_paper.get("publication_year", "N/A")
                paper_match = f"**Found {total_count:,} academic works.** Top match: *{title}* ({year})"
                reasons.append("Core concepts appear in peer-reviewed academic literature.")
            else:
                score -= 35
                error_type = "Pure Hallucination Risk"
                reasons.append("Zero matching peer-reviewed papers found in OpenAlex—high risk of fabricated concepts or fake citations.")
        except Exception:
            reasons.append("Could not reach OpenAlex academic database.")
            
    score = max(5, min(98, score))
    return score, error_type, reasons, paper_match

user_prompt = st.text_area(
    "Enter a claim or statement to analyze:", 
    "Thomas Edison single-handedly invented the very first light bulb without any prior inventors."
)

if st.button("Check Hallucination Risk", type="primary"):
    if not user_prompt.strip():
        st.warning("Please enter a claim first!")
    else:
        with st.spinner("Querying 250M+ academic papers on OpenAlex..."):
            confidence, error_type, reasons, paper_match = analyze_claim(user_prompt)
            
        st.divider()
        st.subheader("Analysis Results")
        
        col1, col2 = st.columns(2)
        col1.metric("Confidence Score", f"{confidence}%")
        col2.metric("Risk Category", error_type)
        
        if confidence < threshold:
            st.error(f"⚠️ **Warning: {confidence}% Confidence Score — Fact-Checking Required!**")
        else:
            st.success(f"✅ **Passed: {confidence}% Confidence Score (Above {threshold}% threshold).**")
            
        st.markdown("**Why this score?**")
        for r in reasons:
            st.write(f"- {r}")
            
        if paper_match:
            st.info(f"📚 **Academic Literature Check:** {paper_match}")
