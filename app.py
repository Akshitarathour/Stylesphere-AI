import streamlit as st
import os
import sqlite3
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

import database
from agents.closet_agent import ClosetAgent
from agents.image_agent import ImageAgent
from agents.style_agent import StyleAgent
from agents.weather_agent import WeatherAgent
from agents.sustainability_agent import SustainabilityAgent
from agents.packing_agent import PackingAgent
from agents.preference_agent import PersonalPreferenceAgent
from agents.shopping_agent import ShoppingAgent
from agents.trend_agent import FashionTrendAgent
from agents.occasion_agent import OccasionAgent

# Set page config
st.set_page_config(
    page_title="StyleSphere AI - Premium Smart Wardrobe",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
database.init_db()

# Create upload directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Initialize Agents
@st.cache_resource
def get_agents():
    return {
        "closet": ClosetAgent(),
        "image": ImageAgent(),
        "style": StyleAgent(),
        "weather": WeatherAgent(),
        "sustainability": SustainabilityAgent(),
        "packing": PackingAgent(),
        "preference": PersonalPreferenceAgent(),
        "shopping": ShoppingAgent(),
        "trend": FashionTrendAgent(),
        "occasion": OccasionAgent()
    }

agents = get_agents()

# Global styling
st.markdown("""
<style>
    /* Premium font and styling */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main body background styling */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Elegant Dark Mode Style Card with glassmorphism */
    .clothing-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .clothing-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    /* Gradient headers */
    .gradient-text {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* Hero section styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(192, 132, 252, 0.05) 100%);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin-bottom: 35px;
        position: relative;
        overflow: hidden;
    }
    
    /* Suitcase layout style cards */
    .suitcase-card {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(251, 191, 36, 0.25);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    .suitcase-card:hover {
        border-color: rgba(251, 191, 36, 0.6);
        box-shadow: 0 10px 25px rgba(251, 191, 36, 0.15);
    }

    /* Eco friendly utility styling */
    .eco-score-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-radius: 24px;
        padding: 30px;
        border: 1px solid rgba(16, 185, 129, 0.25);
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    /* Premium buttons override */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    }
    
    /* Sidebar styling overrides */
    div[data-testid="stSidebar"] div.element-container {
        margin-bottom: 8px;
    }
    div[data-testid="stSidebar"] select {
        font-size: 15px !important;
        padding: 8px !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar setup
st.sidebar.markdown("<h1 class='gradient-text' style='text-align: center; font-size: 32px; margin-bottom: 5px;'>StyleSphere AI</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 25px;'>Intelligent Wardrobe & Styling Assistant</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# API Key handling via collapsible settings
from dotenv import dotenv_values
env_vars = dotenv_values(".env")

# Pre-load keys from env or .env file (stripping quotes)
env_groq_key = (os.environ.get("GROQ_API_KEY") or env_vars.get("GROQ_API_KEY", "")).strip().strip('"\'')
env_gemini_key = (os.environ.get("GEMINI_API_KEY") or env_vars.get("GEMINI_API_KEY", "")).strip().strip('"\'')

if env_groq_key and not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = env_groq_key
if env_gemini_key and not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = env_gemini_key

# Draw a single unified settings expander
with st.sidebar.expander("⚙️ Connection Settings", expanded=True):
    groq_input = st.text_input(
        "Groq API Key", 
        type="password", 
        value= " "
    )
    gemini_input = st.text_input(
        "Gemini API Key", 
        type="password", 
        value = " "
    )

    if groq_input:
        os.environ["GROQ_API_KEY"] = groq_input.strip()
    if gemini_input:
        os.environ["GEMINI_API_KEY"] = gemini_input.strip()

# Resolve final keys
api_key = os.environ.get("GROQ_API_KEY", "").strip()
gemini_key_val = os.environ.get("GEMINI_API_KEY", "").strip()
user_key = api_key

# Check if API key is missing
if not api_key:
    st.sidebar.warning("⚠️ **Groq API Key Missing:** Please set the `GROQ_API_KEY` in a `.env` file or enter it in settings.")

# Page navigation with icons
menu_options = [
    "🏠 Home Dashboard",
    "👚 Digital Wardrobe",
    "📤 Upload Clothing",
    "💡 Outfit Recommendation",
    "📅 Today's Outfit",
    "📊 Wardrobe Analytics",
    "🌿 Sustainability Matrix",
    "✈️ Travel Packing",
    "🛍️ Shopping Advisor",
    "⚙️ Preferences & Settings"
]
page_choice = st.sidebar.selectbox("Navigate Page", menu_options)

# Map page choice back to standard choices for compatibility
page_choice_map = {
    "🏠 Home Dashboard": "🏠 Home",
    "👚 Digital Wardrobe": "👚 Wardrobe",
    "📤 Upload Clothing": "📤 Upload Clothing",
    "💡 Outfit Recommendation": "💡 Outfit Recommendation",
    "📅 Today's Outfit": "📅 Today's Outfit",
    "📊 Wardrobe Analytics": "📊 Wardrobe Analytics",
    "🌿 Sustainability Matrix": "🌿 Sustainability",
    "✈️ Travel Packing": "✈️ Travel Packing",
    "🛍️ Shopping Advisor": "🛍️ Shopping Advisor",
    "⚙️ Preferences & Settings": "⚙️ Settings"
}
page_choice = page_choice_map.get(page_choice, "🏠 Home")

# Helper function to render clothing item details
def display_clothing_grid(items, is_wishlist=False, on_delete=None):
    if not items:
        st.info("No clothing items found in this section.")
        return
        
    cols = st.columns(4)
    for idx, item in enumerate(items):
        with cols[idx % 4]:
            # Show image if path exists
            img_path = item.get('image_path')
            has_img = False
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    st.image(img, use_container_width="stretch")
                    has_img = True
                except Exception:
                    pass
            
            # Info Card
            st.markdown(f"""
            <div class="clothing-card" style="margin-top: {-12 if has_img else 0}px; border-top-left-radius: {0 if has_img else 20}px; border-top-right-radius: {0 if has_img else 20}px;">
                <p style="font-weight: 700; font-size: 14px; margin-bottom: 6px; color: #f8fafc; line-height: 1.3;">{item.get('notes') or 'Clothing Item'}</p>
                <div style="display: flex; flex-direction: column; gap: 4px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; margin-top: 6px;">
                    <span style="font-size: 12px; color: #94a3b8;">🏷️ <b>Category:</b> {item.get('category').title()}</span>
                    <span style="font-size: 12px; color: #94a3b8;">🎨 <b>Colors:</b> {item.get('colors')}</span>
                    <span style="font-size: 12px; color: #94a3b8;">🧵 <b>Fabric:</b> {item.get('fabric') or 'Unknown'}</span>
                    <span style="font-size: 12px; color: #e2e8f0; font-weight: 600; margin-top: 4px;">💰 Price: ${item.get('price'):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metadata detail view expander
            with st.expander("Details & Actions"):
                st.write(f"**Pattern:** {item.get('pattern') or 'Solid'}")
                st.write(f"**Sleeve:** {item.get('sleeve_type') or 'N/A'}")
                st.write(f"**Seasons:** {item.get('season_suitability') or 'All-season'}")
                if not is_wishlist:
                    st.write(f"**Wears:** {item.get('wear_count', 0)}")
                    st.write(f"**Last Worn:** {item.get('last_worn_date') or 'Never'}")
                if item.get('tags'):
                    st.write(f"**Tags:** {item.get('tags')}")
                
                # Delete option
                if on_delete:
                    if st.button("Delete Item", key=f"del_{item['id']}"):
                        on_delete(item['id'])
                        st.rerun()

# ----------------- 1. HOME PAGE -----------------
if page_choice == "🏠 Home":
    # Premium Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 style="font-size: 38px; font-weight: 800; margin-bottom: 12px; color: #ffffff; line-height: 1.2;">
            Elevate Your Style with <span class="gradient-text">Cognitive Fashion AI</span>
        </h1>
        <p style="font-size: 15px; color: #cbd5e1; max-width: 700px; line-height: 1.6; margin-bottom: 0;">
            Welcome to <b>StyleSphere AI</b>. Harness the power of coordinate vision intelligence and cooperative 
            multi-agent workflows to organize your digital wardrobe, audit cost-per-wear sustainability metrics, 
            and synthesize tailored daily recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Core Capabilities Features Cards
    st.markdown("### ⚡ Core Capabilities")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        # 1. Pehle alag se CSS style inject karein (Aapki sidebar wali styling ke liye)
        st.markdown(
            """
            <style>
            /* Sidebar background */
            section[data-testid="stSidebar"] {
                background-color: #0E1117 !important;
            }
            /* Sidebar text */
            section[data-testid="stSidebar"] * {
                color: white !important;
            }
            /* Sidebar buttons and radio labels */
            section[data-testid="stSidebar"] .stButton > button, 
            section[data-testid="stSidebar"] label, 
            section[data-testid="stSidebar"] p, 
            section[data-testid="stSidebar"] span, 
            section[data-testid="stSidebar"] div {
                color: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 2. Ab card ka HTML design alag se likhein
        st.markdown(
            """
            <div class="clothing-card" style="min-height: 170px;">
                <h4 style="color: #818CF8; margin-bottom: 8px; font-size: 15px;">
                    📷 Vision Auto-Tagging
                </h4>
                <p style="color: #A0AEC0; font-size: 13px;">
                    Upload pictures of your clothes to automatically tag and organize your wardrobe.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
       
    with f_col2:
        st.markdown(
            """
            <div class="clothing-card" style="min-height: 170px;">
                <h4 style="color: #c084fc; margin-bottom: 8px; font-size: 15px;">🌦️ Weather-Aware Styling</h4>
                <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 0;">
                    Incorporate real-time atmospheric guidelines and layering suggestions to construct styling recommendations.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with f_col3:
        st.markdown(
            """
            <div class="clothing-card" style="min-height: 170px;">
                <h4 style="color: #f472b6; margin-bottom: 8px; font-size: 15px;">🌿 Circular Eco-Audit</h4>
                <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 0;">
                    Quantify wardrobe gaps, analyze double-purchase overlap risks, and audit your sustainability performance scores.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

            
    # Check wardrobe count
    items = database.get_all_clothing_items()
    total_items = len(items)
    
    # Home Metrics
    st.markdown("### 📊 Wardrobe Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="clothing-card" style="text-align: center; padding: 20px; border-left: 4px solid #818cf8;">
            <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">👗 Total Garments</p>
            <h2 style="font-size: 30px; font-weight: 700; color: #ffffff; margin: 0;">{total_items}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        wishlist_items = database.get_wishlist_items()
        st.markdown(f"""
        <div class="clothing-card" style="text-align: center; padding: 20px; border-left: 4px solid #c084fc;">
            <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">🛍️ Wishlist Registry</p>
            <h2 style="font-size: 30px; font-weight: 700; color: #ffffff; margin: 0;">{len(wishlist_items)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if total_items > 0:
            worn_count = len([it for it in items if it["wear_count"] > 0])
            utilization_val = f"{(worn_count/total_items)*100:.1f}%"
        else:
            utilization_val = "0%"
        st.markdown(f"""
        <div class="clothing-card" style="text-align: center; padding: 20px; border-left: 4px solid #f472b6;">
            <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">📈 Wardrobe Utilization</p>
            <h2 style="font-size: 30px; font-weight: 700; color: #ffffff; margin: 0;">{utilization_val}</h2>
        </div>
        """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Weather Integration Section
    st.markdown("### 🌦️ Dynamic Weather Styling")
    w_col1, w_col2 = st.columns([1, 2])
    with w_col1:
        st.markdown("##### 📍 Location Weather Simulation")
        temp = st.slider("Temperature (°C)", -10, 45, 20, key="home_temp_slider")
        condition = st.selectbox("Weather Condition", ["Clear/Sunny", "Cloudy", "Rainy", "Snowy", "Windy"], key="home_cond_select")
        
    with w_col2:
        st.markdown("##### 💡 AI Stylist Advisory")
        weather_icons = {
            "Clear/Sunny": "☀️",
            "Cloudy": "☁️",
            "Rainy": "🌧️",
            "Snowy": "❄️",
            "Windy": "💨"
        }
        w_icon = weather_icons.get(condition, "🌡️")
        advice = agents["weather"].generate_weather_advice(temp, condition, api_key=api_key)
        st.markdown(f"""
        <div class="clothing-card" style="border: 1px solid rgba(99, 102, 241, 0.15); background: rgba(99, 102, 241, 0.03); padding: 18px; margin-top: 10px;">
            <p style="font-size: 15px; font-weight: 700; color: #818cf8; margin-bottom: 8px;">
                {w_icon} Recommended Dressing Rule ({temp}°C, {condition})
            </p>
            <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6; margin: 0;">{advice}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Timeless Fashion Tip of the Day
    st.markdown("### 💡 Styling Tip of the Day")
    tips = agents["trend"].get_timeless_tips()
    tip = tips[datetime.now().day % len(tips)]
    st.markdown(f"""
    <div class="clothing-card" style="border-color: rgba(251, 191, 36, 0.25); background: rgba(251, 191, 36, 0.03); padding: 24px;">
        <h4 style="color: #fbbf24; font-weight: 700; margin-bottom: 8px;">✨ {tip['formula']}</h4>
        <p style="font-size: 14px; color: #e2e8f0; line-height: 1.6; margin: 0;">{tip['explanation']}</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- 2. WARDROBE -----------------
elif page_choice == "👚 Wardrobe":
    st.markdown("<h1 class='gradient-text'>Digital Wardrobe Inventory</h1>", unsafe_allow_html=True)
    st.write("Browse and filter through your catalog of items.")
    
    # Horizontal Filter Layout
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        categories = ["All", "Top", "Bottom", "Shoes", "Outer", "Dress", "Accessory"]
        selected_cat = st.selectbox("Filter by Category", categories, key="wardrobe_category_select")
    with f_col2:
        search_query = st.text_input("🔍 Search items by tags or notes...", key="wardrobe_search_input")
    
    filter_cat = None if selected_cat == "All" else selected_cat.lower()
    items = agents["closet"].get_inventory(category=filter_cat)
    
    if search_query:
        items = [it for it in items if search_query.lower() in (it.get("notes") or "").lower() or search_query.lower() in (it.get("tags") or "").lower()]
    
    def handle_delete(item_id):
        # Fetch item details first to remove file
        it = agents["closet"].get_item(item_id)
        if it and it.get("image_path") and os.path.exists(it["image_path"]):
            try:
                os.remove(it["image_path"])
            except Exception:
                pass
        agents["closet"].delete_item(item_id)
        st.success("Item deleted successfully!")
        
    display_clothing_grid(items, on_delete=handle_delete)

# ----------------- 3. UPLOAD CLOTHING -----------------
elif page_choice == "📤 Upload Clothing":
    st.markdown("<h1 class='gradient-text'>Upload Clothing Item</h1>", unsafe_allow_html=True)
    st.write("Incorporate new pieces into your wardrobe registry. The AI vision recognition parser will analyze the item and suggest tag categories automatically.")
    
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.35); border: 2px dashed rgba(99, 102, 241, 0.4); border-radius: 16px; padding: 30px; text-align: center; margin-bottom: 25px;">
        <span style="font-size: 38px;">📤</span>
        <h4 style="margin-top: 10px; color: #818cf8; font-weight: 700;">Drag and Drop Image File</h4>
        <p style="font-size: 12px; color: #94a3b8;">Supports JPG, JPEG, and PNG files up to 10MB</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a clothing photo...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        st.markdown("### Garment Preview")
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Preview of uploaded file", width=320)
        
        # Save file to uploads folder temporarily or permanently
        file_ext = uploaded_file.name.split(".")[-1]
        filename = f"clothing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        saved_path = os.path.join(UPLOAD_DIR, filename)
        
        # Analyze button
        if st.button("🚀 Run AI Recognition Pipeline"):
            # Get bytes
            uploaded_file.seek(0)
            img_bytes = uploaded_file.read()
            
            # Progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Connecting to AI recognition pipeline...")
            progress_bar.progress(20)
            
            import time
            time.sleep(0.3)
            status_text.text("Parsing visual features and patterns...")
            progress_bar.progress(50)
            
            metadata = agents["image"].analyze_clothing_image(
                image_bytes=img_bytes,
                mime_type=f"image/{file_ext if file_ext != 'jpg' else 'jpeg'}",
                api_key=gemini_key_val
            )
            
            progress_bar.progress(85)
            status_text.text("Cataloging metadata tags...")
            time.sleep(0.2)
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            time.sleep(0.1)
            
            # Clear progress trackers
            progress_bar.empty()
            status_text.empty()
            
            st.session_state["detected_metadata"] = metadata
            st.session_state["uploaded_file_bytes"] = img_bytes
            st.session_state["saved_path"] = saved_path
            
            # Save the file permanently
            image.save(saved_path)
            st.success("🎉 AI analysis complete! Review detected metadata below.")
            
    if "detected_metadata" in st.session_state:
        meta = st.session_state["detected_metadata"]
        st.markdown("### 📋 Edit Detected Metadata")
        
        # Prefill form with metadata
        cat_options = ["top", "bottom", "shoes", "outer", "dress", "accessory"]
        cat_index = cat_options.index(meta.get("category", "top")) if meta.get("category", "top") in cat_options else 0
        
        # Columns for form styling
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            category = st.selectbox("Category", cat_options, index=cat_index)
            colors = st.text_input("Colors (comma separated)", meta.get("colors", ""))
            pattern = st.selectbox("Pattern", ["solid", "striped", "plaid", "floral", "graphic", "dotted", "animal print", "camouflage", "other"])
            sleeve_type = st.selectbox("Sleeve Type", ["short", "long", "sleeveless", "none", "other"])
        with c_col2:
            season_suitability = st.text_input("Season Suitability", meta.get("season_suitability", "all-season"))
            fabric = st.text_input("Fabric", meta.get("fabric", "cotton"))
            brand = st.text_input("Brand", "")
            price = st.number_input("Purchase Price ($)", min_value=0.0, value=0.0, step=5.0)
            
        tags = st.text_input("Style Tags (comma separated)", ", ".join(meta.get("tags", [])))
        notes = st.text_area("Stylist Notes / Description", meta.get("notes", ""))
        
        if st.button("Save to Digital Wardrobe"):
            # Add clothing item to SQLite via closet agent
            item_id = agents["closet"].add_item(
                category=category,
                colors=colors,
                pattern=pattern,
                sleeve_type=sleeve_type,
                season_suitability=season_suitability,
                fabric=fabric,
                brand=brand,
                price=price,
                tags=tags,
                notes=notes,
                image_path=st.session_state["saved_path"]
            )
            
            st.success(f"Item saved successfully as ID #{item_id}!")
            # Clean session state
            del st.session_state["detected_metadata"]
            if "uploaded_file_bytes" in st.session_state:
                del st.session_state["uploaded_file_bytes"]
            if "saved_path" in st.session_state:
                del st.session_state["saved_path"]
            st.rerun()

# ----------------- 4. OUTFIT RECOMMENDATION -----------------
elif page_choice == "💡 Outfit Recommendation":
    st.markdown("<h1 class='gradient-text'>AI Styled Outfits</h1>", unsafe_allow_html=True)
    st.write("Generate style combinations matching an occasion and current weather rules.")
    
    # Form elements
    occasion = st.selectbox("Occasion Type", ["College", "Office", "Interview", "Wedding", "Party", "Festival", "Casual", "Date", "Travel"])
    temp = st.slider("Forecast Temperature (°C)", -10, 45, 18)
    condition = st.selectbox("Forecast Condition", ["Clear/Sunny", "Cloudy", "Rainy", "Snowy", "Windy"])
    
    if st.button("Generate Outfits"):
        wardrobe_items = agents["closet"].get_inventory()
        if not wardrobe_items:
            st.warning("Please add clothing items to your wardrobe first.")
        else:
            with st.spinner("AI Agents consulting style & weather matrices..."):
                # Get weather rule text
                weather_advice = agents["weather"].generate_weather_advice(temp, condition, api_key=api_key)
                
                # Recommend outfits
                recommendations = agents["style"].recommend_outfits(
                    wardrobe_items=wardrobe_items,
                    occasion=occasion,
                    weather_advice=weather_advice,
                    api_key=api_key
                )
                
            st.markdown("### Styling Recommendations")
            if not recommendations:
                st.info("No cohesive outfits could be formulated. Try adding more variety of tops, bottoms, and shoes.")
            
            for idx, rec in enumerate(recommendations):
                # Custom styled recommendation card
                st.markdown(f"""
                <div class="clothing-card" style="border-left: 5px solid #818cf8; background: rgba(99, 102, 241, 0.03); margin-bottom: 20px;">
                    <h3 style="color: #ffffff; margin-bottom: 4px; font-weight: 700;">👔 {rec.get('name')}</h3>
                    <p style="font-size: 14px; font-weight: 500; color: #cbd5e1;">Vibe: <i>{rec.get('description')}</i></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Fetch detailed items forming outfit
                outfit_items = []
                item_ids = rec.get("item_ids", [])
                for iid in item_ids:
                    it = agents["closet"].get_item(iid)
                    if it:
                        outfit_items.append(it)
                
                # Display those items in a clean grid
                display_clothing_grid(outfit_items, is_wishlist=False)
                
                # Expandable stylist notes card
                with st.expander("📝 View Custom Stylist Advisory Notes", expanded=True):
                    st.info(rec.get('stylist_notes'))
                
                # Save button
                if st.button("⭐ Save Outfit to Favorites", key=f"save_outfit_{idx}"):
                    items_str = ",".join(map(str, item_ids))
                    database.save_recommended_outfit(
                        name=rec.get("name"),
                        description=rec.get("description"),
                        items=items_str,
                        occasion=occasion,
                        is_favorite=1
                    )
                    st.success("Outfit saved to Favorites!")
                st.markdown("<hr style='border: 0; height: 1px; background: rgba(255,255,255,0.08); margin: 30px 0;'>", unsafe_allow_html=True)

# ----------------- 5. TODAY'S OUTFIT -----------------
elif page_choice == "📅 Today's Outfit":
    st.markdown("<h1 class='gradient-text'>Log Today's Outfit</h1>", unsafe_allow_html=True)
    st.write("Log the items you wear today to keep your sustainability statistics accurate and build style history.")
    
    items = agents["closet"].get_inventory()
    
    if not items:
        st.warning("Your wardrobe is empty. Add items first.")
    else:
        # Multi-select items to wear
        item_options = {f"#{it['id']} - {it['notes']} ({it['category']})": it['id'] for it in items}
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            selected_worn = st.multiselect("Select the items worn today:", list(item_options.keys()))
            occasion = st.selectbox("Log Occasion", ["Casual", "College", "Office", "Interview", "Wedding", "Party", "Festival", "Date", "Travel"])
        with col_input2:
            rating = st.slider("Style satisfaction rating (1-5)", 1, 5, 5)
            feedback = st.text_input("Any personal styling feedback / notes?")
            
        if st.button("Log Wear Activity"):
            if not selected_worn:
                st.error("Please select at least one item.")
            else:
                for item_label in selected_worn:
                    item_id = item_options[item_label]
                    agents["closet"].log_wear(
                        item_id=item_id,
                        occasion=occasion,
                        rating=rating,
                        feedback=feedback
                    )
                st.success("Successfully logged today's wear history!")
                st.balloons()
                st.rerun()
                
    st.markdown("---")
    st.subheader("📜 Recent Wear History Logs")
    logs = agents["closet"].get_usage_logs()
    if logs:
        # Convert list of logs into a pretty display
        for lg in logs[:10]: # show latest 10
            cat_emojis = {"top": "👚", "bottom": "👖", "shoes": "👟", "outer": "🧥", "dress": "👗", "accessory": "👜"}
            cat_icon = cat_emojis.get(lg.get("category", "").lower(), "🏷️")
            rating_stars = "⭐" * lg.get("rating", 0)
            
            st.markdown(f"""
            <div class="clothing-card" style="padding: 16px; margin-bottom: 12px; background: rgba(15, 23, 42, 0.35);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13px; color: #818cf8; font-weight: 600;">📅 {lg.get('date_worn')}</span>
                    <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 600;">🎗️ {lg.get('occasion')}</span>
                </div>
                <p style="font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 4px;">
                    {cat_icon} {lg.get('notes') or 'Clothing Item'} ({lg.get('colors')})
                </p>
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 4px;">
                    Feedback: <i>"{lg.get('feedback') or 'No notes provided'}"</i>
                </p>
                <div style="font-size: 12px; color: #fbbf24;">Satisfaction: {rating_stars}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No wear history logged yet.")

# ----------------- 6. WARDROBE ANALYTICS -----------------
elif page_choice == "📊 Wardrobe Analytics":
    st.markdown("<h1 class='gradient-text'>Wardrobe Analytics & Cost-Per-Wear</h1>", unsafe_allow_html=True)
    
    items = database.get_all_clothing_items()
    if not items:
        st.warning("No data available. Add items to view visual insights.")
    else:
        df = pd.DataFrame(items)
        
        # Calculate KPI variables
        total_value = df["price"].sum()
        avg_price = df["price"].mean()
        most_worn = df.loc[df["wear_count"].idxmax()] if len(df) > 0 and df["wear_count"].max() > 0 else None
        
        # KPI Cards row
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(f"""
            <div class="clothing-card" style="text-align: center; border-bottom: 3px solid #818cf8; padding: 18px;">
                <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase;">💳 Total Wardrobe Value</p>
                <h3 style="font-size: 26px; color: #ffffff; margin: 0;">${total_value:.2f}</h3>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class="clothing-card" style="text-align: center; border-bottom: 3px solid #c084fc; padding: 18px;">
                <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase;">📈 Avg Piece Value</p>
                <h3 style="font-size: 26px; color: #ffffff; margin: 0;">${avg_price:.2f}</h3>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            most_worn_name = most_worn["notes"] if most_worn is not None else "N/A"
            most_worn_count = most_worn["wear_count"] if most_worn is not None else 0
            st.markdown(f"""
            <div class="clothing-card" style="text-align: center; border-bottom: 3px solid #f472b6; padding: 18px;">
                <p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px; text-transform: uppercase;">🔥 Most Loved Piece</p>
                <h3 style="font-size: 20px; color: #ffffff; margin: 0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                    {most_worn_name} ({most_worn_count} wears)
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
        # Charts section
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📁 Categories Distribution")
            fig1 = px.pie(df, names="category", title="Items per Category", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
        with col_c2:
            st.subheader("💵 Cost-Per-Wear (CPW) Analysis")
            st.write("An item's value is determined by how often you wear it relative to its price.")
            
            cpw_insights = agents["shopping"].get_cost_per_wear_insights()
            df_cpw = pd.DataFrame(cpw_insights)
            
            fig2 = px.bar(df_cpw, x="notes", y="cpw", color="wear_count", 
                         labels={"cpw": "Cost-Per-Wear ($)", "notes": "Clothing Item"},
                         title="Cost-Per-Wear (Hover to see details)",
                         color_continuous_scale="Viridis")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.subheader("📋 Cost-Per-Wear Metrics Data")
        st.dataframe(df_cpw[["notes", "category", "price", "wear_count", "cpw"]])

# ----------------- 7. SUSTAINABILITY -----------------
elif page_choice == "🌿 Sustainability":
    st.markdown("<h1 class='gradient-text'>Wardrobe Sustainability Matrix</h1>", unsafe_allow_html=True)
    st.write("Review eco-efficiency scores, underused items, and styling ideas to extend clothing lifespan.")
    
    stats = agents["sustainability"].calculate_utilization()
    
    # Custom Green Score Card
    st.markdown(f"""
    <div class="eco-score-card">
        <h3 style="color: #34d399; margin-bottom: 6px; font-weight: 700;">🌍 Wardrobe Sustainability Performance</h3>
        <p style="font-size: 14px; color: #a7f3d0; margin-bottom: 20px;">
            Analyzing fabric sustainability indices and overall utility distribution.
        </p>
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 16px; padding: 15px 30px; min-width: 150px;">
                <span style="font-size: 12px; color: #a7f3d0; text-transform: uppercase; font-weight: 600;">Index Score</span>
                <h2 style="font-size: 36px; color: #ffffff; margin: 5px 0 0 0; font-weight: 700;">{stats['sustainability_score']}/100</h2>
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 16px; padding: 15px 30px; min-width: 150px;">
                <span style="font-size: 12px; color: #a7f3d0; text-transform: uppercase; font-weight: 600;">Utilization Rate</span>
                <h2 style="font-size: 36px; color: #ffffff; margin: 5px 0 0 0; font-weight: 700;">{stats['utilization_rate']}%</h2>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Reports
    st.subheader("🌿 Personalized Sustainability Report")
    if not api_key:
        st.warning("Please configure your Groq API Key to see full sustainability feedback report.")
    report = agents["sustainability"].generate_sustainability_report(stats, api_key=api_key)
    st.info(report)
    
    st.markdown("---")
    
    # Underused items
    st.subheader("⚠️ Underused Clothing Items (Worn <= 1 Time)")
    if stats["underused"]:
        display_clothing_grid(stats["underused"])
    else:
        st.success("Great job! All items in your wardrobe have been worn frequently.")

# ----------------- 8. TRAVEL PACKING -----------------
elif page_choice == "✈️ Travel Packing":
    st.markdown("<h1 class='gradient-text'>Minimalist Packing Assistant</h1>", unsafe_allow_html=True)
    st.write("Generates a capsule wardrobe checklist for your upcoming trip using your own wardrobe inventory.")
    
    # Horizontal Itinerary Layout
    col_it1, col_it2, col_it3 = st.columns(3)
    with col_it1:
        destination = st.text_input("Destination City / Country", "Paris, France")
    with col_it2:
        duration = st.number_input("Trip Duration (Days)", min_value=1, max_value=30, value=5)
    with col_it3:
        weather_cond = st.selectbox("Expected Weather Mode", ["Warm / Sunny", "Mild / Rainy", "Cold / Snowy", "Windy / Variable"])
    
    if st.button("Generate Packing List"):
        items = agents["closet"].get_inventory()
        if not items:
            st.warning("Please add clothing items to your digital wardrobe first.")
        else:
            with st.spinner("AI is planning your packing checklist..."):
                packing_res = agents["packing"].generate_packing_list(
                    wardrobe_items=items,
                    destination=destination,
                    weather_condition=weather_cond,
                    duration_days=duration,
                    api_key=api_key
                )
                
            st.subheader("🧳 Packing Checklist")
            st.info(packing_res.get("explanation", "Packing ideas"))
            
            # Show items
            packed_items = packing_res.get("packing_list", [])
            if packed_items:
                grid_items = []
                for pi in packed_items:
                    it = agents["closet"].get_item(pi.get("item_id"))
                    if it:
                        grid_items.append(it)
                        # Suitcase style checklist card
                        st.markdown(f"""
                        <div class="suitcase-card" style="margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span style="font-size: 24px;">🧳</span>
                                <div>
                                    <h5 style="color: #fbbf24; margin: 0; font-weight: 700;">{it['notes']}</h5>
                                    <p style="font-size: 12px; color: #d1d5db; margin: 2px 0 0 0;">
                                        <b>Category:</b> {it['category'].title()} | <b>Reason:</b> {pi.get('reason')}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                st.markdown("### Visual Checklist Gallery")
                display_clothing_grid(grid_items)
            else:
                st.info("No items matches the category criteria.")
                
            st.subheader("💡 Capsule Mix & Match Ideas")
            st.write(packing_res.get("mix_match_ideas", ""))

# ----------------- 9. SHOPPING ADVISOR -----------------
elif page_choice == "🛍️ Shopping Advisor":
    st.markdown("<h1 class='gradient-text'>Shopping Advisor & Wishlist</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["🛒 Evaluate Potential Buy", "📝 Wishlist Registry"])
    
    with tabs[0]:
        st.subheader("Evaluate a prospective item before buying")
        st.write("Prevent duplicates and calculate double-buying prevention score.")
        
        category = st.selectbox("Prospective Category", ["top", "bottom", "shoes", "outer", "dress", "accessory"])
        colors = st.text_input("Colors", "black, grey")
        pattern = st.selectbox("Pattern Type", ["solid", "striped", "plaid", "floral", "graphic", "other"])
        fabric = st.text_input("Fabric Material", "cotton")
        price = st.number_input("Price ($)", min_value=0.0, value=49.99)
        
        if st.button("Run Pre-Purchase Assessment"):
            with st.spinner("AI Shopping agent auditing database..."):
                eval_res = agents["shopping"].evaluate_wishlist_item(
                    category=category,
                    colors=colors,
                    pattern=pattern,
                    fabric=fabric,
                    price=price,
                    api_key=api_key
                )
                
            # Premium assessment review card
            st.markdown("### Pre-Purchase Assessment Result")
            if eval_res.get("is_duplicate"):
                st.markdown(f"""
                <div class="clothing-card" style="border: 1px solid rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.03); padding: 20px;">
                    <h4 style="color: #f87171; margin-bottom: 6px; font-weight: 700;">⚠️ Duplicate Risk Warning</h4>
                    <p style="font-size: 14px; color: #fca5a5; line-height: 1.5; margin: 0;">{eval_res.get('duplicate_reason')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="clothing-card" style="border: 1px solid rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.03); padding: 20px;">
                    <h4 style="color: #34d399; margin-bottom: 6px; font-weight: 700;">✅ Unique Addition Verified</h4>
                    <p style="font-size: 14px; color: #a7f3d0; line-height: 1.5; margin: 0;">This item is distinct from your current wardrobe entries.</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="clothing-card" style="margin-top: 15px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <h5 style="color: #818cf8; margin: 0; font-weight: 700;">Versatility Score</h5>
                    <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; font-weight: 700; font-size: 16px; padding: 4px 12px; border-radius: 12px;">
                        {eval_res.get('versatility_score')}/100
                    </span>
                </div>
                <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin-bottom: 12px;">{eval_res.get('versatility_analysis')}</p>
                <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 12px;">
                    <h6 style="color: #fbbf24; margin-bottom: 4px; font-weight: 700;">Stylist Verdict</h6>
                    <p style="font-size: 13px; color: #cbd5e1; line-height: 1.5; margin: 0;"><i>"{eval_res.get('advice')}"</i></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Option to save to wishlist
            if st.button("Save to Wishlist"):
                database.add_wishlist_item(
                    category=category,
                    colors=colors,
                    pattern=pattern,
                    fabric=fabric,
                    price=price,
                    estimated_wear_count=15
                )
                st.success("Saved to wishlist!")
                st.rerun()
                
    with tabs[1]:
        st.subheader("My Wishlist Items")
        w_items = database.get_wishlist_items()
        
        def handle_wish_delete(wish_id):
            database.delete_wishlist_item(wish_id)
            st.success("Wishlist item deleted!")
            
        if w_items:
            display_clothing_grid(w_items, is_wishlist=True, on_delete=handle_wish_delete)
        else:
            st.info("Wishlist is empty.")

# ----------------- 10. SETTINGS -----------------
elif page_choice == "⚙️ Settings":
    st.markdown("<h1 class='gradient-text'>Settings & Preferences</h1>", unsafe_allow_html=True)
    
    st.subheader("API Keys Configuration")
    
    # Groq Input ke liye unique key lagayein
    user_groq_input = st.text_input(
        "Groq API Key", 
        type="password", 
        value=os.environ.get("GROQ_API_KEY", ""), 
        help="Enter your Groq API Key",
        key="settings_groq_api_key"  # <-- Yeh unique key lagayein
    )
    
    # Gemini Input ke liye unique key lagayein
    user_gemini_input = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=os.environ.get("GEMINI_API_KEY", ""), 
        help="Enter your Gemini API Key",
        key="settings_gemini_api_key"  # <-- Yeh unique key lagayein
    )

    if st.button("Save Keys", key="save_keys_settings"):
        if user_groq_input:
            os.environ["GROQ_API_KEY"] = user_groq_input.strip()
        if user_gemini_input:
            os.environ["GEMINI_API_KEY"] = user_gemini_input.strip()
        st.success("API keys updated successfully!")
    st.markdown("---")
    st.subheader("User Style Profiles")
    
    pref_agent = agents["preference"]
    profile = pref_agent.load_preference_profile()
    
    fav_colors = st.text_input(
        "Favorite Colors (comma separated)",
        ", ".join(profile.get("favorite_colors", []))
    )
    
    pref_occ = st.text_input(
        "Preferred Occasions (comma separated)",
        ", ".join(profile.get("preferred_occasions", []))
    )
    
    style_options = [
        "Casual",
        "Classic",
        "Minimalist",
        "Bold",
        "Bohemian",
        "Alternative"
    ]
    
    saved_style = profile.get("style_vibe", "Casual")
    
    if saved_style not in style_options:
        saved_style = "Casual"
    
    style_vibe = st.selectbox(
        "Style Vibe",
        style_options,
        index=style_options.index(saved_style)
    )
    
    if st.button("Save Style Preferences"):
        profile["favorite_colors"] = [
            c.strip() for c in fav_colors.split(",") if c.strip()
        ]
        profile["preferred_occasions"] = [
            o.strip() for o in pref_occ.split(",") if o.strip()
        ]
        profile["style_vibe"] = style_vibe
    
        pref_agent.save_preference_profile(profile)
        st.success("Style preference profile saved successfully!")
    
    st.markdown("---")
    st.subheader("AI Preferences Learning")
    st.write(
        "Let the preference agent analyze your wardrobe and logs history to refine preferences automatically."
    )
    
    if st.button("Run Implicit Profile Learning"):
        with st.spinner("Analyzing history..."):
            learn_msg = pref_agent.learn_preferences_from_history(api_key=user_key)
    
        st.info(learn_msg)
