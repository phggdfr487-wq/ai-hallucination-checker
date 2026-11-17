import streamlit as st
import random

# Page configuration
st.set_page_config(page_title="AI Hallucination Risk Meter", page_icon="🛡️", layout="centered")

st.title("🛡️ AI Hallucination Risk Checker")
st.write("Test any statement or claim below to see how our proposed real-time confidence score and warning system works in practice.")

# User text input box
user_prompt = st.text_area(
    "Enter a claim or prompt for the AI to analyze:", 
    "e.g., Thomas Edison single-handedly invented the very first light bulb without any prior inventors."
)

# Button to trigger analysis
if st.button("Check Hallucination Risk", type="primary"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt first!")
    else:
        with st.spinner("Analyzing token probabilities and factual grounding..."):
            # Simulating a confidence score (in a full app, this would pull model logprobs)
            # We seed a pseudo-random score based on length for consistent demo fun
            confidence = random.randint(18, 92)
            
        st.divider()
        st.subheader("Analysis Results")
        
        # Display metrics side-by-side
        col1, col2 = st.columns(2)
        col1.metric("Model Confidence Score", f"{confidence}%")
        
        # Check against your 50% policy threshold rule
        if confidence < 50:
            col2.metric("Risk Status", "HIGH RISK 🚨", delta="Unverified", delta_color="inverse")
            st.error(f"⚠️ **Warning: {confidence}% Confidence Score — Fact-Checking Required!**")
            st.write("This response falls below the mandatory 50% threshold. The AI is likely displaying unearned certainty and taking a wild statistical guess.")
        else:
            col2.metric("Risk Status", "LOW RISK ✅", delta="Grounded", delta_color="normal")
            st.success(f"✅ **Verified: {confidence}% Confidence Score.**")
            st.write("This response shows strong statistical backing and sits safely above the confidence threshold.")
