import rdflib
from rdflib import Namespace, RDF, RDFS, Literal
import re

# Configuration
INPUT_FILE = "data/report/proposed_additions.md"
GRAPH_FILE = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://math.bot/ontology/")

def import_additions():
    print(f"[INFO] Loading {GRAPH_FILE}...")
    g = rdflib.Graph()
    g.parse(GRAPH_FILE, format="turtle")
    
    # Helper to find URI by Label
    def find_concept(label_name):
        label_name = label_name.strip()
        for s, p, o in g.triples((None, RDF.type, NS.Concept)):
            label = g.value(s, RDFS.label)
            if label and str(label) == label_name:
                return s
        return None

    print(f"[INFO] Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    added_count = 0
    
    for line in lines:
        if "->" not in line: 
            # print(f"[DEBUG] Skipping line (no arrow): {line.strip()}")
            continue
        
        # Parse: "- [ ] Concept A -> Concept B (comment)"
        # Regex to capture Concept A and Concept B
        # Expected format:  - [ ] A -> B ...
        # Or just: - A -> B
        
        # Remove list marker and checkbox "- [ ]" or just "-"
        cleaned = re.sub(r'^\s*-\s*(\[.*?\])?\s*', '', line)
        # print(f"[DEBUG] Cleaned line: '{cleaned}'")
        
        # Split by arrow (maxsplit=1 to handle arrows in comments)
        parts = cleaned.split("->", 1)
        if len(parts) < 2: 
            print(f"[DEBUG] Skipping line (split fail): '{cleaned}'")
            continue
        
        pre_text = parts[0].strip()
        post_text = parts[1]
        
        # Remove comments in parentheses from pre_text and post_text
        pre_text = re.sub(r'\(.*?\)', '', pre_text).strip()
        post_text = re.sub(r'\(.*?\)', '', post_text).strip()
        
        pre_uri = find_concept(pre_text)
        post_uri = find_concept(post_text)
        
        if pre_uri and post_uri:
            g.add((pre_uri, NS.prerequisiteOf, post_uri))
            print(f"[ADD] {pre_text} -> {post_text}")
            added_count += 1
        else:
            if not pre_uri: print(f"[WARN] Pre-concept '{pre_text}' not found in ontology.")
            if not post_uri: print(f"[WARN] Post-concept '{post_text}' not found in ontology.")

    print(f"[INFO] Added {added_count} new prerequisite links.")
    
    print(f"[INFO] Saving to {GRAPH_FILE}...")
    g.serialize(destination=GRAPH_FILE, format="turtle")
    print("[SUCCESS] Done.")

if __name__ == "__main__":
    import_additions()
