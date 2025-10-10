import streamlit as st

def app():
    st.set_page_config(page_title="🌾 Agriculture Assistant - Home", layout="wide")
    
    # --- Header ---
    st.title("🏠 Welcome to Agriculture Assistant")
    st.markdown("### Empowering Farmers with Smart Technology 🌱")

    # --- About Section ---
    st.markdown("""
    **Agriculture Assistant** is your all-in-one platform designed to help farmers and agri-enthusiasts 
    manage their activities, learn modern techniques, and connect with essential resources.
    """)

    # --- Features Section ---
    st.subheader("🌟 Key Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - 📊 **Crop Management:** Track crop growth and productivity.  
        - 💧 **Smart Irrigation Tips:** Get region-specific irrigation suggestions.  
        - ☀️ **Weather Forecast:** Know when to sow, water, or harvest.  
        - 🧑‍🌾 **Farmer Profiles:** Manage your personal and farm details.
        """)
    with col2:
        st.markdown("""
        - 🛒 **Market Insights:** Stay updated with current crop prices.  
        - 🌿 **Soil & Fertilizer Guide:** Improve yield with scientific guidance.  
        - 🤝 **Community Support:** Connect and share with other farmers.  
        - 📱 **Accessible Anywhere:** Works online on mobile and desktop.
        """)

    # --- Quick Tips Section ---
    st.subheader("💡 Quick Agricultural Tips")
    tips = [
        "Use organic compost to enhance soil fertility naturally.",
        "Avoid overwatering—most crops need consistent, not excessive, moisture.",
        "Rotate crops annually to maintain healthy soil.",
        "Test your soil’s pH level every season for balanced nutrients.",
        "Store seeds in a cool, dry place to maintain viability."
    ]
    for tip in tips:
        st.markdown(f"✅ {tip}")

    # --- Footer ---
    st.markdown("---")
    st.markdown("""
    🌾 **Agriculture Assistant** — Built for a sustainable farming future.  
    📍 *Serving Farmers Across Tamil Nadu & Beyond.*  
    """)

# --- For testing locally ---
if __name__ == "__main__":
    app()