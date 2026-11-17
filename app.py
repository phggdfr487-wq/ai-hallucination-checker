import streamlit as st
import requests
import re
import time
import json

# Page configuration
st.set_page_config(
    page_title="Hallucination Risk Engine | Epistemic Safety Console",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean SaaS / Research Lab CSS
st.markdown("""
<style>
    /* Main canvas background & typography */
    .stApp {
        background-color: #090D16;
        color: #E2E8F0;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1120px;
    }
    
    /* Top Telemetry Navbar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
    }
    .nav-title {
        font-size: 16px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.01em;
    }
    .nav-pills {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .pill {
        background-color: #1E293B;
        color: #94A3B8;
        border: 1px solid #334155;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-family: monospace;
    }
    .pill-live {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Cards & Containers */
    .panel-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.35rem;
        margin-bottom: 1rem;
    }
    .stTextArea textarea {
        background-color: #090D16 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        font-size: 15px !important;
    }
    
    /* Status Badges */
    .badge-high {
        background-color: rgba(239, 68, 68, 0.14);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
    .badge-low {
        background-color: rgba(16, 185, 129, 0.14);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
    .badge-gibberish {
        background-color: rgba(245, 158, 11, 0.14);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation / Telemetry Header
st.markdown("""
<div class="top-nav">
    <div>
        <div class="nav-title">Hallucination Risk Engine</div>
        <div style="font-size: 12px; color: #94A3B8;">Epistemic Grounding & Adversarial Input Firewall</div>
    </div>
    <div class="nav-pills">
        <span class="pill-live">● SYSTEM OPERATIONAL</span>
        <span class="pill">OPENALEX API</span>
        <span class="pill">v2.4.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Core Analysis Engine
def analyze_claim(text):
    start_time = time.time()
    text_clean = text.strip()
    words = text_clean.split()
    
    # GUARD 1: Minimum length or purely numeric
    if len(words) < 4 or text_clean.isdigit():
        latency = round((time.time() - start_time) * 1000, 1)
        return None, "Non-Propositional Input", ["Input is too short (requires at least 4 words) or purely numeric."], None, "general", True, latency

    lower_text = text_clean.lower()
    
    # GUARD 2: Structural & Grammatical Anchor Check
    structural_anchors = [
        "is", "are", "was", "were", "has", "have", "had", "do", "does", "did", 
        "will", "would", "can", "could", "should", "by", "to", "from", "that", 
        "which", "who", "in", "on", "at", "for", "with", "as", "an", "the"
    ]
    anchor_count = sum(1 for word in words if word.lower() in structural_anchors)
    is_structural_gibberish = (anchor_count == 0) or (len(words) < 7 and anchor_count < 2)
    
    # GUARD 3: Middle-Injection & Slang Noise Scanner
    brain_rot_words = [
        "sigma", "rizz", "skibidi", "gyatt", "fanum", "oi", "tralaleo", 
        "ohio", "mewing", "edging", "bop", "blud", "gng", "demure", "cooked"
    ]
    slang_matches = sum(1 for word in words if word.lower().strip(".,!?") in brain_rot_words)
    has_middle_slang = slang_matches > 0
    
    nonsense_triggers = ["eating a house", "milk the website", "drinking the website", "rebuilding the moon with cheese"]
    is_surreal = any(trigger in lower_text for trigger in nonsense_triggers)
    
    dangling_endings = ["of", "the", "a", "an", "in", "on", "by", "with", "to", "from"]
    clean_last = words[-1].lower().strip(".,!?")
    clean_second_last = words[-2].lower().strip(".,!?") if len(words) >= 2 else ""
    ends_with_dangling = clean_last in dangling_endings or (len(words) >= 5 and clean_second_last in dangling_endings and len(clean_last) <= 3)
    
    if is_surreal or is_structural_gibberish or has_middle_slang or ends_with_dangling or len(set(words)) <= 3:
        latency = round((time.time() - start_time) * 1000, 1)
        return 5, "Adversarial / Gibberish Injection", [
            "Blocked by structural firewall: detected missing grammatical glue, dangling prepositions, or embedded slang noise.",
            "Rejected prior to external scholarly database querying."
        ], None, "general", True, latency

    score = 60
    reasons = []
    error_type = "Literature Grounded"
    domain_type = "general"
    
    # 1. Training Data Bias detector
    if any(phrase in lower_text for phrase in ["single-handedly", "100% proven", "always", "never fails", "undisputed", "first ever"]):
        score -= 25
        error_type = "Training Data Bias"
        reasons.append("Contains absolute phrasing frequently learned from oversimplified web forums.")
        
    # 2. Legal citation detector
    if re.search(r"\bv\.\b", text_clean) and any(word in lower_text for word in ["court", "ruling", "case", "precedent", "v.", "judge"]):
        score -= 30
        error_type = "Unverified Legal Citation"
        domain_type = "legal"
        reasons.append("Contains legal case citations—one of the highest-risk categories for fabricated outputs.")

    # 3. Medical / Scientific domain classifier
    if any(word in lower_text for word in ["study", "clinical", "cure", "percent", "%", "researchers", "journal", "cells", "dna"]):
        domain_type = "science"

    # 4. Query OpenAlex Academic Paper API
    search_terms = [w for w in re.findall(r'\b[A-Za-z]{4,}\b', text_clean) if w.lower() not in structural_anchors and w.lower() not in brain_rot_words]
    search_query = " ".join(search_terms[:5])
    
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
    latency = round((time.time() - start_time) * 1000, 1)
    return score, error_type, reasons, paper_match, domain_type, False, latency

def get_verification_steps(domain_type):
    if domain_type == "legal":
        return [
            ("CourtListener (Free Law Project)", "Search the exact case name and docket number to confirm the judicial opinion exists."),
            ("Justia / Cornell LII", "Verify statutory text and real court precedents directly.")
        ]
    elif domain_type == "science":
        return [
            ("PubMed / Google Scholar", "Look up the primary study title and verify sample sizes and peer-review status."),
            ("Consensus.app or Elicit", "Use retrieval-grounded research engines linking directly to peer-reviewed PDFs.")
        ]
    else:
        return [
            ("Google Scholar / OpenAlex", "Cross-check historical or technical claims against published academic works."),
            ("Search-Grounded Verification", "Verify claims using primary databases rather than ungrounded model summaries.")
        ]

# Session state for pre-loading stress tests
if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = "Thomas Edison single-handedly invented the very first light bulb without any prior inventors."

# Multi-Tab Architecture
tab_engine, tab_stress, tab_arch = st.tabs([
    "Live Evaluation Console",
    "Adversarial Stress-Test Suite",
    "System Architecture & Heuristics"
])

# ==========================================
# TAB 1: LIVE EVALUATION CONSOLE
# ==========================================
with tab_engine:
    left_col, right_col = st.columns([1.4, 1], gap="large")

    with left_col:
        st.markdown("#### Claim Input")
        user_prompt = st.text_area(
            "Statement to verify",
            value=st.session_state.prompt_input,
            height=135,
            label_visibility="collapsed"
        )
        
        c1, c2 = st.columns([1, 1.6])
        with c1:
            run_check = st.button("Run Epistemic Check", type="primary", use_container_width=True)
        with c2:
            threshold = st.slider("Policy Confidence Threshold (%)", 10, 90, 50)

    if run_check:
        if not user_prompt.strip():
            with left_col:
                st.warning("Enter a statement above to run an evaluation.")
        else:
            confidence, error_type, reasons, paper_match, domain_type, is_gibberish, latency = analyze_claim(user_prompt)
            
            with left_col:
                st.markdown("---")
                st.markdown("#### Diagnostic Audit")
                
                if is_gibberish:
                    st.markdown('<div class="badge-gibberish">BLOCKED: ADVERSARIAL / NOISE INPUT</div>', unsafe_allow_html=True)
                elif confidence < threshold:
                    st.markdown(f'<div class="badge-high">FLAGGED: BELOW {threshold}% THRESHOLD</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-low">VERIFIED: ABOVE {threshold}% THRESHOLD</div>', unsafe_allow_html=True)
                    
                st.markdown(f"**Classification:** `{error_type}` &nbsp;|&nbsp; **Latency:** `{latency} ms`")
                for r in reasons:
                    st.markdown(f"- {r}")
                    
                if paper_match:
                    st.info(f"**Scholarly Grounding Match:** {paper_match}")

                # JSON Compliance Audit Report Export
                audit_report = {
                    "claim": user_prompt,
                    "grounding_score": confidence,
                    "threshold": threshold,
                    "classification": error_type,
                    "domain": domain_type,
                    "adversarial_blocked": is_gibberish,
                    "latency_ms": latency,
                    "reasons": reasons
                }
                st.download_button(
                    label="Export JSON Audit Log",
                    data=json.dumps(audit_report, indent=2),
                    file_name="epistemic_audit_report.json",
                    mime="application/json"
                )

            with right_col:
                st.markdown("#### Grounding Telemetry")
                display_score = f"{confidence}%" if confidence is not None else "N/A"
                numeric_score = confidence if confidence is not None else 0
                score_color = "#FBBF24" if is_gibberish else ("#EF4444" if confidence < threshold else "#10B981")
                
                st.markdown(f"""
                <div class="panel-card">
                    <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em;">Estimated Grounding Score</div>
                    <div style="font-size: 40px; font-weight: 800; color: {score_color}; margin: 4px 0 4px 0;">{display_score}</div>
                    <div style="font-size: 12px; color: #64748B;">Minimum Required Policy: {threshold}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(numeric_score / 100)
                
                st.markdown("#### Primary Verification Sources")
                for source_name, instruction in get_verification_steps(domain_type):
                    st.markdown(f"""
                    <div class="panel-card" style="padding: 1rem;">
                        <div style="font-weight: 600; color: #F8FAFC; font-size: 14px;">{source_name}</div>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 4px;">{instruction}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        with right_col:
            st.markdown("#### Grounding Telemetry")
            st.markdown("""
            <div class="panel-card">
                <div style="font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em;">Estimated Grounding Score</div>
                <div style="font-size: 40px; font-weight: 800; color: #475569; margin: 4px 0 4px 0;">--%</div>
                <div style="font-size: 12px; color: #64748B;">Awaiting claim execution</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(0.0)

# ==========================================
# TAB 2: ADVERSARIAL STRESS-TEST SUITE
# ==========================================
with tab_stress:
    st.markdown("#### Red-Team Adversarial Benchmark Cases")
    st.caption("Select any edge-case prompt below to load it into the Live Evaluation Console and test how the structural firewall handles it.")
    
    test_cases = [
        ("1. Middle-Sentence Slang Injection", "Cells are sigma made up of tissues and organelles.", "Tests whether embedded brain-rot/slang inside an otherwise valid biology sentence gets intercepted."),
        ("2. Dangling Preposition Hybrid", "Cells are made up of oi e.", "Tests whether starting with real scientific terms and ending in truncated noise gets caught."),
        ("3. Pure Brain-Rot Word Padding", "sigma 67 oi tralaleo", "Tests whether bypassing minimum word counts with zero grammatical connectors fails structural checks."),
        ("4. Fabricated Legal Precedent", "In the landmark 2022 ruling of Mata v. Avianca, the Supreme Court upheld fake citations.", "Tests detection of high-risk legal citation patterns."),
        ("5. Literature-Grounded Scientific Claim", "Mitochondria generate most of the chemical energy needed to power the cell's biochemical reactions.", "Baseline valid claim that should pass structural checks and match OpenAlex records.")
    ]
    
    for title, sample_text, desc in test_cases:
        with st.container():
            col_info, col_act = st.columns([3.5, 1])
            with col_info:
                st.markdown(f"**{title}**")
                st.code(sample_text, language=None)
                st.caption(desc)
            with col_act:
                st.write("")
                st.write("")
                if st.button("Load Prompt", key=title, use_container_width=True):
                    st.session_state.prompt_input = sample_text
                    st.success("Loaded! Switch to 'Live Evaluation Console' and click Run.")
            st.divider()

# ==========================================
# TAB 3: SYSTEM ARCHITECTURE
# ==========================================
with tab_arch:
    st.markdown("#### Multi-Layer Verification Pipeline")
    st.markdown("""
    This engine evaluates unverified text without relying on commercial LLM APIs, eliminating billing dependencies while maintaining sub-second latency.
    
    1. **Layer 1 — Structural & Syntactic Firewall:** Verifies propositional sentence structure by requiring grammatical anchors (verbs, prepositions, logical connectors) and blocking dangling prepositions.
    2. **Layer 2 — Adversarial Noise & Slang Scanner:** Intercepts mid-sentence noise injections and non-propositional word padding before external API calls are triggered.
    3. **Layer 3 — Linguistic Risk Heuristics:** Penalizes overconfident/absolute training-data bias markers (`"single-handedly"`, `"100% proven"`) and flags high-risk legal citation syntax (`v.`).
    4. **Layer 4 — OpenAlex Scholarly Grounding:** Extracts core domain nouns and queries over 250M+ indexed academic records in real time to verify empirical literature presence.
    """)
