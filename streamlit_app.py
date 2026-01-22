import streamlit as st
import sys
import os
import json
import rdflib

# Add 'app' directory to path to import reasoning_engine
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# [Cloud Fix] Inject Secrets to Environment for reasoning_engine.py
# Streamlit Cloud uses st.secrets, but our engine checks os.getenv
try:
    # Check if we are on Streamlit Cloud (st.secrets works)
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    # Running locally without .streamlit/secrets.toml
    # We rely on .env (loaded by reasoning_engine) or existing os.environ
    pass
except Exception as e:
    # Any other error with secrets?
    print(f"Warning: Issue accessing st.secrets: {e}")

# Critical Check BEFORE importing the engine
# If the key is still missing (neither in secrets nor .env loaded yet), we should check.
# Note: reasoning_engine loads .env itself, but for Cloud we need to be sure.
if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in st.secrets:
    # If we are local, reasoning_engine might find .env, so we can try-except the import
    pass

try:
    from reasoning_engine import generate_sparql, execute_sparql, generate_answer
except ValueError as e:
    st.error("🚨 **Deployment Error: Google API Key Missing**")
    st.warning("Please configure your Secrets in Streamlit Cloud Settings.")
    st.code('GOOGLE_API_KEY = "AIzaSy..."', language="toml")
    st.info("Go to 'Manage app' > 'Settings' > 'Secrets' and paste your key.")
    st.stop()

from graph_loader import load_graph, generate_schema_info
from visualize_graph import visualize_ontology

# Page Config
st.set_page_config(page_title="Math Ontology Bot", layout="wide")

# Paths
TBOX_PATH = "data/ontology/math_tbox.ttl"
DATA_PATH = "data/knowledge_graph/math_abox.ttl"
VISUALIZATION_PATH = "math_graph.html"

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "graph_loaded" not in st.session_state:
    st.session_state.graph_loaded = False
if "viz_html" not in st.session_state:
    st.session_state.viz_html = None

# Sidebar
with st.sidebar:
    st.header("🤖 Math Bot Config")
    st.write("Ontology grounded high school math tutor.")
    
    if st.button("Reload Knowledge Graph"):
        st.session_state.graph_loaded = False
        st.session_state.viz_html = None # Reset visualization
        st.experimental_rerun()

    st.divider()
    st.subheader("Visualization")
    
    # Priority: 1. Dynamic HTML (from session), 2. Static File
    if st.session_state.viz_html:
        st.components.v1.html(st.session_state.viz_html, height=300, scrolling=True)
        st.caption("Dynamic Context Visualization")
    elif os.path.exists(VISUALIZATION_PATH):
        with open(VISUALIZATION_PATH, 'r', encoding='utf-8') as f:
            html_data = f.read()
        st.components.v1.html(html_data, height=300, scrolling=True)
        st.caption("Mini-map of the Ontology")
    else:
        st.error("Visualization file not found.")

# Main Load Logic
@st.cache_resource
def get_graph_data():
    g = load_graph(DATA_PATH)
    t = load_graph(TBOX_PATH)
    full_g = g + t
    schema = generate_schema_info(full_g)
    return full_g, schema

try:
    full_graph, schema_info = get_graph_data()
    st.session_state.graph_loaded = True
except Exception as e:
    st.error(f"Failed to load graph: {e}")
    st.stop()

# Title
st.title("📐 Math Ontology Chatbot")
st.caption("Ask about High School Math concepts! (e.g. 'Taylor Series', 'Calculus Prerequisites')")

# Chat UI
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "evidence" in msg and msg["evidence"]:
            with st.expander("🔍 Evidence (Used Concepts)"):
                st.json(msg["evidence"])

if prompt := st.chat_input("Ask a math question..."):
    # User Message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Thinking...
    with st.spinner("Analyzing Ontology..."):
        # 1. Reasoning
        sparql_res = generate_sparql(prompt, schema_info)
        
        # 2. Execution
        db_data = []
        if sparql_res and "query" in sparql_res and sparql_res["query"]:
             db_data = execute_sparql(sparql_res["query"], full_graph)
        
        # 3. Answer Generation
        final_res = generate_answer(prompt, db_data, sparql_res.get("explanation", ""))
        
        answer_text = final_res.get("answer", "No answer generated.")
        evidence_data = final_res.get("evidence", [])
        
        # 4. Update Visualization (Highlighting)
        if evidence_data:
            highlight_nodes = []
            for item in evidence_data:
                # Add Concept/Subject/Chapter labels to highlight list
                if item.get("concept"): highlight_nodes.append(item["concept"])
                if item.get("chapter"): highlight_nodes.append(item["chapter"])
                if item.get("subject"): highlight_nodes.append(item["subject"])
            
            # Generate new HTML with highlights
            try:
                new_html = visualize_ontology(graph=full_graph, highlight_labels=highlight_nodes, return_html_str=True)
                st.session_state.viz_html = new_html
            except Exception as e:
                print(f"Visualization Error: {e}")

    # Assistant Message
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": answer_text,
        "evidence": evidence_data
    })
    
    with st.chat_message("assistant"):
        st.markdown(answer_text)
        if evidence_data:
            with st.expander("🔍 Evidence (Ontology Trace)"):
                st.table(evidence_data) # Use Table for cleaner view than JSON
                st.caption(f"Logic: {sparql_res.get('explanation', '')}")
            
    # Rerun to update sidebar immediately
    st.rerun()
