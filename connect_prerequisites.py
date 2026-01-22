import rdflib
from rdflib import Namespace, RDF, RDFS, Literal

# Configuration
FILE_PATH = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://snu.ac.kr/math/")

def connect_prerequisites():
    print(f"[INFO] Loading {FILE_PATH}...")
    g = rdflib.Graph()
    g.parse(FILE_PATH, format="turtle")
    
    # Helper to find URI by Label
    def find_concept(label_name):
        for s, p, o in g.triples((None, RDF.type, NS.Concept)):
            label = g.value(s, RDFS.label)
            if label and str(label) == label_name:
                return s
        return None

    # Helper to connect
    def connect(parent_label, child_label):
        parent_uri = find_concept(parent_label)
        child_uri = find_concept(child_label)
        
        if not parent_uri: return # Silent fail for cleaner output or use print for debug
        if not child_uri: return
            
        g.add((parent_uri, NS.prerequisiteOf, child_uri))
        print(f"[LINK] {parent_label} -> {child_label}")

    print("\n[INFO] Linking Full Curriculum...")

    # --- 1. Common Math 1 (Basics) ---
    connect("다항식의 덧셈과 뺄셈", "다항식의 곱셈")
    connect("다항식의 곱셈", "곱셈공식")
    connect("곱셈공식", "인수분해")
    connect("나머지정리", "인수분해")
    connect("복소수", "이차방정식") # Roots can be complex
    connect("인수분해", "이차방정식") # Solving via factoring
    connect("이차방정식", "이차방정식과 이차함수의 관계")
    connect("이차방정식", "여러 가지 방정식") # Higher order equations
    connect("일차부등식", "이차부등식")

    # --- 2. Common Math 2 (Sets & Functions) ---
    connect("집합의 뜻과 표현", "집합의 연산")
    connect("집합의 연산", "명제")
    connect("집합의 연산", "함수") # Domain/Range are sets
    connect("함수", "합성함수")
    connect("함수", "역함수")
    connect("유리식", "유리함수")
    connect("무리식", "무리함수")
    
    # --- 3. Algebra (Su-1: Exp/Log, Trig, Seq) ---
    # Exp/Log
    connect("거듭제곱", "지수")
    connect("지수", "로그")
    connect("지수", "지수함수")
    connect("로그", "로그함수")
    connect("지수함수", "지수함수의 방부등식")
    connect("로그함수", "로그함수의 방부등식")
    
    # Trig
    connect("일반각", "삼각함수")
    connect("삼각함수", "삼각함수의 그래프")
    connect("삼각함수의 그래프", "삼각함수 방부등식")
    connect("삼각함수", "사인법칙")
    connect("삼각함수", "코사인법칙")
    
    # Sequences
    connect("등차수열", "등차수열의 합")
    connect("등비수열", "등비수열의 합")
    connect("시그마", "여러가지 수열의 합")
    connect("등차수열", "수학적 귀납법") # Logic flow

    # --- 4. Calculus 1 (Su-2: Poly Calculus) ---
    # Basics
    connect("함수", "함수의 극한") # Function concept is prereq for limit
    connect("함수의 극한", "함수의 연속")
    connect("함수의 연속", "미분계수")
    connect("미분계수", "도함수")
    connect("도함수", "접선의 방정식")
    connect("도함수", "함수의 극대와 극소")
    connect("도함수", "부정적분")
    connect("부정적분", "정적분")
    connect("정적분", "정적분의 활용")

    # --- 5. Probability & Statistics ---
    connect("경우의 수", "순열")
    connect("순열", "조합")
    connect("조합", "이항정리")
    connect("순열", "확률의 뜻")
    connect("조합", "확률의 뜻")
    connect("확률의 뜻", "조건부확률")
    connect("확률의 뜻", "확률분포")
    connect("확률분포", "정규분포")
    connect("정규분포", "통계적 추정")

    # --- 6. Calculus 2 (Transcendental) ---
    connect("수열", "수열의 극한") # Algebra Seq -> Calc2 Seq Limit
    connect("수열의 극한", "급수")
    connect("지수함수", "지수함수와 로그함수의 미분")
    connect("로그함수", "지수함수와 로그함수의 미분")
    connect("삼각함수", "삼각함수의 미분")
    connect("도함수", "여러 가지 미분법") # Synthetic (Chain rule etc from Calc 1 base)
    connect("여러 가지 미분법", "도함수의 활용") # Advanced application
    connect("정적분", "여러 가지 함수의 적분")
    connect("여러 가지 미분법", "치환적분법과 부분적분법") # Reverse chain/product rule

    # --- 7. Geometry ---
    connect("이차방정식", "이차곡선") # Quadratic eqs basis
    connect("이차곡선", "이차곡선의 접선")
    connect("벡터의 뜻", "벡터의 연산")
    connect("벡터의 연산", "벡터의 성분과 내적")
    connect("공간도형", "공간좌표")
    connect("공간좌표", "도형의 방정식") # Space equations

    # --------------------------------------------------
    
    print(f"\n[INFO] Saving updated graph to {FILE_PATH}...")
    g.serialize(destination=FILE_PATH, format="turtle")
    print("[SUCCESS] Done.")

if __name__ == "__main__":
    connect_prerequisites()
