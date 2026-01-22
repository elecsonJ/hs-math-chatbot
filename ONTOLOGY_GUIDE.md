# 수학 온톨로지(Knowledge Graph) 작성 가이드

이 문서는 수학 챗봇이 사용하는 **지식 그래프(Knowledge Graph)** 데이터를 작성하는 방법을 설명합니다.
데이터는 **Turtle(.ttl)** 형식을 사용합니다.

## 1. 파일 구조
- **TBox (Schema)**: `data/ontology/math_tbox.ttl`
    - 데이터의 "뼈대"를 정의합니다 (과목, 단원, 개념이라는 '틀'과 관계들).
    - *이 파일은 자주 수정할 필요가 없습니다.*
- **ABox (Data)**: `data/knowledge_graph/math_abox.ttl`
    - 실제 수학 데이터(내용)가 들어갑니다.
    - *선생님께서 주로 작성하게 될 파일입니다.*

---

## 2. 기본 문법 (Turtle)
- `prefix`: 주소 줄임말입니다. `:이름` 처럼 간단하게 쓰기 위함입니다.
- `;` (세미콜론): 주어가 같을 때 속성을 계속 나열할 때 씁니다.
- `.` (마침표): 문장이 끝날 때 찍습니다.
- `#`: 주석(설명)입니다. 컴퓨터는 읽지 않습니다.

---

## 3. **[중요] 작성 원칙 (High School Only)**
이 온톨로지는 **고등학교 교육과정**만 담아야 합니다.
- **대학 수학 내용(예: 테일러 급수, 다변수 미분)은 절대 추가하지 마세요.**
- 사용자가 대학 내용을 물어보면, 챗봇 엔진이 알아서 "관련된 고교 기초 개념"을 찾아서 답변하도록 설계되어 있습니다.
- 따라서 선생님께서는 **고등학교 1학년 ~ 3학년(미적분/기하/확통 등)** 내용만 충실히 채워주시면 됩니다.

---

## 4. 데이터 입력 방법 (ABox 작성법)

### 단계 1: 과목/단원 정의하기
먼저 개념이 속할 큰 주소를 만듭니다. (이미 있는 경우 건너뜀)

```turtle
# 과목 (Subject)
:Sub_Math2 a :Subject ; 
    rdfs:label "수학II" ;        # 화면에 보일 이름
    :hasChapter :Chap_Diff2 .   # 포함하고 있는 대단원 연결

# 대단원 (Chapter)
:Chap_Diff2 a :Chapter ; 
    rdfs:label "미분" ;
    :hasSection :Sec_DiffCoeff . # 포함하고 있는 소단원 연결

# 소단원 (Section)
:Sec_DiffCoeff a :Section ;
    rdfs:label "미분계수와 도함수" .
```

### 단계 2: 개념(Concept) 추가하기
가장 중요한 부분입니다. 아이디(`:Con_...`)는 영문으로 유니크하게 짓고, `rdfs:label`에 한글 이름을 적습니다.

```turtle
:Con_DiffCoeff a :Concept ;
    rdfs:label "미분계수" .      # 학생이 검색할 키워드
```

### 단계 3: 소속 연결하기
위에서 만든 소단원에 이 개념을 등록합니다. **(소단원 쪽에 적어줍니다)**

```turtle
:Sec_DiffCoeff a :Section ;
    # ... 기존 내용 ...
    :hasConcept :Con_DiffCoeff, :Con_Derivative . # 쉼표(,)로 계속 연결 가능
```

### 단계 4: 선수 학습 관계 (Prerequisite) 연결하기 **(핵심)**
"이걸 배우려면 저게 필요해"라는 관계를 정의합니다.
문법: `A :prerequisiteOf B` (A는 B의 선수과목이다 = B를 하려면 A를 먼저 해야 한다)

```turtle
# 예시: 미분계수(A)를 알아야 도함수(B)를 할 수 있다.
:Con_DiffCoeff :prerequisiteOf :Con_Derivative .

# 예시: 함수의 극한(A)을 알아야 미분계수(B)를 할 수 있다.
:Con_Limit :prerequisiteOf :Con_DiffCoeff .
```

---

## 4. 실제 작성 예시 (행렬 추가하기)

만약 "행렬" 단원을 새로 추가한다면 다음과 같이 작성합니다.

```turtle
### 1. 단원 정의
:Sub_Geometry a :Subject ; rdfs:label "기하와 벡터" ;
    :hasChapter :Chap_Matrix .

:Chap_Matrix a :Chapter ; rdfs:label "행렬과 연산" ;
    :hasConcept :Con_MatrixDef, :Con_MatrixAdd .

### 2. 개념 정의
:Con_MatrixDef a :Concept ; rdfs:label "행렬의 뜻" .
:Con_MatrixAdd a :Concept ; rdfs:label "행렬의 덧셈" .

### 3. 관계 정의
# 행렬의 뜻을 알아야 덧셈을 할 수 있다
:Con_MatrixDef :prerequisiteOf :Con_MatrixAdd .
```
