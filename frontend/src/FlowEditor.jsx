import React, { useMemo } from 'react'
import ReactFlow, { Background, MiniMap, Controls } from 'reactflow'
import 'reactflow/dist/style.css'

function mapNodeType(node) {
    // map our simple types to React Flow node types and add styling
    const base = { ...node }
    if (node.type === 'start') {
        base.type = 'default'
        base.data = { label: node.label }
        base.position = { x: 0, y: 0 }
    } else if (node.type === 'decision') {
        base.type = 'default'
        base.data = { label: node.label }
        base.position = { x: 200 * (parseInt(node.id.replace(/[^0-9]/g, '')) || 1), y: 60 }
    } else {
        base.type = 'default'
        base.data = { label: node.label }
        base.position = { x: 400, y: 60 * (parseInt(node.id.replace(/[^0-9]/g, '')) || 1) }
    }
    base.id = node.id
    return base
}

export default function FlowEditor({ data }) {
    const nodes = useMemo(() => (data.nodes || []).map(mapNodeType), [data])
    const edges = useMemo(() => (data.edges || []).map(e => ({ id: `${e.source}->${e.target}`, source: e.source, target: e.target, label: e.condition || '' })), [data])

    return (
        <div style={{ width: '100%', height: '80vh' }}>
            <ReactFlow nodes={nodes} edges={edges} fitView>
                <Background />
                <MiniMap />
                <Controls />
            </ReactFlow>
        </div>
    )
}
