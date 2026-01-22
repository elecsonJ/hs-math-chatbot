import os

OLD_URI = "http://snu.ac.kr/math/"
NEW_URI = "http://math.bot/ontology/"

# List obtained from grep search
files_to_check = [
    "data/ontology/math_tbox.ttl",
    "data/knowledge_graph/math_abox.ttl",
    "visualize_graph.py",
    "app/reasoning_engine.py",
    "export_ontology_report.py",
    "connect_prerequisites.py",
    "verify_connections.py",
    "import_hierarchy_report.py",
    "import_curriculum.py",
    "import_proposed_additions.py",
    "enrich_ontology.py",
    "app/graph_loader.py",
    # Include previous versions just to be clean
    "data/knowledge_graph/math_abox_prev.ttl",
    "data/ontology/math_tbox_prev.ttl",
    "data/knowledge_graph/math_abox_prev_v2.ttl",
    "data/ontology/math_tbox_prev_v2.ttl"
]

files_changed = []

print(f"Starting Refactor: '{OLD_URI}' -> '{NEW_URI}'")

for file_path in files_to_check:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if OLD_URI in content:
                new_content = content.replace(OLD_URI, NEW_URI)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                files_changed.append(file_path)
                print(f"[UPDATED] {file_path}")
            else:
                print(f"[SKIPPED] {file_path}")
        except Exception as e:
            print(f"[ERROR] Could not process {file_path}: {e}")
    else:
        print(f"[MISSING] {file_path}")

print(f"\nTotal files updated: {len(files_changed)}")
