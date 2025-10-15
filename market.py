import streamlit as st

def app():
    st.title("🌾 Inside-App Agriculture Store")

    st.info("Browse top products directly here")

    st.image("https://m.media-amazon.com/images/I/61U5Ofm3zRL._AC_UL320_.jpg", width=150)
    st.markdown("**Organic Fertilizer - ₹399**")
    st.markdown("[🛒 Buy Now](https://www.amazon.in/dp/B09ZQ8XZLL)", unsafe_allow_html=True)

    st.image("https://rukminim2.flixcart.com/image/612/612/xif0q/seed/t/z/6/1-kg-vegetable-seeds-combo-pack-of-15-different-vegetables-1-original-imagkfyqytqg3vgp.jpeg?q=70", width=150)
    st.markdown("**Vegetable Seeds Combo - ₹199**")
    st.markdown("[🛒 Buy on Flipkart](https://www.flipkart.com/search?q=vegetable+seeds)", unsafe_allow_html=True)