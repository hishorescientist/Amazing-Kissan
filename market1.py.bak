import streamlit as st
import pandas as pd
import numpy as np
import time
import json

# ==============================================================================
# 🔐 AUTH & STATE FUNCTIONS (REQUIRED FOR NAVIGATION)
# ==============================================================================

def logout():
    """Clears session state and returns the user to the login screen."""
    # Keep only the essential shared state (like the sheet connection)
    keys_to_delete = [key for key in st.session_state.keys() if key not in ["sheet"]]
    for key in keys_to_delete:
        del st.session_state[key]
    
    st.session_state.logged_in = False
    st.session_state.page = "Login" 
    st.rerun(

# ==============================================================================
# 🤖 GEMINI API SIMULATION (Marketing Content Generation)
# ==============================================================================

def generate_marketing_copy(product_name: str, tone: str) -> dict:
    """
    Simulates calling the Gemini API to generate marketing copy.
    
    NOTE: In a real environment, this function would contain an asynchronous network call 
    to the Gemini API endpoint. We use a placeholder and a delay here.
    
    The payload structure for the actual API call (using gemini-2.5-flash-preview-05-20) 
    would look like this:
    
    const userPrompt = `Write a short, engaging social media post (max 100 words) for our 
                        freshly harvested ${product_name}. The required tone is ${tone}.`;
    const systemPrompt = "You are a creative agricultural marketing specialist. 
                          Your output must be concise and engaging for social media platforms.";
    
    const payload = {
        contents: [{ parts: [{ text: userPrompt }] }],
        systemInstruction: { parts: [{ text: systemPrompt }] },
    };
    
    // ... fetch(apiUrl, { method: 'POST', body: JSON.stringify(payload) }) ...
    """
    
    # --- SIMULATION START ---
    time.sleep(2) # Simulate network delay
    
    # Generate mock response text based on input
    if tone == 'Excited':
        text = f"Harvest Alert! 🎉 Our **{product_name}** are here—picked this morning, bursting with flavor, and 100% locally sourced. Taste the difference that freshness makes! Find us at the farmers market this weekend! #FarmFresh #LocalProduce"
    elif tone == 'Informative':
        text = f"Sustainably Grown **{product_name}**. We focus on soil health and natural methods to bring you the highest quality produce. Learn about our growing practices and commitment to the environment. Available now! #AgriTech #Sustainable"
    else: # Friendly
        text = f"Simple, perfect **{product_name}**. Grown with care on our family farm. We love making good food accessible to our community. Stop by our stand today! #FamilyFarm #Community"

    # Simulate grounding sources
    sources = [
        {"title": "USDA Fresh Produce Standards", "uri": "https://mock.google.com/usda-standards"},
        {"title": "Local Farmers Market Guide", "uri": "https://mock.google.com/market-guide"}
    ]
    
    return {"text": text, "sources": sources}
    # --- SIMULATION END ---


# ==============================================================================
# 🌾 MARKETING APPLICATION UI
# ==============================================================================

def agri_marketing_app():
    """Main function for the agricultural marketing dashboard."""
    
    # Safety Check: Ensure the user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 Access Denied. Please log in to view the marketing dashboard.")
        st.session_state.page = "Login"
        st.rerun()
        return

    user = st.session_state.user
    
    # ------------------ SIDEBAR & LOGOUT ------------------
    with st.sidebar:
        st.subheader("Welcome")
        st.success(f"Logged in as: **{user.get('username', 'Guest')}**")
        st.markdown(f"User: `{user.get('email', 'N/A')}`")
        st.button("Logout", on_click=logout, type="primary", use_container_width=True)
        st.markdown("---")
        st.caption("Marketing Tools")


    # ------------------ MAIN DASHBOARD ------------------
    st.title("🌱 Agricultural Product Marketing Dashboard")
    st.markdown(f"Hello, **{user.get('name', user.get('username', 'Farmer'))}**. Strategize your sales and promotions here.")
    
    st.markdown("---")

    # Use tabs to organize different marketing aspects
    tab1, tab2, tab3 = st.tabs(["✍️ AI Copy Generator", "💰 Pricing Strategy", "📊 Sales Analysis"])

    # --- TAB 1: AI COPY GENERATOR ---
    with tab1:
        st.header("Generate Social Media Content")
        st.markdown("Instantly create engaging social media posts for your products using AI.")

        with st.form("marketing_copy_form"):
            col_prod, col_tone = st.columns(2)
            with col_prod:
                product_name = st.text_input("Product Name", value="Organic Heritage Tomatoes", help="e.g., Gala Apples, Free-Range Eggs")
            with col_tone:
                tone = st.selectbox("Desired Tone", ['Friendly', 'Excited', 'Informative'], index=0)
            
            submitted = st.form_submit_button("Generate Copy", use_container_width=True)

            if submitted:
                if not product_name:
                    st.error("Please enter a product name.")
                else:
                    with st.spinner(f"AI is crafting a {tone} post for {product_name}..."):
                        response = generate_marketing_copy(product_name, tone)
                        
                        st.subheader("Generated Post")
                        # Display the generated content
                        st.markdown(response["text"])

                        st.subheader("Grounded Sources")
                        # Display the mock sources/citations
                        for source in response["sources"]:
                            st.caption(f"🔗 [{source['title']}]({source['uri']})")
                        st.success("Content generation complete!")

    # --- TAB 2: PRICING STRATEGY ---
    with tab2:
        st.header("Wholesale Price Calculator")
        st.markdown("Determine your minimum viable price based on your cost of production and desired margin.")
        
        col_cost, col_yield, col_margin = st.columns(3)
        
        cost_per_acre = col_cost.number_input("Total Production Cost (per acre)", value=1500.0, min_value=0.0, step=100.0, format="%.2f")
        yield_per_acre = col_yield.number_input("Estimated Yield (per unit/acre)", value=500, min_value=1, step=10, help="e.g., 500 lbs of apples, 50 dozen eggs")
        desired_margin = col_margin.slider("Desired Profit Margin (%)", min_value=10, max_value=70, value=35)
        
        if yield_per_acre > 0:
            cost_per_unit = cost_per_acre / yield_per_acre
            min_selling_price = cost_per_unit * (1 + (desired_margin / 100))
            
            st.markdown("---")
            st.metric(label="Cost Per Unit (Breakeven)", value=f"${cost_per_unit:,.2f}")
            st.metric(label="Minimum Target Wholesale Price", value=f"**${min_selling_price:,.2f}**", delta=f"+{desired_margin}% Margin")
        else:
            st.warning("Yield per acre must be greater than zero.")

    # --- TAB 3: SALES ANALYSIS ---
    with tab3:
        st.header("Seasonal Sales Comparison")
        st.markdown("Visualize how this year's sales compare to last year's.")
        
        # Mock Data for visualization
        chart_data = pd.DataFrame(
            {
                "Month": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                "Sales_2024": np.array([20000, 22000, 25000, 35000, 42000, 50000]) * (1 + np.random.randn(6) * 0.05),
                "Sales_2023": np.array([18000, 20000, 23000, 32000, 40000, 48000]) * (1 + np.random.randn(6) * 0.05),
            }
        ).set_index("Month")

        st.line_chart(chart_data)
        
        st.dataframe(chart_data, use_container_width=True)
        st.info("The charts show a healthy sales increase year-over-year. Keep optimizing your marketing!")
