import os
from dotenv import load_dotenv
import streamlit as st

# Import modules
from modules import csv_analysis, database_query, research_agent, google_drive, auto_dashboard

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Data Assistant",
    page_icon="🔰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for menu
if "current_menu" not in st.session_state:
    st.session_state.current_menu = "Database Query"

# Sidebar
with st.sidebar:
    st.title("🔰 AI Data Assistant")
    st.caption("Your Intelligent Data Companion")
    
    st.divider()
    
    # Navigation Menu    
    menu_items = [
        {"icon": "📝", "name": "CSV Analysis", "key": "csv"},
        {"icon": "💾", "name": "Database Query", "key": "database"},
        {"icon": "🔍", "name": "Research Agent", "key": "research"},
        {"icon": "☁️", "name": "Google Drive", "key": "drive"},
        {"icon": "📊", "name": "Auto Dashboard", "key": "dashboard"}
    ]
    
    for item in menu_items:
        if st.button(
            f"{item['icon']}  {item['name']}", 
            key=f"nav_{item['key']}",
            use_container_width=True,
            type="primary" if st.session_state.current_menu == item['name'] else "secondary"
        ):
            st.session_state.current_menu = item['name']
            st.rerun()

# Get current menu
menu = st.session_state.current_menu

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Route to the selected page
if menu == "CSV Analysis":
    csv_analysis.show()
elif menu == "Database Query":
    database_query.show()
elif menu == "Research Agent":
    research_agent.show()
elif menu == "Google Drive":
    google_drive.show()
elif menu == "Auto Dashboard":
    auto_dashboard.show()