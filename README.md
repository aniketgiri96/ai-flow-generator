# AI Script → UI Flow Generator — Full Stack (React + FastAPI)

This repo contains a minimal, **production-ready starter** that: 
- Takes a short user script (plain English `If ... -> ...` lines)
- Converts it to a JSON flow schema (backend FastAPI + optional OpenAI)
- Renders the flow in a React frontend using **React Flow**
- Allows light editing and exporting

---

## Screenshot

![AI Flow Generator Interface](./Screenshot.png)

---

## Project structure

```
ai-flow-generator/
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.js
│  ├─ index.html
│  ├─ src/
│  │  ├─ main.jsx
│  │  ├─ App.jsx
│  │  ├─ FlowEditor.jsx
│  │  └─ styles.css
└─ backend/
   ├─ requirements.txt
   └─ main.py
```

---

## Quick run (local)

### Backend

```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# Optional: set OpenAI API key for LLM-powered parsing
# set OPENAI_API_KEY=sk-...      (Windows)
# export OPENAI_API_KEY=sk-...   (macOS/Linux)

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173 (or printed Vite url)
```

---

## Features

### Backend (`backend/main.py`)

- **FastAPI** server with CORS enabled
- **Dual parsing modes**:
  - **OpenAI-powered**: Uses GPT-4o-mini when `OPENAI_API_KEY` is set for robust, intelligent parsing
  - **Fallback parser**: Simple rule-based parser for common patterns (`If X -> Y`, `Otherwise Z`, etc.)
- **REST API**: POST `/parse` endpoint accepts script text and returns JSON flow structure

### Frontend (`frontend/src/`)

- **React 18** with **Vite** for fast development
- **React Flow** for interactive flow visualization
- Features:
  - Text area for script input
  - "Parse & Draw" button to convert script to visual flow
  - Interactive flow editor with zoom, pan, and minimap
  - Error handling and loading states

---

## Example Scripts

Try these examples in the text area:

```
If user wants sales -> transfer
If user wants support -> ask for ticket number
Otherwise greet politely
```

```
If temperature > 30 -> turn on AC
If temperature < 15 -> turn on heater
Otherwise maintain current temperature
```

---

## How it works

1. **User enters script**: Plain English conditional statements using patterns like:
   - `If [condition] -> [action]`
   - `If [condition] then [action]`
   - `Otherwise [action]`
   - `Else [action]`

2. **Backend parsing**: 
   - If OpenAI is available: Uses LLM to intelligently parse script into nodes and edges
   - Otherwise: Uses pattern matching to extract conditions and actions

3. **JSON response**: Returns structured flow data:
   ```json
   {
     "nodes": [
       {"id": "start", "type": "start", "label": "Start"},
       {"id": "decision0", "type": "decision", "label": "user wants sales"},
       {"id": "action_2", "type": "action", "label": "transfer"}
     ],
     "edges": [
       {"source": "start", "target": "decision0"},
       {"source": "decision0", "target": "action_2", "condition": "user wants sales"}
     ]
   }
   ```

4. **Frontend rendering**: React Flow visualizes the graph with automatic layout

---

## Next Steps & Extensions

Possible enhancements:

1. **State Management**: Add Redux/Zustand for saving flows and export to JSON/PNG
2. **Advanced Parser**: Support `else if` chains, nested conditions, and loops
3. **Executable Flows**: Convert flows into webhook sequences or serverless functions
4. **Node Editing**: Click to edit node labels, add descriptions, change types
5. **Custom Styling**: Different colors for node types, custom shapes
6. **Export Options**: Download as JSON, PNG, or executable code

---

## Technologies Used

- **Backend**: FastAPI, Pydantic, OpenAI (optional), Uvicorn
- **Frontend**: React 18, React Flow, Axios, Vite
- **Language**: Python 3.8+, JavaScript (ES6+)

---

## License

MIT

---

## Contributing

Feel free to fork, enhance, and submit PRs!
