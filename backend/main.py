from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import os

# Optional OpenAI usage if OPENAI_API_KEY is set. If not set, use a simple builtin parser.
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        OPENAI_AVAILABLE = False
except Exception:
    OPENAI_AVAILABLE = False

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScriptIn(BaseModel):
    script: str

class Node(BaseModel):
    id: str
    type: str
    label: str
    x: Optional[int] = None
    y: Optional[int] = None

class Edge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None

class FlowOut(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


@app.post('/parse', response_model=FlowOut)
async def parse_script(payload: ScriptIn):
    text = payload.script.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty script")

    # If OpenAI is available, prefer using an LLM to do a robust parse
    if OPENAI_AVAILABLE:
        try:
            prompt = (
                "Convert the following user flow script (short lines using If/Otherwise/Else or arrows '->' or '→') "
                "into a JSON object with 'nodes' and 'edges'. Each node should have id,type,label. "
                "Edges should have source,target,condition (if any). Only output JSON.\n\nScript:\n" + text
            )
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{"role":"user","content":prompt}],
                max_tokens=600,
                temperature=0.0,
            )
            content = resp['choices'][0]['message']['content']
            # Try to parse the returned JSON
            import json
            parsed = json.loads(content)
            return parsed
        except Exception as e:
            # fallback to simple parser
            print('OpenAI parse failed:', e)

    # SIMPLE FALLBACK PARSER (handles common patterns)
    nodes = []
    edges = []

    # create start node
    nodes.append({"id":"start","type":"start","label":"Start"})
    decision_count = 0

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        # common patterns: If X -> Y ; If X then Y ; Otherwise Y ; Else Y
        l = line
        # normalize arrow char
        l = l.replace('→', '->')
        l = l.replace('—', '-')

        if l.lower().startswith('if '):
            # split around -> or then
            condition = l[3:]
            # try arrow
            if '->' in condition:
                cond, action = [p.strip() for p in condition.split('->', 1)]
            elif ' then ' in condition.lower():
                parts = condition.split(' then ', 1)
                cond, action = parts[0].strip(), parts[1].strip()
            else:
                # try colon
                if ':' in condition:
                    cond, action = [p.strip() for p in condition.split(':',1)]
                else:
                    # fallback: split last space
                    parts = condition.split()
                    cond = ' '.join(parts[:-1]) if len(parts)>1 else condition
                    action = parts[-1] if len(parts)>1 else 'action'

            decision_id = f"decision{decision_count}"
            nodes.append({"id": decision_id, "type":"decision", "label": cond})
            action_id = f"action_{len(nodes)}"
            nodes.append({"id": action_id, "type":"action", "label": action})
            # connect start (or previous decision) to this decision if not connected
            if not any(e['source']=='start' and e['target']==decision_id for e in edges):
                edges.append({"source":"start","target":decision_id})
            edges.append({"source": decision_id, "target": action_id, "condition": cond})
            decision_count += 1
        elif l.lower().startswith('otherwise') or l.lower().startswith('else'):
            # everything after the word is the action
            # example: Otherwise greet politely
            parts = l.split(None,1)
            if len(parts) > 1:
                action = parts[1].strip()
            else:
                action = 'otherwise'
            action_id = f"action_{len(nodes)}"
            nodes.append({"id": action_id, "type":"action", "label": action})
            # if there is at least one decision, attach to last decision; else attach to start
            target_decision = f"decision{max(0, decision_count-1)}" if decision_count>0 else 'start'
            edges.append({"source": target_decision, "target": action_id, "condition": 'otherwise'})
        else:
            # line that uses arrow directly: "If user wants sales -> transfer" or "user says sales -> transfer"
            if '->' in l:
                left, right = [p.strip() for p in l.split('->',1)]
                # if left starts with If, handle above; else create a decision
                if left.lower().startswith('if '):
                    # handled earlier - skip
                    pass
                else:
                    decision_id = f"decision{decision_count}"
                    nodes.append({"id": decision_id, "type":"decision", "label": left})
                    action_id = f"action_{len(nodes)}"
                    nodes.append({"id": action_id, "type":"action", "label": right})
                    edges.append({"source":"start","target":decision_id})
                    edges.append({"source":decision_id,"target":action_id,"condition":left})
                    decision_count += 1
            else:
                # treat as standalone action, attach to start
                action_id = f"action_{len(nodes)}"
                nodes.append({"id": action_id, "type":"action", "label": l})
                edges.append({"source":"start","target":action_id})

    return {"nodes": nodes, "edges": edges}
