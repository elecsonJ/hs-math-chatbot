import rdflib
from pyvis.network import Network
import os
import webbrowser

def visualize_ontology(graph=None, highlight_labels=None, output_file="math_graph.html", return_html_str=False):
    # 1. Load the Graph
    if graph:
        g = graph
        # print("[INFO] Using provided in-memory graph.")
    else:
        g = rdflib.Graph()
        try:
            g.parse("data/ontology/math_tbox.ttl", format="turtle")
            g.parse("data/knowledge_graph/math_abox.ttl", format="turtle")
            print("[INFO] Graph loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load graph: {e}")
            return

    # Normalize highlight_labels for easier matching
    if highlight_labels:
        highlight_labels = set(highlight_labels)
    else:
        highlight_labels = set()

    # 2. Init Pyvis Network (Style: White Background like the Notebook)
    # cdn_resources='in_line' embeds the scripts into the HTML, making it standalone (fixes CDN/CORS issues)
    # [Visual Fix] Disable select_menu to remove "Select by ID" dropdown
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", select_menu=False, directed=True, cdn_resources="in_line")
    
    # Notebook specific options injection
    # [Visual Fix] Tweak physics for stability (stop floating)
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08,
          "damping": 0.9,
          "avoidOverlap": 0
        },
        "stabilization": {
            "enabled": true,
            "iterations": 1000,
            "updateInterval": 25,
            "onlyDynamicEdges": false,
            "fit": true
        },
        "minVelocity": 0.75,
        "maxVelocity": 30
      },
      "nodes": {
        "shadow": {
            "enabled": true,
            "color": "rgba(0,0,0,0.1)",
            "size": 10,
            "x": 5,
            "y": 5
        }
      }
    }
    """)

    # 3. Define Namespaces
    NS = rdflib.Namespace("http://snu.ac.kr/math/")
    RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
    RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    # 4. Extract Nodes & Edges
    def get_label(uri):
        label = g.value(uri, RDFS.label)
        if label:
            return str(label)
        return str(uri).split("/")[-1]

    def get_group(uri):
        types = list(g.objects(uri, RDF.type))
        if NS.Subject in types: return "Subject"
        if NS.Chapter in types: return "Chapter"
        if NS.Section in types: return "Section"
        if NS.Concept in types: return "Concept"
        return "Other"

    # Define Styles (Shapes mimic the 'Mode' from the notebook)
    styles = {
        "Subject": {"color": "#FF6B6B", "shape": "database", "size": 30},   # Database shape for Subject
        "Chapter": {"color": "#4ECDC4", "shape": "box", "size": 25},        # Box for Chapter
        "Section": {"color": "#FFE66D", "shape": "ellipse", "size": 20},    # Ellipse for Section
        "Concept": {"color": "#1A535C", "shape": "dot", "size": 15},        # Dot for Concept
        "Other":   {"color": "#97C2FC", "shape": "text", "size": 10}
    }
    
    # Highlight Style
    highlight_style = {"color": "#FF0000", "shape": "star", "size": 35, "borderWidth": 3, "borderColor": "#000000"}
    # [Visual Fix] Greyed out style for non-highlighted nodes
    grey_style = {"color": "#e0e0e0", "shape": "dot", "size": 10, "font": {"color": "#cccccc"}}

    # print("[INFO] Processing Nodes...")
    existing_nodes = set()
    
    for s in g.subjects(unique=True):
        if not isinstance(s, rdflib.URIRef): continue
        str_s = str(s)
        
        lbl = get_label(s)
        group = get_group(s)
        
        # Determine Style
        if highlight_labels:
            # We are in Focus Mode
            if lbl in highlight_labels:
                style = highlight_style
            else:
                style = grey_style
        else:
            # Normal Mode
            style = styles.get(group, styles["Other"])
        
        # Tooltip
        title = f"<b>{lbl}</b><br>Type: {group}<br>URI: {s}"
        comment = g.value(s, RDFS.comment)
        if comment:
             title += f"<br><i>{comment}</i>"

        # Check if style has custom border logic (highlight)
        extra_args = {}
        if "borderWidth" in style:
            extra_args["borderWidth"] = style["borderWidth"]
            extra_args["color"] = {"background": style["color"], "border": style.get("borderColor", "black")}
        else:
            extra_args["color"] = style["color"]
        
        # Font color override for grey nodes
        if "font" in style:
            extra_args["font"] = style["font"]

        net.add_node(str_s, label=lbl, title=title, 
                     shape=style["shape"], size=style["size"], group=group, **extra_args)
        existing_nodes.add(str_s)

    # print("[INFO] Processing Edges...")
    for s, p, o in g:
        if not isinstance(s, rdflib.URIRef) or not isinstance(o, rdflib.URIRef): continue
        str_s = str(s)
        str_o = str(o)
        
        if str_s not in existing_nodes or str_o not in existing_nodes:
            continue
        
        prop_name = str(p).split("/")[-1].split("#")[-1]
        
        if prop_name == "type": continue
        
        # Default Visual Style for Edges
        width = 1
        edge_color = "#bdbdbd"
        dashes = False
        
        if highlight_labels:
            # Focus Mode Logic
            s_lbl = get_label(s)
            o_lbl = get_label(o)
            
            s_high = s_lbl in highlight_labels
            o_high = o_lbl in highlight_labels
            
            if s_high and o_high:
                # [Strong] Connection between two relevant nodes
                # Preserve semantic colors but make them pop
                if "prerequisiteOf" in prop_name:
                    edge_color = "#FF0000" # Bright Red
                    width = 3
                elif "has" in prop_name:
                    edge_color = "#555555" # Dark Grey
                    width = 3
                else:
                    edge_color = "#000000"
                    width = 2
            elif s_high or o_high:
                # [Context] Connection to a relevant node
                edge_color = "#aaaaaa" # Visible Medium Grey
                width = 1
                dashes = True # Dotted line for context
            else:
                # [Dimmed] Background noise
                edge_color = "#eeeeee" # Very Light Grey (barely visible to reduce clutter)
                width = 1
        else:
            # Standard Mode (No Highlight)
            if "prerequisiteOf" in prop_name:
                edge_color = "#FF4040" 
                width = 2
            elif "has" in prop_name:
                edge_color = "#848484" 
                width = 3

        net.add_edge(str_s, str_o, title=prop_name, color=edge_color, width=width, dashes=dashes)

    # 5. Output
    if return_html_str:
        return net.generate_html()
    else:
        net.save_graph(output_file)
        print(f"[SUCCESS] Visualization saved to {output_file}")
        try:
            webbrowser.open('file://' + os.path.realpath(output_file))
        except:
            pass

if __name__ == "__main__":
    visualize_ontology()
