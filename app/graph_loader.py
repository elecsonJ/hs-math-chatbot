import rdflib
import os

def load_graph(file_path):
    """
    Load an RDF graph from a Turtle file.
    
    Args:
        file_path (str): The absolute path to the .ttl file.
        
    Returns:
        rdflib.Graph: The loaded RDF graph.
    """
    g = rdflib.Graph()
    try:
        g.parse(file_path, format="turtle")
        print(f"[INFO] Successfully loaded graph from {file_path}")
        print(f"[INFO] Graph scale: {len(g)} triples")
        return g
    except Exception as e:
        print(f"[ERROR] Failed to load graph: {e}")
        return None

def generate_schema_info(graph):
    """
    Extracts schema information (Classes, Properties) from the graph
    and returns it as a formatted string for LLM context.
    
    Args:
        graph (rdflib.Graph): The loaded RDF graph.
        
    Returns:
        str: Formatted schema information string.
    """
    
    # 1. Namespace Binding
    # Assuming standard prefixes, but we can extract namespaces if needed.
    # For simplicity, we hardcode the base namespace if it's consistent 
    # or extract it dynamically. Let's extract dynamically or use PREFIX definitions.
    
    schema_str = "### Ontology Schema Information ###\n\n"
    schema_str += "Prefixes:\n"
    schema_str += "@prefix : <http://snu.ac.kr/dining/> .\n"
    schema_str += "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    schema_str += "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    schema_str += "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    schema_str += "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"

    # 2. Extract Classes
    schema_str += "Classes:\n"
    # Query for all classes (rdf:type owl:Class)
    # Also considering RDFS classes if simple TBox
    query_classes = """
    SELECT DISTINCT ?cls
    WHERE {
        ?cls a owl:Class .
        FILTER(STRSTARTS(STR(?cls), "http://snu.ac.kr/dining/"))
    }
    """
    results = graph.query(query_classes)
    for row in results:
        cls_name = row.cls.split("/")[-1] # Get local name
        schema_str += f"- :{cls_name}\n"
    
    schema_str += "\n"

    # 3. Extract Properties (ObjectProperty & DatatypeProperty)
    schema_str += "Properties (with Domain & Range):\n"
    
    query_props = """
    SELECT DISTINCT ?prop ?type ?domain ?range ?comment
    WHERE {
        VALUES ?type { owl:ObjectProperty owl:DatatypeProperty }
        ?prop a ?type .
        OPTIONAL { ?prop rdfs:domain ?domain }
        OPTIONAL { ?prop rdfs:range ?range }
        OPTIONAL { ?prop rdfs:comment ?comment }
        FILTER(STRSTARTS(STR(?prop), "http://snu.ac.kr/dining/"))
    }
    ORDER BY ?type ?prop
    """
    results_props = graph.query(query_props)
    
    for row in results_props:
        prop_name = row.prop.split("/")[-1]
        prop_type = "ObjectProperty" if "ObjectProperty" in str(row.type) else "DatatypeProperty"
        
        domain_name = row.domain.split("/")[-1] if row.domain else "Unknown"
        # Range might be XSD or Class
        range_str = str(row.range)
        if "http://snu.ac.kr/dining/" in range_str:
             range_name = ":" + range_str.split("/")[-1]
        elif "#" in range_str:
             range_name = "xsd:" + range_str.split("#")[-1]
        else:
             range_name = range_str
             
        comment = f"  # {row.comment}" if row.comment else ""
        
        schema_str += f"- :{prop_name} ({prop_type})\n"
        schema_str += f"  Domain: :{domain_name} -> Range: {range_name}{comment}\n"

    return schema_str

if __name__ == "__main__":
    # Test Code
    # Updated Test Paths for Math Ontology
    TBOX_PATH = "data/ontology/math_tbox.ttl"
    DATA_PATH = "data/knowledge_graph/math_abox.ttl"
    
    print("Loading Graph...")
    g = load_graph(DATA_PATH)
    tbox = load_graph(TBOX_PATH)
    
    if g and tbox:
        # Merge graphs for schema extraction test
        # In real app, we might want to keep them separate or just rely on the fact 
        # that we need TBox for schema info.
        full_graph = g + tbox
    
        print("\nExtracting Schema Info...")
        schema_text = generate_schema_info(full_graph)
        print("-" * 40)
        print(schema_text)
        print("-" * 40)
        print("Schema Extraction Complete.")
