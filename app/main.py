from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reasoning_engine import generate_sparql, execute_sparql, generate_answer
from graph_loader import load_graph, generate_schema_info

app = FastAPI()

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Graph ONCE at startup
print("Initializing Knowledge Graph...")
TBOX_PATH = "/Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto/data/ontology/math_tbox.ttl"
DATA_PATH = "/Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto/data/knowledge_graph/math_abox.ttl"

g = load_graph(DATA_PATH)
tbox = load_graph(TBOX_PATH)
full_graph = g + tbox
schema_info = generate_schema_info(full_graph)
print("Graph Initialized.")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_msg = request.message
        print(f"[User] {user_msg}")
        
        # 1. Reasoning
        sparql_res = generate_sparql(user_msg, schema_info)
        print(f"[SPARQL] {sparql_res.get('query')}")
        
        # 2. Execution
        if sparql_res.get('query'):
            db_res = execute_sparql(sparql_res['query'], full_graph)
            print(f"[DB] Found {len(db_res)} rows")
        else:
            db_res = []
            
        # 3. Answer Generation
        final_response = generate_answer(user_msg, db_res, sparql_res.get('explanation', ''))
        
        return final_response
            
    except Exception as e:
        print(f"[Error] {e}")
        return {
            "answer": "죄송합니다. 시스템 오류가 발생했습니다.",
            "evidence": []
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
