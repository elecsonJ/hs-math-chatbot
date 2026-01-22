import re
import rdflib
from rdflib import Namespace, RDF, RDFS, Literal

# Configuration
INPUT_FILE = "data/raw/curr.md"
OUTPUT_FILE = "data/knowledge_graph/math_abox.ttl"

# Namespaces
NS = Namespace("http://math.bot/ontology/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

def generate_skeleton():
    g = rdflib.Graph()
    g.bind("", NS)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)

    # State variables
    current_subject = None
    current_chapter = None
    
    # Counters for unique IDs
    sub_count = 0
    chap_count = 0
    sec_count = 0
    con_count = 0
    
    print(f"[INFO] Reading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Skip top-level categories indicated by '-' if they are just grouping headers
        # But wait, looking at file, '- 미적' is followed by '미적분1'. 
        # '- 대수' followed by '대수'.
        # Let's ignore lines starting with '-' for now and focus on the explicit subjects below them?
        # Or maybe treating them as comments.
        if line.startswith("-"):
            continue

        # Check for Chapter: "Name (N단원)"
        chapter_match = re.search(r"(.*)\s*\((\d+)단원\)", line)
        
        # Check for Section/Concepts: has "#"
        if "#" in line:
            # It is a Section line with Concepts
            parts = line.split("#")
            section_name = parts[0].strip()
            concepts = [c.strip() for c in parts[1:] if c.strip()]
            
            if not current_chapter:
                print(f"[WARN] Skipping Section '{section_name}' because no Chapter is set.")
                continue
                
            # Create Section
            sec_count += 1
            sec_uri = NS[f"Sec_{sec_count:03d}"]
            g.add((sec_uri, RDF.type, NS.Section))
            g.add((sec_uri, RDFS.label, Literal(section_name)))
            g.add((current_chapter, NS.hasSection, sec_uri))
            
            # Create Concepts
            for con_name in concepts:
                con_count += 1
                con_uri = NS[f"Con_{con_count:04d}"]
                g.add((con_uri, RDF.type, NS.Concept))
                g.add((con_uri, RDFS.label, Literal(con_name)))
                g.add((sec_uri, NS.hasConcept, con_uri))
                
        elif chapter_match:
            # It is a Chapter
            chapter_name = chapter_match.group(1).strip()
            
            if not current_subject:
                 # Fallback if file starts with chapter? unlikely based on file
                 print(f"[WARN] Chapter '{chapter_name}' found without Subject.")
                 continue

            chap_count += 1
            chap_uri = NS[f"Chap_{chap_count:03d}"]
            current_chapter = chap_uri
            
            g.add((chap_uri, RDF.type, NS.Chapter))
            g.add((chap_uri, RDFS.label, Literal(chapter_name)))
            g.add((current_subject, NS.hasChapter, chap_uri))
            
        else:
            # Must be a Subject
            # Exclude lines that are likely garbage or headers like 'contents'
            if line.lower() == "contents": continue
            
            sub_name = line
            sub_count += 1
            sub_uri = NS[f"Sub_{sub_count:02d}"]
            current_subject = sub_uri
            # Reset chapter? Depending on file structure, strictly speaking yes.
            # But chapters belong to subject.
            
            g.add((sub_uri, RDF.type, NS.Subject))
            g.add((sub_uri, RDFS.label, Literal(sub_name)))
            print(f"[PARSER] Found Subject: {sub_name}")

    print(f"[INFO] Genereated {len(g)} triples.")
    print(f"Subjects: {sub_count}, Chapters: {chap_count}, Sections: {sec_count}, Concepts: {con_count}")
    
    # Serialize
    g.serialize(destination=OUTPUT_FILE, format="turtle")
    print(f"[SUCCESS] Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_skeleton()
