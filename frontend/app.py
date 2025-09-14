import streamlit as st
import requests
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🎓 Course Finder",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .course-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .course-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-container {
        display: flex;
        justify-content: space-around;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .metric-item {
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #6c757d;
    }
    
    .search-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .difficulty-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem 0;
    }
    
    .difficulty-beginner { background-color: #d4edda; color: #155724; }
    .difficulty-intermediate { background-color: #fff3cd; color: #856404; }
    .difficulty-advanced { background-color: #f8d7da; color: #721c24; }
    .difficulty-mixed {
    background-color: #f3e5f5; /* Very light lavender */
    color: #4a148c; /* Deep purple */
    }      
    
    .organization-tag {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🎓 Course Finder</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
        Discover your perfect learning path with Sharma's AI-powered recommendation system!
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for filters and settings
with st.sidebar:
    st.header("⚙️ Search Settings")
    
    # Quick search suggestions
    st.subheader("💡 Popular Searches")
    quick_searches = [
        "Machine Learning for Beginners",
        "Advanced Python Programming", 
        "Data Science Fundamentals",
        "Web Development Bootcamp",
        "Digital Marketing Strategy",
        "Cybersecurity Essentials"
    ]
    
    selected_quick = st.selectbox("Choose a quick search:", ["Custom search..."] + quick_searches)
    
    # Difficulty filter
    st.subheader("📊 Difficulty Level")
    difficulty_filter = st.radio(
        "Preferred difficulty:",
        ["Any", "Beginner", "Intermediate", "Advanced"],
        index=0
    )
    
    # Number of results
    st.subheader("📈 Results")
    top_k = st.slider("Number of recommendations:", 1, 15, 8)
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        st.write("**Ranking Weights**")
        similarity_weight = st.slider("Content Similarity", 0.0, 1.0, 0.6, 0.1)
        rating_weight = st.slider("Course Rating", 0.0, 1.0, 0.2, 0.1)
        popularity_weight = st.slider("Popularity", 0.0, 1.0, 0.2, 0.1)

# Main search area
st.markdown('<div class="search-container">', unsafe_allow_html=True)

# col1, col2 = st.columns([4, 1])

# with col1:
    # Use quick search if selected, otherwise use text input
if selected_quick != "Custom search...":
    query = st.text_input(
        "🔍 What would you like to learn?", 
        value=selected_quick,
        help="Enter keywords, topics, or skills you want to learn"
    )
else:
    query = st.text_input(
        "🔍 What would you like to learn?", 
        placeholder="e.g., machine learning, web development, data analysis...",
        help="Enter keywords, topics, or skills you want to learn"
    )

# with col2:
st.write("")  # spacing
search_clicked = st.button("🔍 Find Courses", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add difficulty to query if selected
if difficulty_filter != "Any" and query:
    query_with_difficulty = f"{difficulty_filter.lower()} {query}"
else:
    query_with_difficulty = query

# Search functionality
if search_clicked or query:
    if query:
        with st.spinner("Searching for the perfect courses..."):
            try:
                # Add a small delay for better UX
                time.sleep(0.5)
                
                response = requests.post(
                    "http://localhost:8000/recommend", 
                    json={"query": query_with_difficulty, "top_k": top_k},
                    timeout=30
                )
                
                if response.status_code == 200:
                    recommendations = response.json()["recommendations"]
                    
                    # Results header
                    st.success(f"Found {len(recommendations)} amazing courses for you!✨")
                    
                    
                    st.markdown("---")
                    
                    # Display recommendations
                    for i, rec in enumerate(recommendations, 1):
                        # Determine difficulty badge class
                        diff_class = f"difficulty-{rec['difficulty'].lower()}"
                        
                        # Format student count
                        if rec['students'] >= 1000000:
                            students_display = f"{rec['students']/1000000:.1f}M students"
                        elif rec['students'] >= 1000:
                            students_display = f"{rec['students']/1000:.0f}K students"
                        else:
                            students_display = f"{rec['students']:,} students"
                        
                        # Create course card
                        st.markdown(f"""
                        <div class="course-card">
                            <div style="display: flex; justify-content: between; align-items: flex-start; margin-bottom: 1rem;">
                                <div style="flex: 1;">
                                    <h3 style="margin: 0 0 0.5rem 0; color: #2c3e50; line-height: 1.3;">
                                        {i}. {rec['title']}
                                    </h3>
                                    <span class="organization-tag">📚 {rec['organization']}</span>
                                    <span class="organization-tag">🎓 {students_display}</span>
                                    <span class="difficulty-badge {diff_class}">📈 {rec['difficulty'].title()}</span>                                 
                                </div>
                                <div style="text-align: right; margin-left: 1rem;">
                                    <div style="font-size: 1.5rem; color: #f39c12; margin-bottom: 0.25rem;">
                                        {"⭐" * int(rec['rating'])}{"☆" * (5 - int(rec['rating']))}
                                    </div>
                                    <div style="font-size: 0.9rem; color: #7f8c8d;">
                                        {rec['rating']}/5.0
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show search timestamp
                    st.markdown("---")
                    st.caption(f"🕐 Search completed at {datetime.now().strftime('%H:%M:%S')} | Powered by AI recommendations")
                    
                else:
                    st.error(f"❌ Error: {response.status_code} — Could not fetch recommendations. Please try again.")
                    
            except requests.exceptions.RequestException as e:
                st.error("Connection Error: Make sure your API server is running on http://localhost:8000")
                st.info("💡 **Tip:** Run your FastAPI server with: `uvicorn main:app --reload`")
            
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
    else:
        st.warning("Please enter a search query to find courses")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        <p>🎓 <strong>Course Finder</strong> - Your AI-powered learning companion</p>
        <p>Discover, Learn, Grow 📈</p>
    </div>
    """, unsafe_allow_html=True)

# Add some helpful information in an expander
with st.expander("How to get the best recommendations"):
    st.markdown("""
    **💡 Tips for better search results:**
    
    - **Be specific**: Instead of "programming", try "Python web development" or "JavaScript for beginners"
    - **Include skill level**: Add "beginner", "intermediate", or "advanced" to your search
    - **Mention your goal**: "machine learning for data science" or "React for mobile apps"
    - **Try different keywords**: If you don't find what you want, rephrase your search
    
    **☰ Using the sidebar:**
    - **Quick searches**: Try popular search terms for inspiration
    - **Difficulty filter**: Filter results by your preferred learning level  
    - **Advanced settings**: Adjust how courses are ranked (similarity vs. rating vs. popularity)
    
    **📊 Understanding the results:**
    - Courses are ranked by relevance, rating, and popularity
    - Higher rated courses with more students tend to rank higher
    - Difficulty level matching gives an extra boost to relevant results
    """)