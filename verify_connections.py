import rdflib
from rdflib import Namespace, RDFS, RDF

g = rdflib.Graph()
g.parse("data/knowledge_graph/math_abox.ttl", format="turtle")
NS = Namespace("http://math.bot/ontology/")

targets = ["공간좌표", "확률분포", "조건부확률"]

for target in targets:
    print(f"\nTarget Label: {target}")
    # Find all URIs with this label
    nodes = []
    for s, p, o in g.triples((None, RDFS.label, None)):
        if str(o) == target:
            # Get Type
            node_type = g.value(s, RDF.type)
            nodes.append((s, node_type))
    
    if not nodes:
        print(f"  [Error] No URI found for label '{target}'")
        continue

    for uri, type_uri in nodes:
        type_str = str(type_uri).split('/')[-1] if type_uri else "Unknown"
        print(f"  Node: {uri} (Type: {type_str})")
        
        # Find Prereqs (Incoming edges)
        # ?s prerequisiteOf target
        has_incoming = False
        for s, p, o in g.triples((None, NS.prerequisiteOf, uri)):
            has_incoming = True
            label = g.value(s, RDFS.label)
            conn_type = g.value(s, RDF.type)
            conn_type_str = str(conn_type).split('/')[-1] if conn_type else "?"
            print(f"    <- Prereq: {label} ({conn_type_str})")

        # Find Post-reqs (Outgoing edges)
        # target prerequisiteOf ?o
        has_outgoing = False
        for s, p, o in g.triples((uri, NS.prerequisiteOf, None)):
            has_outgoing = True
            label = g.value(o, RDFS.label)
            conn_type = g.value(o, RDF.type)
            conn_type_str = str(conn_type).split('/')[-1] if conn_type else "?"
            print(f"    -> Next:   {label} ({conn_type_str})")
            
        if not has_incoming and not has_outgoing:
            print("    (No prerequisite connections)")
