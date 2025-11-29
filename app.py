import streamlit as st
import requests
import pandas as pd
import base64
import plotly.graph_objects as go

# -------------------------
# Configuration
# -------------------------
st.set_page_config(page_title="GPC Code Validator", layout="centered")

# -------------------------
# Add Centered Egyptian Tax Authority Logo
# -------------------------
image_path = "logos/logo-removebg-preview.png"
with open(image_path, "rb") as f:
    img_bytes = f.read()
encoded = base64.b64encode(img_bytes).decode()

st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{encoded}" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Centered Title
# -------------------------
st.markdown(
    "<h1 style='text-align: center;'>🛠️ GPC Code Validation System</h1>",
    unsafe_allow_html=True
)

# Define threshold for classification
THRESHOLD = 85

# -------------------------
# User Inputs
# -------------------------
st.subheader("Enter Product Details")
product_title = st.text_input("Product Title:")
gpc_code = st.text_input("GPC Code:")

# -------------------------
# Button to trigger validation
# -------------------------
if st.button("Validate"):

    if not product_title or not gpc_code:
        st.warning("Please provide both Product Title and GPC Code.")
        st.stop()

    payload = {
        "product_title": product_title,
        "gpc_code": gpc_code
    }

    # Replace with your actual Make.com webhook URL
    webhook_url = "https://hook.eu1.make.com/tkz9t362xcz1y44efmdo6og4c7377tc7"

    # -------------------------
    # Send request to Make.com
    # -------------------------
    with st.spinner("Processing..."):
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            st.error(f"Error contacting Make API: {e}")
            st.stop()

    # -------------------------
    # Extract values
    # -------------------------
    final_score = result.get("final_score", 0)
    title_score = result.get("title_score", 0)
    includes_score = result.get("includes_score", 0)
    excludes_score = result.get("excludes_score", 0)
    generated_description = result.get("Product title Generated", "N/A")
    gpc_title = result.get("Product Title", "N/A")
    definition_includes = result.get("Definition Includes", "N/A")
    definition_excludes = result.get("Definition Excludes", "N/A")

    # -------------------------
    # Compute classification
    # -------------------------
    if final_score >= THRESHOLD:
        classification = "Valid Code"
        badge_color = "green"
    else:
        classification = "Wrong Code"
        badge_color = "red"

    # -------------------------
    # Horizontal side-by-side comparison
    # -------------------------
    st.subheader("🔹 Product Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div style='text-align:center'><b>Seller Input</b></div>", unsafe_allow_html=True)
        st.write(f"**Title:** {product_title}")
        st.markdown("**Generated Description (from Gemini):**")
        st.write(generated_description)

    with col2:
        st.markdown("<div style='text-align:center'><b>GPC Code Product</b></div>", unsafe_allow_html=True)
        st.write(f"**Title:** {gpc_title}")
        st.write(f"**Includes:** {definition_includes}")
        st.write(f"**Excludes:** {definition_excludes}")

    # -------------------------
    # Display Plotly Gauge Charts for each score
    # -------------------------
    st.markdown("---")

    st.markdown(
        f"<h2 style='text-align:center;'>📊 Similarity Scores Breakdown</h2>",
        unsafe_allow_html=True,
    )


    def display_gauge(score, label, color="blue"):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': label, 'font': {'size': 20}},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': color},
                   'steps': [
                       {'range': [0, 50], 'color': '#f2f2f2'},
                       {'range': [50, 100], 'color': '#d9d9d9'}
                   ]}
        ))
        fig.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<h3 style='text-align:center;'>Title Similarity</h3>",
        unsafe_allow_html=True,
    )
    display_gauge(title_score, "Title Similarity", "blue")
    st.markdown("---")
    st.markdown(
        f"<h3 style='text-align:center;'>Includes Similarity</h3>",
        unsafe_allow_html=True,
    )
    display_gauge(includes_score, "Includes Similarity", "green")
    st.markdown("---")
    st.markdown(
        f"<h3 style='text-align:center;'>Excludes Similarity</h3>",
        unsafe_allow_html=True,
    )
    display_gauge(excludes_score, "Excludes Similarity", "red")
    

    st.markdown("---")

    # -------------------------
    # Display Final Score and Classification in center
    # -------------------------
    st.markdown(
        f"<h1 style='text-align:center'>Final Score: {final_score}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h2 style='text-align:center; color:{badge_color}'>{classification}</h2>",
        unsafe_allow_html=True,
    )