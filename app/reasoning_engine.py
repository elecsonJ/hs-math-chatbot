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
MODEL_NAME = "gemini-3-flash-preview"
model = genai.GenerativeModel(MODEL_NAME, generation_config={"response_mime_type": "application/json"})

def generate_sparql(question, schema_info):
    prompt = f"""
    You are an expert Math Ontology Engineer.
    Your task is to convert a natural language question into a SPARQL query.
    
    ### Ontology Schema (TBox)
    {schema_info}
    
    ### Guidelines
    1. **Context**: The Ontology ONLY contains **High School Math** concepts.
    2. **Concept Mapping**:
       - High School Concept: Query directly.
       - University/Advanced Concept: **INFER** high school prerequisites (e.g., "Taylor Series" -> "Series|Differentiation") and query those.
    
    3. **Out-of-Curriculum Detection (NEW)**:
       - If the user asks about a concept that is NOT in the High School curriculum:
       - **You MUST include the exact phrase "OUT_OF_CURRICULUM" in your `explanation` field.**
       - **CRITICAL**: You MUST still generate a SPARQL query to retrieve relevant high school prerequisites. Do NOT return an empty query.
    
    4. **Output Goal**: Retrieve `Label`, `Subject`, `Chapter`. 
       - Use `FILTER(regex(?label, "Term1|Term2", "i"))`.
       - If the term might have synonyms, include them in the regex (e.g. "미분계수|순간변화율").
       - **ALWAYS use the prefix**: `PREFIX : <http://snu.ac.kr/math/>`
    
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
    Checks if the concept is out of curriculum based on sparql_explanation.
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
    1. **Analyze**: Carefully evaluate the retrieved data (Concepts, Prerequisites, etc.) and the provided Logic string.
    
    2. **Scope & Ambiguity Check (CRITICAL)**:
       - **Case A: Out of Curriculum** (Logic contains "OUT_OF_CURRICULUM"):
         - Start answer with: "교육과정 외의 내용입니다."
         - Explain that the concept is advanced and link it to the retrieved High School prerequisites.
         - **MUST provide the 'evidence' list** containing those prerequisites.
       
       - **Case B: Concept Ambiguity** (Same Name, Different Depth):
         - If the user asks about a concept (e.g., "Continuous Probability Distribution", "Matrix") that exists in High School but implies a University-level depth (e.g., "Is this all?", "General definition"):
         - **Do NOT** simply say "Study the high school version."
         - Explicitly clarify: "고등학교 과정에서는 ~만 다루지만, 대학 과정에서는 ~까지 확장됩니다." (Distinguish the scope).
         - Then, guide them to the High School concepts available in the ontology.

    3. **Answer Style & Language**: 
       - **Language**: Write the entire 'answer' in **Korean**.
       - **Tone**: Maintain an encouraging, empathetic, and helpful mentor persona.
       - **Guidance**: Use the `Retrieved Knowledge` to suggest which high school foundations the student should review.
    
    4. **Evidence Construction**:
       - Create an 'evidence' list based strictly on the 'Retrieved Knowledge'.
       - **IMPORTANT**: Even if the concept is "Out of Curriculum" or "Ambiguous", you MUST list the retrieved related concepts in `evidence` so they can be visualized.
       - Map the data to: subject, chapter, concept, and desc (short reason for relevance).
       - If hierarchy info (subject/chapter) is missing, do NOT infer it. STRICTLY use "Unknown" or "None".
       
    ### Output Format (JSON)
    Strictly adhere to this Typescript Interface:
    interface Response {{
        answer: string; // Must start with "교육과정 외의 내용입니다." if applicable.
        evidence: {{
            subject: string;
            chapter: string;
            concept: string;
            desc?: string; // e.g., "Prerequisite for this advanced topic"
        }}[];
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result
    except Exception as e:
        print(f"[ERROR] Answer Generation Failed: {e}")
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
