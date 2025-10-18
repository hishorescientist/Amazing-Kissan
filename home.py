import streamlit as st

def app():
    st.set_page_config(page_title="🌾 Agriculture Assistant - Home", layout="wide")

    # --- Global Styles ---
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <style>
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        /* Center title and subtitle */
        h1, h3 {
            text-align: center;
            color: #2E8B57;
        }
        /* Card style boxes */
        .card {
            background-color: #F8FFF8;
            border: 1px solid #D4EED1;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 2px 2px 10px rgba(46, 139, 87, 0.15);
            margin-bottom: 20px;
        }
        /* Subheaders */
        h2, h4 {
            color: #2E8B57;
            font-weight: 600;
        }
        /* Tips styling */
        .tip {
            background-color: #EAF7EA;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        /* Footer */
        .footer {
            text-align: center;
            color: gray;
            font-size: 14px;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.markdown("<h1>🏠 Welcome to Agriculture Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Empowering Farmers with Smart Technology 🌱</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- About Section ---
    st.markdown("""
        <div class="card">
        <h2>About the Platform</h2>
        <p><b>Agriculture Assistant</b> is your all-in-one platform designed to help farmers and agri-enthusiasts 
        manage their activities, learn modern techniques, and connect with essential resources.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Features Section ---
    st.markdown("<h2>🌟 Key Features</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="card">
            <ul>
                <li>📊 <b>Crop Management:</b> Track crop growth and productivity.</li>
                <li>💧 <b>Smart Irrigation Tips:</b> Get region-specific irrigation suggestions.</li>
                <li>☀️ <b>Weather Forecast:</b> Know when to sow, water, or harvest.</li>
                <li>🧑‍🌾 <b>Farmer Profiles:</b> Manage your personal and farm details.</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="card">
            <ul>
                <li>🛒 <b>Market Insights:</b> Stay updated with current crop prices.</li>
                <li>🌿 <b>Soil & Fertilizer Guide:</b> Improve yield with scientific guidance.</li>
                <li>🤝 <b>Community Support:</b> Connect and share with other farmers.</li>
                <li>📱 <b>Accessible Anywhere:</b> Works online on mobile and desktop.</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

    # --- Quick Tips Section ---
    st.markdown("<h2>💡 Quick Agricultural Tips</h2>", unsafe_allow_html=True)
    tips = [
        "Use organic compost to enhance soil fertility naturally.",
        "Avoid overwatering—most crops need consistent, not excessive, moisture.",
        "Rotate crops annually to maintain healthy soil.",
        "Test your soil’s pH level every season for balanced nutrients.",
        "Store seeds in a cool, dry place to maintain viability."
    ]
    for tip in tips:
        st.markdown(f"<div class='tip'>✅ {tip}</div>", unsafe_allow_html=True)

    # --- Footer ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div class="footer">
        🌾 <b>Agriculture Assistant</b> — Built for a sustainable farming future.<br>
        📍 Serving Farmers Across <b>Tamil Nadu & Beyond</b>.
        </div>
    """, unsafe_allow_html=True)


# --- For testing locally ---
if __name__ == "__main__":
    app()