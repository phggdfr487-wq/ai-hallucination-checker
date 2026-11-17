import streamlit as st
import requests
import re

# Clean, emoji-free page configuration
st.set_page_config(
    page_title="Hallucination Risk Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Subtle custom CSS for a clean, modern research-lab look
st.markdown("""
<style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        max-width: 1050px;
    }
    .stTextArea textarea {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        color: #F9FAFB;
        font-size: 15px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border: none;
    }
    .metric-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .status-badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .status-badge-low {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Clean Header
st.markdown("## Hallucination Risk Engine")
st.caption("Automated epistemic grounding and statistical uncertainty analyzer powered by OpenAlex scholarly indexing.")
st.divider()

def analyze_claim(text):
    score = 60
    reasons = []
    error_type = "Literature Grounded"
    domain_type = "general"
    lower_text = text.lower()
    
    # 1. Absolute language / Training Data Bias detector
    if any(phrase in lower_text for phrase in ["single-handedly", "100% proven", "always", "never fails", "undisputed", "first ever"]):
        score -= 25
        error_type = "Training Data Bias"
        reasons.append("Contains absolute phrasing ('single-handedly', 'first ever') frequently learned from oversimplified web forums.")
        
    # 2. Legal citation detector (Mata v. Avianca pattern)
    if re.search(r"\bv\.\b", text) and any(word in lower_text for word in ["court", "ruling", "case", "precedent", "v.", "judge"]):
        score -= 30
        error_type = "Unverified Legal Citation"
        domain_type = "legal"
        reasons.append("Contains legal case citations—one of the highest-risk categories for fabricated model outputs.")

    # 3. Medical / Scientific claim detector
    if any(word in lower_text for word in ["study", "clinical", "cure", "percent", "%", "researchers", "journal"]):
        domain_type = "science"

    # 4. Query OpenAlex Academic Paper API
    words = [w for w in re.findall(r'\b[A-Za-z]{4,}\b', text) if w.lower() not in ["that", "with", "this", "from", "have", "were", "without", "about", "there", "their"]]
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
                paper_match = f"Matched {total_count:,} scholarly records. Top reference: \"{title}\" ({year})."
                reasons.append("Core terminology appears in indexed peer-reviewed academic literature.")
            else:
                score -= 35
                error_type = "High Hallucination Risk"
                reasons.append("Zero matching peer-reviewed papers found in OpenAlex—high probability of fabricated concepts.")
        except Exception:
            reasons.append("External academic database timeout; score reflects linguistic risk signals only.")
            
    score = max(5, min(98, score))
    return score, error_type, reasons, paper_match, domain_type

def get_verification_steps(domain_type, score):
    if domain_type == "legal":
        return [
            ("CourtListener (Free Law Project)", "Search the exact case name and docket number to confirm the judicial opinion actually exists."),
            ("Justia or Cornell LII", "Verify statutory text and real court precedents rather than relying on LLM summaries.")
        ]
    elif domain_type == "science":
        return [
            ("PubMed / Google Scholar", "Look up the primary study title and verify sample sizes and peer-review status."),
            ("Consensus.app or Elicit", "Use retrieval-grounded research engines that link directly to PDF citations.")
        ]
    else:
        return [
            ("Google Scholar / OpenAlex", "Cross-check historical or technical claims against published academic works."),
            ("Perplexity AI (with Citations)", "Run the prompt through a search-grounded engine and click the numbered source links directly.")
        ]

# Main two-column layout: Left = Input & Analysis, Right = Visual Confidence Bar & Next Steps
left_col, right_col = st.columns([1.35, 1], gap="large")

with left_col:
    st.markdown("#### Input Statement")
    user_prompt = st.text_area(
        "Claim or AI output to evaluate",
        value="Thomas Edison single-handedly invented the very first light bulb without any prior inventors.",
        height=130,
        label_visibility="collapsed"
    )
    
    col_btn, col_thresh = st.columns([1, 1.5])
    with col_btn:
        run_check = st.button("Run Analysis", type="primary", use_container_width=True)
    with col_thresh:
        threshold = st.slider("Mandatory Warning Threshold (%)", 10, 90, 50)

if run_check:
    if not user_prompt.strip():
        with left_col:
            st.warning("Enter a statement above to run an epistemic check.")
    else:
        confidence, error_type, reasons, paper_match, domain_type = analyze_claim(user_prompt)
        is_flagged = confidence < threshold
        
        with left_col:
            st.markdown("---")
            st.markdown("#### Diagnostic Breakdown")
            
            if is_flagged:
                st.markdown(f'<div class="status-badge-high">FLAGGED: BELOW {threshold}% THRESHOLD</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-badge-low">PASSED: ABOVE {threshold}% THRESHOLD</div>', unsafe_allow_html=True)
                
            st.markdown(f"**Classification:** `{error_type}`")
            for r in reasons:
                st.markdown(f"- {r}")
                
            if paper_match:
                st.caption(f"Database Log: {paper_match}")

        with right_col:
            st.markdown("#### Confidence & Verification")
            
            # Visual Confidence Bar Card
            bar_color = "#EF4444" if is_flagged else "#10B981"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 13px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em;">Estimated Grounding Score</div>
                <div style="font-size: 36px; font-weight: 700; color: {bar_color}; margin: 4px 0 12px 0;">{confidence}%</div>
                <div style="width: 100%; background-color: #1F2937; border-radius: 6px; height: 12px; overflow: hidden;">
                    <div style="width: {confidence}%; background-color: {bar_color}; height: 100%; border-radius: 6px;"></div>
                </div>
                <div style="font-size: 12px; color: #9CA3AF; margin-top: 8px;">Policy Threshold: {threshold}% minimum required</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recommended Next Steps / Reliable Reasoners
            st.markdown("#### Recommended Verification Sources")
            steps = get_verification_steps(domain_type, confidence)
            for source_name, instruction in steps:
                st.markdown(f"""
                <div class="metric-card" style="padding: 1rem;">
                    <div style="font-weight: 600; color: #F3F4F6; font-size: 14px;">{source_name}</div>
                    <div style="color: #9CA3AF; font-size: 13px; margin-top: 4px;">{instruction}</div>
                </div>
                """, unsafe_allow_html=True)
else:
    with right_col:
        st.markdown("#### Confidence & Verification")
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 13px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em;">Estimated Grounding Score</div>
            <div style="font-size: 36px; font-weight: 700; color: #4B5563; margin: 4px 0 12px 0;">--%</div>
            <div style="width: 100%; background-color: #1F2937; border-radius: 6px; height: 12px;"></div>
            <div style="font-size: 12px; color: #6B7280; margin-top: 8px;">Run an analysis to calculate epistemic confidence</div>
        </div>
        """, unsafe_allow_html=True)
