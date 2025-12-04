import React, { useState } from 'react'
import FlowEditor from './FlowEditor'
import axios from 'axios'

export default function App() {
    const [script, setScript] = useState("If user wants sales -> transfer\nIf user wants support -> ask for ticket number\nOtherwise greet politely")
    const [flow, setFlow] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleParse() {
        setLoading(true)
        setError(null)
        try {
            const res = await axios.post('http://localhost:8000/parse', { script })
            setFlow(res.data)
        } catch (err) {
            console.error(err)
            setError(err?.response?.data?.detail || err.message)
        } finally { setLoading(false) }
    }

    return (
        <div className="app-root">
            <div className="panel left">
                <h2>AI Script → UI Flow Generator</h2>
                <textarea value={script} onChange={e => setScript(e.target.value)} rows={10} />
                <div className="controls">
                    <button onClick={handleParse} disabled={loading}>Parse & Draw</button>
                    {loading && <span>Parsing...</span>}
                    {error && <div className="error">{error}</div>}
                </div>
            </div>

            <div className="panel right">
                <h3>Flow</h3>
                {flow ? (
                    <FlowEditor data={flow} />
                ) : (
                    <div className="placeholder">No flow yet — click "Parse & Draw"</div>
                )}
            </div>
        </div>
    )
}
