# Math Ontology Chatbot Prototype

## Project Structure
- `app/`: Backend Logic (FastAPI + Reasoning Engine)
- `frontend/`: Next.js Chat Interface
- `data/`: Ontology (TBox) and Knowledge Graph (ABox)

## Prerequisites
- Node.js & npm
- Python 3.9+
- `.env` file with `GOOGLE_API_KEY` (already copied)

## How to Run

### 1. Start Backend Server
Open a terminal and run:
```bash
cd /Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto
python3 app/main.py
```
> Server runs at `http://localhost:8000`

### 2. Start Frontend App
Open **another** terminal and run:
```bash
cd /Users/hanjaehoon/pythonz/onthology_camp/dongbo_kids/math_bot_proto/frontend
npm run dev
```
> App runs at `http://localhost:3000`

## Features
- **Context-Aware Math Help**: Ask about "Taylor Series" or other math concepts.
- **Ontology Evidence**: Click "▶ 근거 개념 확인하기" to see the prerequisites traced from the Knowledge Graph.
