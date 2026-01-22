import re
import rdflib
from rdflib import Namespace, RDF, RDFS, Literal

# Configuration
INPUT_FILE = "data/report/hierarchy_report_v2.md"
OUTPUT_FILE = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://math.bot/ontology/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

def import_hierarchy():
    g = rdflib.Graph()
    g.bind("", NS)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # State variables
    current_subject = None
    current_chapter = None
    current_section = None
    
    # Counters for unique IDs
    sub_count = 0
    chap_count = 0
    sec_count = 0
    con_count = 0
    
    print(f"[INFO] Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("Please") or stripped.startswith("Format"):
            continue
            
        # Determine indentation level
        indent = len(line) - len(line.lstrip())
        content = stripped.lstrip("- ").strip()
        
        # Level 1: Subject (No indent usually, or small indent if user messed up, but let's assume standard 0 or 2 spaces)
        # Markdown lists:
        # - Subject
        #   - Chapter
        #     - Section
        #       - #Concept
        
        # We can use regex or simple indent counting. 
        # Approx: 0 spaces -> Subject, 2 spaces -> Chapter, 4 spaces -> Section, 6 spaces -> Concept
        # But report was:
        # - Subject
        #   - Chapter
        
        if content.startswith("#"):
            # It's a Concept! (Starts with #)
            con_name = content.lstrip("#").strip()
            if not current_section:
                 print(f"[WARN] Skipping Concept '{con_name}' - No parent Section.")
                 continue
                 
            con_count += 1
            con_uri = NS[f"Con_{con_count:04d}"]
            g.add((con_uri, RDF.type, NS.Concept))
            g.add((con_uri, RDFS.label, Literal(con_name)))
            g.add((current_section, NS.hasConcept, con_uri))
            
        elif indent < 2: 
            # Subject
            sub_name = content
            sub_count += 1
            sub_uri = NS[f"Sub_{sub_count:02d}"]
            current_subject = sub_uri
            current_chapter = None # Reset
            current_section = None
            
            g.add((sub_uri, RDF.type, NS.Subject))
            g.add((sub_uri, RDFS.label, Literal(sub_name)))
            
        elif indent < 4:
            # Chapter
            chap_name = content
            if not current_subject:
                print(f"[WARN] Skipping Chapter '{chap_name}' - No parent Subject.")
                continue
                
            chap_count += 1
            chap_uri = NS[f"Chap_{chap_count:03d}"]
            current_chapter = chap_uri
            current_section = None # Reset
            
            g.add((chap_uri, RDF.type, NS.Chapter))
            g.add((chap_uri, RDFS.label, Literal(chap_name)))
            g.add((current_subject, NS.hasChapter, chap_uri))
            
        else:
            # Section (Indent >= 4 but not starting with #)
            sec_name = content
            if not current_chapter:
                print(f"[WARN] Skipping Section '{sec_name}' - No parent Chapter.")
                continue
                
            sec_count += 1
            sec_uri = NS[f"Sec_{sec_count:03d}"]
            current_section = sec_uri
            
            g.add((sec_uri, RDF.type, NS.Section))
            g.add((sec_uri, RDFS.label, Literal(sec_name)))
            g.add((current_chapter, NS.hasSection, sec_uri))

    print(f"[INFO] Generated {len(g)} triples.")
    print(f"Subjects: {sub_count}, Chapters: {chap_count}, Sections: {sec_count}, Concepts: {con_count}")
    
    # Serialize
    g.serialize(destination=OUTPUT_FILE, format="turtle")
    print(f"[SUCCESS] Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    import_hierarchy()
