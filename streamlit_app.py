#!/usr/bin/env python3
"""
ResearchBook - Streamlit Web Interface
Academic Intelligence Platform
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from researchbook_final import ResearchBookFinal
import json
import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="ResearchBook - Academic Intelligence Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize ResearchBook
@st.cache_resource
def init_researchbook():
    """Initialize ResearchBook connection (cached for performance)"""
    return ResearchBookFinal()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 ResearchBook</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Academic Intelligence Platform powered by Neo4j + AI</p>', unsafe_allow_html=True)
    
    # Initialize ResearchBook
    try:
        rb = init_researchbook()
        st.success("✅ Connected to databases and AI system")
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    feature = st.sidebar.selectbox(
        "Choose ResearchBook Feature:",
        [
            "🏠 Home",
            "🤖 Smart Research Assistant",
            "👤 Person Lookup", 
            "🎯 Expert Finder",
            "📊 Field Intelligence Brief",
            "📈 Database Overview",
            "📚 User Guide"
        ]
    )
    
    # Main content based on selection
    if feature == "🏠 Home":
        show_home_page()
    elif feature == "🤖 Smart Research Assistant":
        show_smart_research_assistant(rb)
    elif feature == "👤 Person Lookup":
        show_person_lookup(rb)
    elif feature == "🎯 Expert Finder":
        show_expert_finder(rb)
    elif feature == "📊 Field Intelligence Brief":
        show_field_brief(rb)
    elif feature == "💝 Researcher Matching":
        show_researcher_matching(rb)
    elif feature == "📈 Database Overview":
        show_database_overview(rb)
    elif feature == "📚 User Guide":
        show_user_guide()

def show_home_page():
    """Home page with feature overview"""
    st.markdown("## Welcome to ResearchBook! 🚀")
    
    # Highlight Smart Research Assistant
    st.markdown("""
    <div class="feature-card" style="border-left: 5px solid #4CAF50; background-color: #f1f8e9;">
        <h3>🤖 Smart Research Assistant - NEW!</h3>
        <p><strong>Ask anything in natural language!</strong> "Who should meet with Dr. Sarah Chen from MIT?" or "Find me AI experts at Chalmers" - just ask and get intelligent, context-aware responses.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>👤 Person Lookup</h3>
            <p>Search our comprehensive researcher network. Get detailed profiles with ORCID data, career history, thesis involvement, and AI-generated expertise analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Field Intelligence Brief</h3>
            <p>Generate comprehensive research field reports. Analyze researcher networks, trends, and opportunities with AI-powered insights.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Expert Finder</h3>
            <p>Find experts on any topic with AI ranking. Get specific recommendations for media interviews, collaborations, or student supervision.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        """, unsafe_allow_html=True)
    
    # Database stats
    st.markdown("## 📊 Database Coverage")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Academic Network", "154K", "Researchers")
    with col2:
        st.metric("Thesis Ecosystem", "58K", "Academic Relationships")
    with col3:
        st.metric("ORCID Coverage", "78K", "50% Coverage")
    with col4:
        st.metric("Relationship Roles", "731", "Unique Types")

def show_smart_research_assistant(rb):
    """Smart Research Assistant - Natural language interface"""
    st.markdown("## 🤖 Smart Research Assistant")
    st.markdown("Ask anything about researchers, expertise, or strategic meetings in natural language!")
    
    # Quick examples
    with st.expander("💡 Example Questions", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **👤 Person Profile Questions:**
            - "What do you know about Erik Bohlin?"
            - "Show me Jikuang Yang's research"
            - "Tell me about Adil Mardinoglu"
            
            **📊 Expert & Field Analysis:**
            - "Find AI experts at Chalmers"
            - "Show me vehicle safety researchers"
            - "Who works on sustainability?"
            """)
        
        with col2:
            st.markdown("""
            **🤝 Smart Research Assistant (Relations):**
            - "show me 15 relations for Henk Wymeersch"                    
            - "show me 15 relations for Erik Bohlin"
            - "Tiina Nypelö connections"  
            - "Jikuang Yang network"
            - "show connections for Adil Mardinoglu"
            - "Agisilaos Papadogiannis relations"
            
            **💝 Collaboration Matching:**
            - "Find researchers similar to Erik Bohlin"
            - "Who should collaborate with Tiina Nypelö?"
            - "Match with vehicle safety experts"
            """)
    
    # Main input interface
    st.markdown("### 💬 Ask Your Question")
    user_query = st.text_area(
        "What would you like to know?",
        height=120,
        placeholder="e.g., 'Find me 3 Chalmers researchers who should meet with Dr. Sarah Chen from Stanford who works on renewable energy and solar panels'"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("🔍 Ask ResearchBook", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if ask_button and user_query.strip():
        with st.spinner("🤖 Understanding your question and searching our databases..."):
            try:
                # Use the smart query handler
                result = rb.smart_query_handler(user_query.strip())
                
                # Show query interpretation
                if result.get('query_interpretation'):
                    intent = result['query_interpretation']
                    st.markdown("### 🧠 How I Understood Your Question")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        query_type = intent.get('query_type', 'general').replace('_', ' ').title()
                        st.metric("Query Type", query_type)
                    with col2:
                        confidence = intent.get('confidence', 0.8)
                        st.metric("Confidence", f"{confidence:.1%}")
                    with col3:
                        entities_count = len([v for v in intent.get('entities', {}).values() if v])
                        st.metric("Entities Found", entities_count)
                
                # Handle different response types
                if 'error' in result:
                    st.error(f"❌ {result['error']}")
                    if result.get('suggestion'):
                        st.info(f"💡 {result['suggestion']}")
                
                elif result.get('query_interpretation', {}).get('query_type') == 'meeting_recommendation':
                    # Strategic meeting response
                    st.markdown("### 🤝 Strategic Meeting Recommendations")
                    
                    if result.get('participants_found', 0) > 0:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Visitor", result.get('visitor', 'N/A'))
                        with col2:
                            st.metric("HARD Relations", result.get('hard_relations_found', 0))
                        with col3:
                            st.metric("MJUK Relations", result.get('mjuk_relations_found', 0))
                        
                        # Show participants by type
                        if result.get('recommended_participants'):
                            # Separate HARD and MJUK relations
                            hard_participants = [p for p in result['recommended_participants'] if p.get('relation_strength') == 'HARD']
                            mjuk_participants = [p for p in result['recommended_participants'] if p.get('relation_strength') == 'MJUK']
                            
                            if hard_participants:
                                st.markdown("### 🔗 HARD Relations (Konkreta Historiska Bevis)")
                                
                                # Map relation types to Swedish names
                                relation_names = {
                                    'medforfattare': 'Medförfattare',
                                    'handledarnatverk': 'Handledarnätverk: Handledning och examination',
                                    'samma_alma_mater': 'Båda studerade vid samma plats',
                                    'arbetade_samma_org': 'Arbetade på samma organisation'
                                }
                                
                                for i, participant in enumerate(hard_participants):
                                    relation_type = participant.get('relation_type', 'N/A')
                                    swedish_name = relation_names.get(relation_type, relation_type)
                                    st.markdown(f"**{i+1}. {participant['name']}** - *{swedish_name}*")
                            
                            if mjuk_participants:
                                st.markdown("### 🔍 MJUK Relations (Research Alignment)")
                                for i, participant in enumerate(mjuk_participants):
                                    st.markdown(f"**{i+1}. {participant['name']}** - *{participant.get('relation_type', 'N/A')}*")
                        
                        # AI Strategic Analysis
                        st.markdown("### 🎯 Brief Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('strategic_analysis', 'Analysis not available')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"No suitable meeting participants found for {result.get('visitor', 'the visitor')}.")
                        
                elif result.get('query_interpretation', {}).get('query_type') == 'expert_finder':
                    # Expert finder response
                    st.markdown("### 🎯 Expert Search Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Experts", result.get('experts_found', 0))
                    with col2:
                        st.metric("Research Network", result.get('research_intelligence_matches', 0))
                    with col3:
                        st.metric("Academic Network", result.get('academic_network_matches', 0))
                    
                    # AI Ranking
                    st.markdown("### 🤖 AI Expert Analysis")
                    st.markdown(f"""
                    <div class="result-box">
                    {result.get('ai_ranking', 'Analysis not available')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif result.get('query_interpretation', {}).get('query_type') == 'person_lookup':
                    # Person lookup response
                    st.markdown("### 👤 Person Profile")
                    
                    if result.get('found_in_db1') or result.get('found_in_db2'):
                        # AI Analysis
                        st.markdown("### 🤖 AI Profile Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('ai_analysis', 'Analysis not available')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Person not found in our databases. Try a different name variation.")
                
                elif result.get('query_interpretation', {}).get('query_type') == 'field_intelligence':
                    # Field intelligence response
                    st.markdown(f"### 📊 Field Analysis: {result.get('field', 'Research Area')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Active Researchers", result.get('researchers_found', 0))
                    with col2:
                        st.metric("Recent Activity", result.get('trends', {}).get('total_recent', 0))
                    
                    # AI Intelligence Brief
                    st.markdown("### 🤖 AI Intelligence Brief")
                    st.markdown(f"""
                    <div class="result-box">
                    {result.get('ai_intelligence_brief', 'Analysis not available')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif result.get('query_interpretation', {}).get('query_type') == 'researcher_matching':
                    # Researcher matching response
                    st.markdown("### 💝 Collaboration Matches")
                    
                    if result.get('matches_found', 0) > 0:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Target Researcher", result.get('target_researcher', 'N/A'))
                        with col2:
                            st.metric("Potential Matches", result['matches_found'])
                        
                        # AI Analysis
                        st.markdown("### 🤖 AI Match Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('ai_analysis', 'Analysis not available')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("No matches found. Try a different researcher name.")
                
                else:
                    # General/fallback response
                    st.markdown("### 🔍 Search Results")
                    
                    if result.get('fallback_search'):
                        st.info("🔄 Processed as general expert search")
                    
                    if result.get('ai_ranking'):
                        st.markdown("### 🤖 AI Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('ai_ranking', 'Analysis not available')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if result.get('experts_found', 0) > 0:
                        st.metric("Experts Found", result['experts_found'])
                    
                # Raw data toggle (for debugging)
                if st.toggle("🔧 Show raw response data", value=False):
                    st.json(result)
                    
            except Exception as e:
                st.error(f"❌ Error processing your question: {str(e)}")
                st.info("💡 Try rephrasing your question or use the traditional search functions below.")
                
    elif ask_button and not user_query.strip():
        st.warning("⚠️ Please enter a question to get started!")
    
    # Quick action buttons
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👤 Person Search"):
            st.session_state.quick_action = "👤 Person Lookup"
    with col2:
        if st.button("🎯 Find Experts"):
            st.session_state.quick_action = "🎯 Expert Finder"
    with col3:
        if st.button("📊 Field Analysis"):
            st.session_state.quick_action = "📊 Field Intelligence Brief"  
    with col4:
        if st.button("🤝 Meeting Planner"):
            # Pre-fill with meeting example
            st.text_area("Example meeting query:", 
                        "Who from Chalmers should meet with Dr. John Smith from MIT who works on quantum computing?",
                        key="meeting_example")

def show_person_lookup(rb):
    """Person lookup interface"""
    st.markdown("## 👤 Person Lookup")
    st.markdown("Search our comprehensive academic network and get AI-powered researcher insights.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **full names**: "Maria Andersson" not just "Maria"
        - Try variations: "John Smith" vs "J. Smith"  
        - Check ORCID data for verification
        - **Read the AI analysis** - it's the most valuable part!
        
        **Perfect for:** Finding specific researchers, understanding their networks, checking expertise
        """)
    
    # Input
    researcher_name = st.text_input("Enter researcher name:", placeholder="e.g., Anders, Maria, John Smith")
    
    if st.button("🔍 Search Researcher", type="primary"):
        if researcher_name:
            with st.spinner("Searching databases and generating AI analysis..."):
                try:
                    result = rb.lookup_person(researcher_name)
                    
                    # Display results
                    st.markdown(f"### Results for: **{researcher_name}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Research Profiles", len(result.get('researcher_data', [])))
                    with col2:
                        st.metric("Academic Activities", len(result.get('thesis_data', [])))
                    with col3:
                        found_status = "Found" if (result['found_in_db1'] or result['found_in_db2']) else "Not Found"
                        st.metric("Status", found_status)
                    
                    if result['found_in_db1'] or result['found_in_db2']:
                        # AI Analysis
                        st.markdown("### 🤖 AI Profile Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('ai_analysis', 'No analysis available')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed data tabs
                        tab1, tab2 = st.tabs(["📊 Research Profile", "🎓 Thesis Activities"])
                        
                        with tab1:
                            if result.get('researcher_data'):
                                st.markdown("#### Database 1: Research Profile")
                                for i, profile in enumerate(result['researcher_data']):
                                    with st.expander(f"Profile {i+1}: {profile['name']}"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**ORCID ID:** {profile.get('orcid_id', 'N/A')}")
                                            st.write(f"**Publications:** {profile.get('total_publications', 0)}")
                                        with col2:
                                            st.write(f"**Given Names:** {profile.get('given_names', 'N/A')}")
                                            st.write(f"**Family Name:** {profile.get('family_name', 'N/A')}")
                                        
                                        if profile.get('affiliations'):
                                            st.write("**Affiliations:**")
                                            for aff in profile['affiliations']:
                                                st.write(f"- {aff.get('organization', 'Unknown')} ({aff.get('role', 'N/A')})")
                        
                        with tab2:
                            if result.get('thesis_data'):
                                st.markdown("#### Database 2: Thesis Activities")
                                try:
                                    # Fix list columns that cause rendering issues
                                    thesis_data_clean = []
                                    for thesis in result['thesis_data']:
                                        thesis_clean = thesis.copy()
                                        # Convert keywords list to string
                                        if 'keywords' in thesis_clean and isinstance(thesis_clean['keywords'], list):
                                            thesis_clean['keywords'] = ', '.join(thesis_clean['keywords'])
                                        # Also handle abstract length - might be too long
                                        if 'abstract' in thesis_clean and len(str(thesis_clean['abstract'])) > 500:
                                            thesis_clean['abstract'] = str(thesis_clean['abstract'])[:500] + "..."
                                        thesis_data_clean.append(thesis_clean)
                                    
                                    # Skip DataFrame entirely - use simple display
                                    st.write("**Thesis Activities:**")
                                    for i, thesis in enumerate(thesis_data_clean, 1):
                                        st.write(f"**{i}. {thesis.get('role', 'Unknown Role')}**")
                                        st.write(f"📄 Title: {thesis.get('thesis_title', 'No title')}")
                                        st.write(f"📚 Type: {thesis.get('thesis_type', 'Unknown')}")
                                        st.write(f"🏷️ Keywords: {thesis.get('keywords', 'None')}")
                                        if thesis.get('abstract'):
                                            with st.expander("View Abstract"):
                                                st.write(thesis['abstract'])
                                        st.divider()
                                    
                                    # Debug info
                                    st.write(f"Debug: Found {len(result['thesis_data'])} thesis entries")
                                    
                                except Exception as e:
                                    st.error(f"Error displaying thesis data: {e}")
                                    st.write("Raw thesis data:")
                                    st.json(result.get('thesis_data', [])[:2])  # Show first 2 entries
                            else:
                                st.info("No thesis data found for this person.")
                    else:
                        st.warning("No researcher found with that name in either database.")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Please enter a researcher name to search.")

def show_expert_finder(rb):
    """Expert finder interface"""
    st.markdown("## 🎯 Expert Finder")
    st.markdown("Find experts on any topic with AI ranking and recommendations.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Be **specific**: "machine learning" not "AI"
        - Try synonyms: "sustainability" + "environmental science"
        - Use AI rankings - they consider expertise depth
        - Check "Best for:" recommendations (media, collaboration, supervision)
        
        **Perfect for:** Finding collaborators, media experts, understanding research landscape
        """)
    
    # Input
    topic = st.text_input("Enter research topic:", placeholder="e.g., machine learning, sustainability, robotics")
    limit = st.slider("Number of experts to find:", 5, 20, 10)
    
    if st.button("🔍 Find Experts", type="primary"):
        if topic:
            with st.spinner("Searching for experts and generating AI rankings..."):
                try:
                    result = rb.find_expert(topic, limit=limit)
                    
                    # Display results
                    st.markdown(f"### Expert Results for: **{topic}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Experts", result['experts_found'])
                    with col2:
                        st.metric("Research Network", result['db1_matches'])
                    with col3:
                        st.metric("Academic Network", result['db2_matches'])
                    
                    if result['experts_found'] > 0:
                        # AI Ranking
                        st.markdown("### 🤖 AI Expert Ranking & Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result['ai_ranking']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Expert details
                        st.markdown("### 📋 Expert Details")
                        for i, expert in enumerate(result.get('expert_list', [])):
                            with st.expander(f"Expert {i+1}: {expert['name']}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Source:** {expert.get('source', 'Unknown')}")
                                    if 'relevant_publications' in expert:
                                        st.write(f"**Relevant Publications:** {expert['relevant_publications']}")
                                    if 'relevant_theses' in expert:
                                        st.write(f"**Relevant Theses:** {expert['relevant_theses']}")
                                
                                with col2:
                                    if 'organizations' in expert:
                                        st.write(f"**Organizations:** {', '.join(expert['organizations'])}")
                                    if 'roles' in expert:
                                        st.write(f"**Roles:** {', '.join(expert['roles'])}")
                    else:
                        st.warning(f"No experts found for topic: {topic}")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Please enter a research topic to search for experts.")

def show_field_brief(rb):
    """Field intelligence brief interface"""
    st.markdown("## 📊 Field Intelligence Brief")
    st.markdown("Generate comprehensive research field analysis with AI insights.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **field names**: "artificial intelligence", "biotechnology"
        - Try broader terms for better coverage
        - Review activity trends for field momentum
        - Use AI insights for strategic planning
        
        **Perfect for:** Grant writing, strategic planning, identifying research gaps
        """)
    
    # Input
    research_field = st.text_input("Enter research field:", placeholder="e.g., artificial intelligence, sustainability, biotechnology")
    
    if st.button("📊 Generate Field Brief", type="primary"):
        if research_field:
            with st.spinner("Analyzing field data and generating intelligence brief..."):
                try:
                    result = rb.generate_field_brief(research_field)
                    
                    # Display results
                    st.markdown(f"### Field Brief: **{research_field}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Active Researchers", result['researchers_found'])
                    with col2:
                        st.metric("Recent Activity", result['trends']['total_recent'])
                    
                    # AI Intelligence Brief
                    st.markdown("### 🤖 AI Intelligence Brief")
                    st.markdown(f"""
                    <div class="result-box">
                    {result['ai_intelligence_brief']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Trends visualization
                    if result['trends']['yearly_activity']:
                        st.markdown("### 📈 Activity Trends")
                        df = pd.DataFrame(result['trends']['yearly_activity'])
                        fig = px.bar(df, x='year', y='count', 
                                   title=f"Annual Research Activity in {research_field}",
                                   labels={'year': 'Year', 'count': 'Number of Theses'})
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Analysis error: {e}")
        else:
            st.warning("Please enter a research field to analyze.")

def show_researcher_matching(rb):
    """Researcher matching interface"""
    st.markdown("## 💝 Researcher Matching")
    st.markdown('"Tinder for Researchers" - Find compatible researchers for collaboration.')
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **full researcher names** for best matches
        - Target researchers with thesis/publication activity
        - Look for complementary (not identical) expertise
        - Use AI compatibility analysis to understand WHY matches work
        
        **Perfect for:** Finding collaborators, understanding academic networks, career progression
        """)
    
    # Input
    researcher_name = st.text_input("Enter researcher name to find matches:", placeholder="e.g., Anders, Maria")
    
    if st.button("💝 Find Matches", type="primary"):
        if researcher_name:
            with st.spinner("Finding compatible researchers and generating match analysis..."):
                try:
                    result = rb.match_researchers(researcher_name)
                    
                    if 'error' not in result:
                        # Display results
                        st.markdown(f"### Matches for: **{researcher_name}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Potential Matches", result['matches_found'])
                        with col2:
                            st.metric("Keywords Used", len(result.get('target_keywords', [])))
                        
                        # Target keywords
                        if result.get('target_keywords'):
                            st.markdown("### 🏷️ Target Researcher Keywords")
                            keywords_display = ", ".join(result['target_keywords'][:10])  # Show first 10
                            st.info(f"Matching based on: {keywords_display}")
                        
                        # AI Analysis
                        st.markdown("### 🤖 AI Match Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result['ai_analysis']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Match details
                        if result.get('potential_matches'):
                            st.markdown("### 👥 Potential Matches")
                            for i, match in enumerate(result['potential_matches']):
                                with st.expander(f"Match {i+1}: {match['name']} (Relevance: {match['relevance']})"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Name:** {match['name']}")
                                        st.write(f"**Relevance Score:** {match['relevance']}")
                                    with col2:
                                        st.write(f"**Roles:** {', '.join(match.get('roles', []))}")
                                    
                                    if match.get('sample_work'):
                                        st.write("**Sample Work:**")
                                        for work in match['sample_work']:
                                            st.write(f"- {work}")
                    else:
                        st.error(result['error'])
                        
                except Exception as e:
                    st.error(f"Matching error: {e}")
        else:
            st.warning("Please enter a researcher name to find matches.")

def show_database_overview(rb):
    """Database overview and statistics"""
    st.markdown("## 📈 Database Overview")
    st.markdown("Overview of ResearchBook data sources and statistics.")
    
    # Database info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
        <h3>🌍 Research Intelligence System</h3>
        <ul>
        <li><strong>154,272</strong> researchers</li>
        <li><strong>78,287</strong> with ORCID IDs (50.7%)</li>
        <li><strong>685,709</strong> relationships</li>
        <li><strong>ORCID integration</strong> with career tracking</li>
        <li><strong>Temporal data</strong> for career progression</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
        <h3>🎓 Academic Collaboration Network</h3>
        <ul>
        <li><strong>57,633</strong> nodes (40K people, 18K theses)</li>
        <li><strong>52,772</strong> relationships</li>
        <li><strong>731</strong> unique relationship types</li>
        <li><strong>Complete thesis ecosystems</strong></li>
        <li><strong>Granular role mapping</strong></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature status
    st.markdown("### ✅ Feature Status")
    features = [
        ("Person Lookup", "✅ Working", "Search across database with AI analysis"),
        ("Expert Finder", "✅ Working", "Topic-based expert discovery with ranking"),
        ("Field Intelligence", "✅ Working", "Comprehensive research field reports"),
        ("Cross-database Integration", "✅ Working", "Seamless data correlation"),
        ("AI Analysis", "✅ Working", "Via LightLLM")
    ]
    
    for feature, status, description in features:
        col1, col2, col3 = st.columns([2, 1, 4])
        with col1:
            st.write(f"**{feature}**")
        with col2:
            st.write(status)
        with col3:
            st.write(description)

def show_user_guide():
    """Comprehensive User Guide"""
    st.markdown("## 📚 ResearchBook User Guide")
    st.markdown("Complete guide to getting maximum value from ResearchBook")
    
    # Quick Start section
    with st.expander("🚀 Quick Start (2 minutes)", expanded=True):
        st.markdown("""
        ### Get Started in 3 Steps:
        1. **Choose your task:** Find expert? Research field analysis? Collaboration partners?
        2. **Enter specific search terms** (avoid single words - be descriptive!)
        3. **Read the AI analysis** - this is where the real insights are!
        
        **💡 Pro Tip:** ResearchBook isn't just search - it's research intelligence. The AI analysis provides insights you won't find anywhere else.
        """)
    
    # Use Cases
    with st.expander("🎯 Real Use Cases", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 👨‍🔬 For Researchers:
            - **"I need AI/ML collaborators for my project"**
              → Expert Finder: "machine learning"
            
            - **"Who should I contact about sustainability?"**
              → Person Lookup: specific names from Field Brief
              
            - **"What's the landscape in my research area?"**  
              → Field Intelligence Brief: your field
            
            - **"Who could I collaborate with?"**
            """)
        
        with col2:
            st.markdown("""
            #### 👩‍💼 For Administrators/Media:
            - **"Find media experts on current topics"**
              → Expert Finder + "Best for media interviews"
            
            - **"Analyze our research strengths"**
              → Field Intelligence across multiple areas
              
            - **"Identify collaboration opportunities"**
              → Field Intelligence Brief
            
            - **"Background on research areas"**
              → Field Intelligence + Person Lookup
            """)
    
    # Feature Guides
    st.markdown("## 🔧 Feature-by-Feature Guides")
    
    # Person Lookup Guide
    with st.expander("👤 Person Lookup - Master Guide", expanded=False):
        st.markdown("""
        ### ✅ Best Practices:
        - **Use full names:** "Maria Andersson" not "Maria"
        - **Try variations:** "John Smith", "J. Smith", "J.A. Smith"
        - **Look for ORCID verification:** Green checkmark = verified researcher
        - **Don't skip AI analysis:** Contains career insights and collaboration potential
        
        ### 📊 Understanding Results:
        - **Research Profiles:** ORCID data, publications, career history
        - **Academic Activities:** Thesis supervision, examination, collaboration roles
        - **AI Analysis:** Expertise areas, career progression, network connections
        
        ### 🎯 When to Use:
        - Researching potential collaborators
        - Preparing for meetings/conferences  
        - Understanding someone's academic background
        - Verifying expertise areas
        """)
    
    # Expert Finder Guide  
    with st.expander("🎯 Expert Finder - Master Guide", expanded=False):
        st.markdown("""
        ### ✅ Search Strategy:
        - **Be specific:** "machine learning" not "computers"
        - **Try synonyms:** "sustainability" AND "environmental science"
        - **Use compound terms:** "biomedical engineering", "quantum computing"
        
        ### 📈 Interpreting Rankings:
        - **AI considers:** Publication relevance, supervision experience, career depth
        - **"Best for" recommendations:** Media (communication skills), Collaboration (complementary expertise), Supervision (teaching experience)
        - **Higher thesis counts:** More teaching/mentoring experience
        
        ### 🔍 Pro Tips:
        - Research Network = publication-based expertise
        - Academic Network = thesis/supervision expertise  
        - Both networks = well-rounded expert
        - Check sample work for relevance verification
        """)
    
    # Field Intelligence Guide
    with st.expander("📊 Field Intelligence Brief - Master Guide", expanded=False):
        st.markdown("""
        ### 🎯 Strategic Applications:
        - **Grant Writing:** Understanding field landscape and key players
        - **Research Planning:** Identifying gaps and opportunities
        - **Partnership Development:** Finding collaboration potential
        - **Competitive Analysis:** Mapping research strengths
        
        ### 📈 Reading Trends:
        - **Rising thesis counts:** Growing, active field
        - **Multiple institutions:** Collaborative opportunities exist
        - **Recent activity spikes:** Emerging hot topics
        - **Stable patterns:** Mature, established field
        
        ### 💡 AI Insights Decode:
        - **"Key Players":** Most influential researchers
        - **"Research Networks":** Collaboration clusters
        - **"Opportunities":** Gaps where you could contribute
        - **"Strategic Insights":** Actionable recommendations
        """)
    
    
    # AI Analysis Guide
    with st.expander("🤖 Understanding AI Analysis", expanded=False):
        st.markdown("""
        ### What AI Analysis Tells You:
        
        **📊 "Expertise Areas"** = What they actually work on (not just job titles)
        
        **📈 "Career Progression"** = How they've developed professionally over time
        
        **🤝 "Academic Networks"** = Who they're connected to and how
        
        **🔗 "Collaboration Potential"** = Why you should work together (specific opportunities)
        
        **🎯 "Strategic Insights"** = Bigger picture opportunities for the field
        
        ### 🎯 Trust the AI When:
        - It explains WHY someone is an expert (methodology-based reasoning)
        - It suggests specific use cases (media, collaboration, supervision)
        - It identifies patterns across multiple data points
        - It connects dots you might miss manually
        
        ### ⚠️ Verify When:
        - Names seem unusual (potential matching errors)
        - Claims seem too broad (cross-check with source data)
        - Very recent information (AI works on historical patterns)
        """)
    
    # Search Tips
    with st.expander("🔍 Advanced Search Tips", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Better Search Terms:
            
            **Instead of:** "computers"  
            **Use:** "computer science", "computational methods"
            
            **Instead of:** "environment"  
            **Use:** "sustainability", "climate science"
            
            **Instead of:** "medicine"  
            **Use:** "biomedical engineering", "clinical research"
            
            **Instead of:** "AI"  
            **Use:** "artificial intelligence", "machine learning"
            """)
        
        with col2:
            st.markdown("""
            ### 🔄 Finding Hidden Connections:
            
            1. **Use Field Intelligence** to discover field-specific terminology
            2. **Check thesis keywords** for research area vocabulary  
            3. **Try related concepts:** "robotics" → "automation", "control systems"
            4. **Follow supervision chains** to map academic families
            5. **Cross-reference different searches** to find intersection points
            """)
    
    # Getting Maximum Value
    with st.expander("💰 Getting Maximum Value", expanded=False):
        st.markdown("""
        ### 🔬 Research Planning Workflow:
        1. **Field Intelligence** → Understand the landscape
        2. **Expert Finder** → Identify key players  
        3. **Person Lookup** → Deep-dive on specific people
        
        ### 📊 Strategic Analysis Workflow:
        1. **Multiple field searches** to compare research areas
        2. **Track same searches over time** to spot trends
        3. **Use AI insights for decision-making** (not just data)
        4. **Cross-reference ORCID data** for verification
        
        ### 🚀 Pro User Strategies:
        - **Bookmark interesting researchers** (copy/paste AI analysis)
        - **Build collaboration target lists** from multiple searches
        - **Use for competitive intelligence** (who's working on what)
        - **Research preparation** for conferences, meetings, partnerships
        """)
    
    # FAQ
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        st.markdown("""
        ### Common Questions:
        
        **Q: "Why no results for my search?"**  
        A: Try broader terms, check spelling, use synonyms, or search related concepts
        
        **Q: "How accurate is the AI analysis?"**  
        A: AI interprets data patterns - always cross-check with source data when making important decisions
        
        **Q: "What if someone appears in both networks?"**  
        A: Great! More complete profile = better insights and more reliable analysis
        
        **Q: "Can I export or save results?"**  
        A: Currently view-only, but you can copy/paste AI analysis for your records
        
        **Q: "How often is data updated?"**  
        A: Research network updated regularly, thesis network reflects historical academic relationships
        
        **Q: "Why do some searches find more experts than others?"**  
        A: Popular research areas have more activity; niche fields may have fewer but higher-quality matches
        """)
    
    # Quick Reference
    with st.expander("⚡ Quick Reference Card", expanded=False):
        st.markdown("""
        ### 🚀 ResearchBook Cheat Sheet:
        
        | Feature | Best For | Pro Tip |
        |---------|----------|---------|
        | **👤 Person Lookup** | Specific researchers | Full names work best |
        | **🎯 Expert Finder** | Topic experts | Be specific, check AI rankings |
        | **📊 Field Intelligence** | Strategic planning | Perfect for grant writing |
        
        ### 💡 Remember:
        **ResearchBook isn't just search - it's research intelligence!**
        
        The AI analysis is the most valuable part - it connects dots, identifies patterns, and provides insights you won't find anywhere else.
        """)


if __name__ == "__main__":
    main()