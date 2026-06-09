import { useState, useEffect, useCallback } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'

// Custom node component with Solo Leveling glowing borders
const CustomVocabNode = ({ data }) => {
  const statusColors = {
    locked: '#444444',
    discovered: '#1a73e8',
    activated: '#7b1fa2',
    stabilized: '#00897b',
    mastered: '#ef6c00',
    awakened: '#2e7d32',
  }

  const borderGlow = {
    locked: 'none',
    discovered: '0 0 10px rgba(26, 115, 232, 0.5)',
    activated: '0 0 12px rgba(123, 31, 162, 0.6)',
    stabilized: '0 0 14px rgba(0, 137, 123, 0.7)',
    mastered: '0 0 18px rgba(239, 108, 0, 0.8)',
    awakened: '0 0 22px rgba(46, 125, 50, 0.9)',
  }

  return (
    <div
      style={{
        padding: '12px 18px',
        borderRadius: '8px',
        background: '#0a0a0c',
        border: `2px solid ${statusColors[data.status] || '#777'}`,
        boxShadow: borderGlow[data.status],
        color: '#ffffff',
        minWidth: '140px',
        textAlign: 'center',
        fontFamily: "'Outfit', 'Inter', sans-serif",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      
      <div style={{ fontSize: '15px', fontWeight: '700', letterSpacing: '0.5px' }}>{data.label}</div>
      
      <div
        style={{
          fontSize: '9px',
          color: '#888',
          textTransform: 'uppercase',
          marginTop: '6px',
          letterSpacing: '1px',
          fontWeight: 'bold',
        }}
      >
        {data.type}
      </div>
      
      <div
        style={{
          fontSize: '9px',
          color: statusColors[data.status],
          marginTop: '2px',
          fontWeight: 'bold',
          textTransform: 'uppercase',
        }}
      >
        {data.status}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  )
}

const nodeTypes = {
  vocabNode: CustomVocabNode,
}

function WordNetworkTree({ api, vocabularyItems, onLoadData }) {
  const [topics, setTopics] = useState([])
  const [selectedTopicId, setSelectedTopicId] = useState(null)
  const [newTopicName, setNewTopicName] = useState('')
  const [showNewTopicForm, setShowNewTopicForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // React Flow states
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  // Sidebar / Drawer states
  const [selectedNode, setSelectedNode] = useState(null)
  const [linkTargetWordId, setLinkTargetWordId] = useState('')

  useEffect(() => {
    loadTopics()
  }, [])

  useEffect(() => {
    if (selectedTopicId) {
      loadTree(selectedTopicId)
    } else {
      setNodes([])
      setEdges([])
    }
    setSelectedNode(null)
  }, [selectedTopicId])

  async function loadTopics() {
    try {
      setLoading(true)
      const data = await api('/vocabulary/tree/topics')
      setTopics(data)
      if (data.length > 0 && !selectedTopicId) {
        setSelectedTopicId(data[0].id)
      }
    } catch (err) {
      setError(err.message || 'Failed to load topics')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateTopic(e) {
    e.preventDefault()
    if (!newTopicName.trim()) return
    try {
      setLoading(true)
      const newTopic = await api('/vocabulary/tree/topics', {
        method: 'POST',
        body: JSON.stringify({ topic_name: newTopicName }),
      })
      setTopics((prev) => [...prev, newTopic])
      setSelectedTopicId(newTopic.id)
      setNewTopicName('')
      setShowNewTopicForm(false)
    } catch (err) {
      setError(err.message || 'Failed to create topic')
    } finally {
      setLoading(false)
    }
  }

  async function loadTree(topicId) {
    try {
      setLoading(true)
      const tree = await api(`/vocabulary/tree/${topicId}`)
      
      // Map DB nodes to React Flow format
      const flowNodes = tree.nodes.map((node) => ({
        id: String(node.id),
        type: 'vocabNode',
        position: {
          x: node.x_position !== null ? node.x_position : Math.random() * 400 + 50,
          y: node.y_position !== null ? node.y_position : Math.random() * 300 + 50,
        },
        data: {
          label: node.node_label,
          type: node.node_type || 'word',
          status: node.status,
          vocabulary_item_id: node.vocabulary_item_id,
          dbNode: node,
        },
      }))

      // Map DB edges to React Flow format
      const flowEdges = tree.edges.map((edge) => ({
        id: String(edge.id),
        source: String(edge.source_node_id),
        target: String(edge.target_node_id),
        type: 'smoothstep',
        animated: edge.strength > 1,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#555',
        },
        style: { stroke: '#555' },
      }))

      setNodes(flowNodes)
      setEdges(flowEdges)
    } catch (err) {
      setError(err.message || 'Failed to load tree')
    } finally {
      setLoading(false)
    }
  }

  // Handle drag stop - persist positions
  const onNodeDragStop = useCallback(
    async (event, node) => {
      try {
        await api(`/vocabulary/tree/nodes/${node.id}`, {
          method: 'PATCH',
          body: JSON.stringify({
            x_position: node.position.x,
            y_position: node.position.y,
          }),
        })
      } catch (err) {
        console.error('Failed to save node position:', err)
      }
    },
    [api]
  )

  // Handle edge connections
  const onConnect = useCallback(
    async (connection) => {
      try {
        const newEdge = await api('/vocabulary/tree/edges', {
          method: 'POST',
          body: JSON.stringify({
            source_node_id: parseInt(connection.source),
            target_node_id: parseInt(connection.target),
            edge_type: 'collocation_link',
          }),
        })

        const flowEdge = {
          id: String(newEdge.id),
          source: String(newEdge.source_node_id),
          target: String(newEdge.target_node_id),
          type: 'smoothstep',
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#555',
          },
          style: { stroke: '#555' },
        }

        setEdges((eds) => addEdge(flowEdge, eds))
      } catch (err) {
        setError(err.message || 'Failed to connect nodes')
      }
    },
    [api, setEdges]
  )

  // Add a word from Codex into the visual map
  async function handleAddWordToTree(item) {
    if (!selectedTopicId) return
    // Check if item already exists as node in this tree
    const exists = nodes.some((n) => n.data.vocabulary_item_id === item.id)
    if (exists) {
      setError(`"${item.word}" is already on this topic tree map.`)
      return
    }

    try {
      setLoading(true)
      const newNode = await api('/vocabulary/tree/nodes', {
        method: 'POST',
        body: JSON.stringify({
          topic_id: selectedTopicId,
          vocabulary_item_id: item.id,
          node_label: item.word,
          node_type: 'word',
          status: 'discovered',
          x_position: 150 + Math.random() * 100,
          y_position: 150 + Math.random() * 100,
        }),
      })

      const flowNode = {
        id: String(newNode.id),
        type: 'vocabNode',
        position: { x: newNode.x_position, y: newNode.y_position },
        data: {
          label: newNode.node_label,
          type: newNode.node_type || 'word',
          status: newNode.status,
          vocabulary_item_id: newNode.vocabulary_item_id,
          dbNode: newNode,
        },
      }

      setNodes((nds) => [...nds, flowNode])
      setError('')
    } catch (err) {
      setError(err.message || 'Failed to add node')
    } finally {
      setLoading(false)
    }
  }

  // Handle node selection
  const onNodeClick = useCallback(
    (event, node) => {
      const dbNode = node.data.dbNode
      const linkedItem = vocabularyItems.find((item) => item.id === dbNode.vocabulary_item_id)
      setSelectedNode({
        node: dbNode,
        item: linkedItem || null,
      })
    },
    [vocabularyItems]
  )

  async function handleDeleteEdge(edgeId) {
    if (!window.confirm('Remove this connection edge?')) return
    try {
      setLoading(true)
      await api(`/vocabulary/tree/edges/${edgeId}`, { method: 'DELETE' })
      setEdges((eds) => eds.filter((e) => e.id !== String(edgeId)))
    } catch (err) {
      setError(err.message || 'Failed to delete connection')
    } finally {
      setLoading(false)
    }
  }

  async function handleSyncAll() {
    try {
      setLoading(true)
      await api('/vocabulary/tree/sync-all', { method: 'POST' })
      if (selectedTopicId) {
        await loadTree(selectedTopicId)
      }
      if (onLoadData) {
        await onLoadData()
      }
    } catch (err) {
      setError(err.message || 'Failed to sync node states')
    } finally {
      setLoading(false)
    }
  }

  // Filter codex items not yet in tree
  const unmappedItems = vocabularyItems.filter(
    (item) => !nodes.some((n) => n.data.vocabulary_item_id === item.id)
  )

  return (
    <div className="vocab-tree-layout">
      {/* Sidebar: Topics & Codex List */}
      <div className="vocab-tree-sidebar">
        <div className="sidebar-section">
          <div className="sidebar-section-header">
            <h3>Topic Visual Maps</h3>
            <button
              className="system-button system-button--xs"
              onClick={() => setShowNewTopicForm(!showNewTopicForm)}
            >
              {showNewTopicForm ? 'Cancel' : '+ New'}
            </button>
          </div>

          {showNewTopicForm && (
            <form onSubmit={handleCreateTopic} className="new-topic-form">
              <input
                type="text"
                value={newTopicName}
                onChange={(e) => setNewTopicName(e.target.value)}
                placeholder="Topic Name (e.g. Health)"
                className="system-input"
                required
              />
              <button type="submit" className="system-button system-button--primary system-button--xs">
                Create
              </button>
            </form>
          )}

          <div className="topics-list">
            {topics.map((t) => (
              <button
                key={t.id}
                className={`topic-select-btn ${selectedTopicId === t.id ? 'active' : ''}`}
                onClick={() => setSelectedTopicId(t.id)}
              >
                👁️ {t.topic_name}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-section codex-linker-section">
          <h4>Connect Codex Items</h4>
          <p className="section-desc">Click a word to add it into your active topic tree map.</p>
          <div className="unmapped-words-list">
            {unmappedItems.map((item) => (
              <button
                key={item.id}
                className="add-to-tree-btn"
                onClick={() => handleAddWordToTree(item)}
              >
                <span>{item.word}</span>
                <span className="add-plus">+</span>
              </button>
            ))}
            {unmappedItems.length === 0 && (
              <div className="all-mapped-msg">All Codex items are mapped or Codex is empty.</div>
            )}
          </div>
        </div>

        <div className="sidebar-actions">
          <button className="system-button sync-all-btn" onClick={handleSyncAll}>
            🔄 Sync Mastery States
          </button>
        </div>
      </div>

      {/* Visual Canvas Area */}
      <div className="vocab-tree-canvas">
        {error && <div className="canvas-error">{error}</div>}
        {loading && <div className="canvas-loader">Mapping network...</div>}
        
        {selectedTopicId ? (
          <div style={{ width: '100%', height: '100%', background: '#08080a' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeDragStop={onNodeDragStop}
              onConnect={onConnect}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background color="#1f1f2e" gap={20} size={1.5} />
              <Controls showInteractive={false} style={{ background: '#111', border: '1px solid #333' }} />
              <MiniMap
                style={{ background: '#111', border: '1px solid #333' }}
                nodeColor={(node) => {
                  const colors = {
                    locked: '#444',
                    discovered: '#1a73e8',
                    activated: '#7b1fa2',
                    stabilized: '#00897b',
                    mastered: '#ef6c00',
                    awakened: '#2e7d32',
                  }
                  return colors[node.data.status] || '#777'
                }}
                maskColor="rgba(0, 0, 0, 0.7)"
              />
            </ReactFlow>
          </div>
        ) : (
          <div className="canvas-empty-state">
            <h4>No Topic Visual Map Selected</h4>
            <p>Create or select a topic visual map from the sidebar to launch the grid.</p>
          </div>
        )}
      </div>

      {/* Drawer: Detailed node stats & connections */}
      {selectedNode && (
        <div className="vocab-tree-drawer">
          <div className="drawer-header">
            <h3>Lexical Node Scanner</h3>
            <button className="close-drawer-btn" onClick={() => setSelectedNode(null)}>
              ✕
            </button>
          </div>

          <div className="drawer-content">
            <div className="node-badge-row">
              <h4>{selectedNode.node.node_label}</h4>
              <span className={`node-badge status-${selectedNode.node.status}`}>
                {selectedNode.node.status}
              </span>
            </div>

            {selectedNode.item ? (
              <div className="node-item-details">
                <div className="detail-row">
                  <span>Part of Speech:</span>
                  <strong>{selectedNode.item.part_of_speech}</strong>
                </div>
                {selectedNode.item.cefr_level && (
                  <div className="detail-row">
                    <span>CEFR Level:</span>
                    <strong>{selectedNode.item.cefr_level}</strong>
                  </div>
                )}
                {selectedNode.item.pronunciation_ipa && (
                  <div className="detail-row">
                    <span>IPA:</span>
                    <strong className="ipa-text">{selectedNode.item.pronunciation_ipa}</strong>
                  </div>
                )}
                {selectedNode.item.word_stress && (
                  <div className="detail-row">
                    <span>Word Stress:</span>
                    <strong>{selectedNode.item.word_stress}</strong>
                  </div>
                )}

                <div className="detail-section">
                  <h5>Definitions</h5>
                  {selectedNode.item.meaning_en && (
                    <div className="meaning-block">
                      <small>ENGLISH</small>
                      <p>{selectedNode.item.meaning_en}</p>
                    </div>
                  )}
                  {selectedNode.item.meaning_vi && (
                    <div className="meaning-block">
                      <small>VIETNAMESE</small>
                      <p>{selectedNode.item.meaning_vi}</p>
                    </div>
                  )}
                </div>

                {selectedNode.item.examples && selectedNode.item.examples.length > 0 && (
                  <div className="detail-section">
                    <h5>Examples</h5>
                    <ul className="drawer-examples">
                      {selectedNode.item.examples.map((ex) => (
                        <li key={ex.id}>{ex.example_sentence}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedNode.item.collocations && selectedNode.item.collocations.length > 0 && (
                  <div className="detail-section">
                    <h5>Collocations</h5>
                    <div className="drawer-tags">
                      {selectedNode.item.collocations.map((col) => (
                        <span key={col.id} className="drawer-tag">
                          {col.collocation}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="node-unlinked-details">
                <p>This node is a visual label and has no linked vocabulary item in Codex.</p>
              </div>
            )}

            {/* Edge removal management */}
            <div className="edge-remover-section">
              <h5>Connected Edges</h5>
              <div className="edges-list">
                {edges
                  .filter((e) => e.source === String(selectedNode.node.id) || e.target === String(selectedNode.node.id))
                  .map((e) => {
                    const otherNodeId = e.source === String(selectedNode.node.id) ? e.target : e.source
                    const otherNode = nodes.find((n) => n.id === otherNodeId)
                    const label = otherNode ? otherNode.data.label : `Node #${otherNodeId}`
                    return (
                      <div key={e.id} className="edge-row">
                        <span>Link to <strong>{label}</strong></span>
                        <button
                          className="edge-del-btn"
                          onClick={() => handleDeleteEdge(e.id)}
                        >
                          Unlink
                        </button>
                      </div>
                    )
                  })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WordNetworkTree
