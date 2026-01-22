import google.generativeai as genai
import os
from dotenv import load_dotenv
import rdflib
import json

# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini Model
MODEL_NAME = "gemini-2.0-flash-exp" 
model = genai.GenerativeModel(MODEL_NAME, generation_config={"response_mime_type": "application/json"})

def generate_sparql(question, schema_info):
    """
    Generates a SPARQL query based on the user's question and schema info.
    Goal: Retrieve relevant concepts and their prerequisites/relationships.
    """
    
    prompt = f"""
    You are an expert Math Ontology Engineer.
    Your task is to convert a natural language question into a SPARQL query to retrieve relevant math concepts and their prerequisites.
    
    ### Ontology Schema (TBox)
    {schema_info}
    
    ### Guidelines
    1. **Context**: The Ontology ONLY contains **High School Math** concepts.
    2. **Concept Mapping (CRITICAL)**:
       - If the user asks about a **High School Concept** (e.g., "미분계수", "합성함수"):
         -> In this case, just query for that concept directly as usual.
       - If the user asks about a **University/Advanced Concept** (e.g., "테일러 급수", "선형대수", "다변수 미분"):
         -> **DO NOT** query for "Taylor Series" (as it's not in the ontology).
         -> **INFER** the relevant High School prerequisites (e.g., "급수", "합성함수의 미분", "이계도함수").
         -> Query for **THOSE inferred concepts** using Regex OR (e.g., "Term1|Term2").
    
    3. **Output Goal**:
       - Retrieve the `Label`, `Subject`, `Chapter` of the concepts you identified.
    
    4. **Search Strategy**:
       - Use `FILTER(regex(?label, "Term1|Term2", "i"))`.
    
    ### Example 1 (High School Query)
    Question: "합성함수 미분이 뭐야?"
    Response:
    {{
        "query": "PREFIX : <http://snu.ac.kr/math/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?targetLabel ?targetSubject ?targetChapter WHERE {{ ?target a :Concept ; rdfs:label ?targetLabel . FILTER(regex(?targetLabel, '합성함수의 미분', 'i')) OPTIONAL {{ ?targetSection :hasConcept ?target . ?targetChapNode :hasSection ?targetSection . ?targetSubNode :hasChapter ?targetChapNode . ?targetSubNode rdfs:label ?targetSubject . ?targetChapNode rdfs:label ?targetChapter . }} }}",
        "explanation": "'합성함수의 미분'은 고교 과정에 있으므로 직접 검색합니다."
    }}
    
    ### Example 2 (University Query - Mapping)
    Question: "테일러 급수가 너무 어려워."
    Response:
    {{
        "query": "PREFIX : <http://snu.ac.kr/math/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?targetLabel ?targetSubject ?targetChapter WHERE {{ ?target a :Concept ; rdfs:label ?targetLabel . FILTER(regex(?targetLabel, '급수|합성함수의 미분|이계도함수', 'i')) OPTIONAL {{ ?targetSection :hasConcept ?target . ?targetChapNode :hasSection ?targetSection . ?targetSubNode :hasChapter ?targetChapNode . ?targetSubNode rdfs:label ?targetSubject . ?targetChapNode rdfs:label ?targetChapter . }} }}",
        "explanation": "'테일러 급수'는 온톨로지에 없으므로, 이를 이해하기 위해 필요한 고교 과정인 '급수', '합성함수의 미분', '이계도함수'를 검색합니다."
    }}
    
    ### User Question
    {question}
    
    ### Response
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result
    except Exception as e:
        print(f"[ERROR] SPARQL Generation Failed: {e}")
        return {"query": "", "explanation": f"Error: {e}"}

def execute_sparql(query, graph):
    """
    Executes the SPARQL query on the given graph.
    """
    try:
        results = graph.query(query)
        data = []
        for row in results:
            item = {}
            for var in results.vars:
                val = row[var]
                item[str(var)] = str(val) if val is not None else None
            data.append(item)
        return data
    except Exception as e:
        print(f"[ERROR] SPARQL Execution Failed: {e}")
        return []

def generate_answer(question, raw_data, sparql_explanation):
    """
    Generates a structured JSON answer with 'answer' and 'evidence'.
    """
    
    data_summary = json.dumps(raw_data, ensure_ascii=False) if raw_data else "No data found."
    
    prompt = f"""
    You are a Math Mentor Chatbot.
    
    ### User Question
    {question}
    
    ### Retrieved Knowledge (SPARQL Results)
    {data_summary}
    (Logic: {sparql_explanation})
    
    ### Instructions
    1. **Analyze**: Look at the retrieved data (Concepts, Prerequisites, etc.).
    2. **Answer**: Write a helpful, empathetic response in Korean. 
       - If the user asks about a difficult concept, explain it briefly and suggest checking the prerequisites found in the data.
    3. **Evidence**: Construct a list of evidence based strictly on the 'Retrieved Knowledge'.
       - Map the data to: subject, chapter, concept. 
       - If specific hierarchy info (subject/chapter) is missing in data, infer or leave as "Unknown".
       
    ### Output Format (JSON)
    Or strictly strictly adhere to this Typescript Interface:
    interface Response {{
       answer: string; // The main chat message
       evidence: {{
           subject: string;
           chapter: string;
           concept: string;
           desc?: string; // Short reason why this is relevant (e.g. "Prerequisite")
       }}[];
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        # Ensure it parses
        result = json.loads(text)
        return result
    except Exception as e:
        return {
            "answer": f"답변 생성 중 오류가 발생했습니다. ({e})",
            "evidence": []
        }

if __name__ == "__main__":
    # Test Block
    from graph_loader import load_graph, generate_schema_info
    
    # Updated Paths
    TBOX_PATH = "/Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto/data/ontology/math_tbox.ttl"
    DATA_PATH = "/Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto/data/knowledge_graph/math_abox.ttl"
    
    print("Loading Graph...")
    g = load_graph(DATA_PATH)
    tbox = load_graph(TBOX_PATH)
    full_graph = g + tbox
    
    # Extract Schema
    schema = generate_schema_info(full_graph)
    
    # Test Question
    test_q = "테일러 급수가 너무 어려워. 고등학교 때 뭘 공부했어야 하지?"
    print(f"\n[Question] {test_q}")
    
    # 1. Gen SPARQL
    sparql_res = generate_sparql(test_q, schema)
    print(f"[SPARQL] {sparql_res['query']}")
    
    # 2. Execute
    db_res = execute_sparql(sparql_res['query'], full_graph)
    print(f"[DB Result] {len(db_res)} rows found.")
    
    # 3. Gen Answer
    final_json = generate_answer(test_q, db_res, sparql_res['explanation'])
    print("\n[Final JSON]")
    print(json.dumps(final_json, indent=2, ensure_ascii=False))
