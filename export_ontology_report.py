import rdflib
from rdflib import Namespace, RDF, RDFS
import os

# Configuration
INPUT_FILE = "data/knowledge_graph/math_abox.ttl"
HIERARCHY_FILE = "data/report/hierarchy_report.md"
PREREQ_FILE = "data/report/prerequisites_report.md"

# Namespaces
NS = Namespace("http://math.bot/ontology/")

def export_reports():
    print(f"[INFO] Loading {INPUT_FILE}...")
    g = rdflib.Graph()
    g.parse(INPUT_FILE, format="turtle")
    
    # Ensure raw directory exists
    os.makedirs("data/report", exist_ok=True)

    # --- 1. Export Hierarchy ---
    print(f"[INFO] Generating {HIERARCHY_FILE}...")
    with open(HIERARCHY_FILE, "w", encoding="utf-8") as f:
        f.write("# Ontology Hierarchy Report\n")
        f.write("Please edit this file to correct any structure errors.\n")
        f.write("Format: \n- Subject\n  - Chapter\n    - Section\n      - #Concept\n\n")
        
        # Get Subjects
        subjects = []
        for s in g.subjects(RDF.type, NS.Subject):
            label = g.value(s, RDFS.label)
            subjects.append((s, str(label)))
        
        # Sort subjects logic (naive sort by label or URI)
        subjects.sort(key=lambda x: x[1]) 

        for sub_uri, sub_label in subjects:
            f.write(f"- {sub_label}\n")
            
            # Get Chapters
            chapters = []
            for o in g.objects(sub_uri, NS.hasChapter):
                label = g.value(o, RDFS.label)
                chapters.append((o, str(label)))
            chapters.sort(key=lambda x: x[1])

            for chap_uri, chap_label in chapters:
                f.write(f"  - {chap_label}\n")
                
                # Get Sections
                sections = []
                for o in g.objects(chap_uri, NS.hasSection):
                    label = g.value(o, RDFS.label)
                    sections.append((o, str(label)))
                sections.sort(key=lambda x: x[1])

                for sec_uri, sec_label in sections:
                    f.write(f"    - {sec_label}\n")
                    
                    # Get Concepts
                    concepts = []
                    for o in g.objects(sec_uri, NS.hasConcept):
                        label = g.value(o, RDFS.label)
                        concepts.append((o, str(label)))
                    concepts.sort(key=lambda x: x[1])

                    for con_uri, con_label in concepts:
                        f.write(f"      - #{con_label}\n")

    # --- 2. Export Prerequisites ---
    print(f"[INFO] Generating {PREREQ_FILE}...")
    with open(PREREQ_FILE, "w", encoding="utf-8") as f:
        f.write("# Prerequisite Relationships\n")
        f.write("Format: Preconcept -> Postconcept\n\n")
        
        prereqs = []
        for s, p, o in g.triples((None, NS.prerequisiteOf, None)):
            pre_label = g.value(s, RDFS.label)
            post_label = g.value(o, RDFS.label)
            if pre_label and post_label:
                prereqs.append(f"{pre_label} -> {post_label}")
        
        prereqs.sort()
        for link in prereqs:
            f.write(f"- {link}\n")

    print("[SUCCESS] Reports generated.")

if __name__ == "__main__":
    export_reports()
