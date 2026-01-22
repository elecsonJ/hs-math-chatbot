import rdflib
from rdflib import Namespace, RDFS, Literal

# Configuration
INPUT_PROP_FILE = "data/raw/properties.md"
ABOX_FILE = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://math.bot/ontology/")

def enrich_ontology():
    print(f"[INFO] Loading {ABOX_FILE}...")
    g = rdflib.Graph()
    g.parse(ABOX_FILE, format="turtle")
    
    print(f"[INFO] Reading {INPUT_PROP_FILE}...")
    with open(INPUT_PROP_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Mapping properties by subject name
    # Format: SubjectName -> Grade, Classification
    subj_props = {}
    
    for line in lines:
        line = line.strip()
        if not line or "->" not in line:
            continue
            
        # Example: 공통수학1 -> 1학년 1학기, 공통
        parts = line.split("->")
        subj_name = parts[0].strip()
        props_part = parts[1].strip()
        
        # Split props by comma
        props = [p.strip() for p in props_part.split(",")]
        if len(props) >= 2:
            grade = props[0]
            classification = props[1]
            subj_props[subj_name] = {"grade": grade, "classification": classification}
            
    print(f"[INFO] Found properties for {len(subj_props)} subjects.")
    
    # Assign to Ontology
    updated_count = 0
    # Iterate all Subjects in Graph
    for s, p, o in g.triples((None, rdflib.RDF.type, NS.Subject)):
        label = str(g.value(s, RDFS.label))
        
        if label in subj_props:
            props = subj_props[label]
            g.add((s, NS.grade, Literal(props["grade"])))
            g.add((s, NS.classification, Literal(props["classification"])))
            print(f"[UPDATE] {label}: Grade='{props['grade']}', Class='{props['classification']}'")
            updated_count += 1
        else:
            print(f"[WARN] Subject '{label}' not found in properties file.")
            
    print(f"[INFO] Updated {updated_count} subjects.")
    print(f"[INFO] Saving to {ABOX_FILE}...")
    g.serialize(destination=ABOX_FILE, format="turtle")
    print("[SUCCESS] Done.")

if __name__ == "__main__":
    enrich_ontology()
