import rdflib
from rdflib import Namespace, RDF, RDFS, Literal

# Configuration
FILE_PATH = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://math.bot/ontology/")

def connect_prerequisites():
    print(f"[INFO] Loading {FILE_PATH}...")
    g = rdflib.Graph()
    g.parse(FILE_PATH, format="turtle")
    
    # Helper to find URI by Label (Prioritize Section -> Concept -> others)
    def find_node(label_name):
        # Strict Section Search as requested
        for s, p, o in g.triples((None, RDF.type, NS.Section)):
            if str(g.value(s, RDFS.label)) == label_name:
                return s
        return None

    # Helper to connect
    def connect(parent_label, child_label):
        parent_uri = find_node(parent_label)
        child_uri = find_node(child_label)
        
        if not parent_uri: 
            print(f"[WARN] Parent Section '{parent_label}' not found.")
            return
        if not child_uri:
            print(f"[WARN] Child Section '{child_label}' not found.")
            return
            
        if (parent_uri, NS.prerequisiteOf, child_uri) in g:
            return

        g.add((parent_uri, NS.prerequisiteOf, child_uri))
        print(f"[LINK] {parent_label} -> {child_label}")

    print("\n[INFO] Linking Full Curriculum (Section Only)...")

    # --- 1. Common Math 1 (Basics) ---
    connect("다항식의 연산", "인수분해")
    connect("나머지정리", "인수분해")
    connect("복소수", "이차방정식")
    connect("인수분해", "이차방정식")
    connect("이차방정식", "이차방정식과 이차함수")
    connect("이차방정식", "여러 가지 방정식")

    # --- 2. Common Math 2 (Sets & Functions) ---
    connect("집합의 뜻과 포함 관계", "집합의 연산")
    connect("집합의 연산", "명제")
    connect("집합의 연산", "함수")
    # connect("함수", "합성함수") # Removed: Internal
    # connect("함수", "역함수") # Removed: Internal
    connect("유리함수", "무리함수") # Often taught in sequence

    # --- 3. Algebra (Su-1) ---
    connect("지수", "로그")
    connect("지수", "지수함수")
    connect("로그", "로그함수")
    
    # Trig
    connect("삼각함수", "삼각함수의 그래프")
    connect("삼각함수의 그래프", "삼각함수의 활용") 
    
    # Sequences
    connect("등차수열과 등비수열", "수열의 합")
    connect("등차수열과 등비수열", "수학적 귀납법")

    # --- 4. Calculus 1 (Su-2) ---
    connect("함수", "함수의 극한")
    connect("함수의 극한", "함수의 연속")
    connect("함수의 연속", "미분계수와 도함수")
    connect("미분계수와 도함수", "도함수의 활용")
    connect("도함수의 활용", "부정적분")
    connect("부정적분", "정적분")
    connect("정적분", "정적분의 활용")

    # --- 5. Probability & Statistics ---
    # Common 1 -> ProbStat
    connect("경우의 수와 순열", "조합") 
    connect("경우의 수와 순열", "순열과 조합") # Common1 -> ProbStat linkage
    
    # Internal
    connect("순열과 조합", "이항정리")
    connect("순열과 조합", "확률의 뜻과 활용")
    connect("확률의 뜻과 활용", "조건부확률")
    connect("확률의 뜻과 활용", "확률분포")
    connect("확률분포", "통계적 추정")
    
    # Cross-Subject
    connect("집합의 뜻과 포함 관계", "확률의 뜻과 활용") 
    connect("정적분", "확률분포")

    # --- 6. Calculus 2 ---
    connect("등차수열과 등비수열", "수열의 극한")
    connect("수열의 극한", "급수")
    connect("지수함수", "지수함수와 로그함수의 미분")
    connect("로그함수", "지수함수와 로그함수의 미분")
    connect("삼각함수", "삼각함수의 미분")
    connect("미분계수와 도함수", "여러 가지 미분법") 
    connect("여러 가지 미분법", "도함수의 활용") 
    connect("정적분", "여러 가지 함수의 적분")
    connect("여러 가지 미분법", "치환적분법과 부분적분법")

    # --- 7. Geometry ---
    connect("이차방정식", "이차곡선") 
    connect("이차곡선", "이차곡선의 접선")
    connect("벡터의 연산", "벡터의 성분과 내적")
    
    # Cross-Subject
    connect("평면좌표", "공간좌표")    
    connect("원의 방정식", "공간좌표") 
    connect("직선의 방정식", "공간도형") 
    
    connect("공간도형", "공간좌표")
    connect("공간좌표", "도형의 방정식") 

    # --------------------------------------------------
    
    print(f"\n[INFO] Saving updated graph to {FILE_PATH}...")
    g.serialize(destination=FILE_PATH, format="turtle")
    print("[SUCCESS] Done.")

if __name__ == "__main__":
    connect_prerequisites()
