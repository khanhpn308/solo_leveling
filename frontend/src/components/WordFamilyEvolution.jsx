import { useState, useEffect, useCallback } from 'react'
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'

// Custom node rendering for Word Family Evolution
const CustomFamilyNode = ({ data }) => {
  const rankColors = {
    F: '#666',
    E: '#1a73e8',
    D: '#7b1fa2',
    C: '#00897b',
    B: '#d32f2f',
    A: '#ef6c00',
    S: '#2e7d32',
  }

  const borderGlow = {
    F: 'none',
    E: '0 0 8px rgba(26, 115, 232, 0.4)',
    D: '0 0 10px rgba(123, 31, 162, 0.5)',
    C: '0 0 12px rgba(0, 137, 123, 0.6)',
    B: '0 0 14px rgba(211, 47, 47, 0.7)',
    A: '0 0 16px rgba(239, 108, 0, 0.8)',
    S: '0 0 20px rgba(46, 125, 50, 0.9)',
  }

  return (
    <div
      style={{
        padding: '10px 14px',
        borderRadius: '6px',
        background: data.isDiscovered ? '#0c0d12' : '#141416',
        border: `2px solid ${data.isDiscovered ? rankColors[data.rank] || '#555' : '#333'}`,
        boxShadow: data.isDiscovered ? borderGlow[data.rank] : 'none',
        color: data.isDiscovered ? '#fff' : '#555',
        opacity: data.isDiscovered ? 1 : 0.6,
        minWidth: '120px',
        textAlign: 'center',
        fontFamily: "'Outfit', 'Inter', sans-serif",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{data.label}</div>
      <div style={{ fontSize: '9px', color: '#888', marginTop: '4px', textTransform: 'uppercase' }}>
        {data.pos || 'unknown'}
      </div>
      {data.isDiscovered ? (
        <div style={{ fontSize: '9px', color: rankColors[data.rank], fontWeight: 'bold', marginTop: '2px' }}>
          AWAKENED (Rank {data.rank})
        </div>
      ) : (
        <div style={{ fontSize: '9px', color: '#555', marginTop: '2px' }}>
          LOCKED
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
    </div>
  )
}

const nodeTypes = {
  familyNode: CustomFamilyNode,
}

// In-code sentence gap questions for fallback families
const QUIZ_QUESTIONS = {
  'fam-produce': [
    { sentence: "The country's agricultural _____ has increased dramatically.", correct: "production", pos: "noun" },
    { sentence: "We had a very _____ meeting today and solved three major bugs.", correct: "productive", pos: "adjective" },
    { sentence: "They launched a new software _____ last week.", correct: "product", pos: "noun" },
    { sentence: "Workers want to increase their _____ and earn bonuses.", correct: "productivity", pos: "noun" }
  ],
  'fam-communicate': [
    { sentence: "Good _____ is the key to a healthy relationship.", correct: "communication", pos: "noun" },
    { sentence: "She is a highly _____ person who loves meeting new people.", correct: "communicative", pos: "adjective" },
    { sentence: "A great leader must be an effective _____.", correct: "communicator", pos: "noun" }
  ],
  'fam-create': [
    { sentence: "The _____ of this new role will improve our team's throughput.", correct: "creation", pos: "noun" },
    { sentence: "Writers need to be extremely _____ to write good novels.", correct: "creative", pos: "adjective" },
    { sentence: "Children show incredible _____ when they are drawing.", correct: "creativity", pos: "noun" },
    { sentence: "The _____ of the game attended the opening ceremony.", correct: "creator", pos: "noun" }
  ]
}

function WordFamilyEvolution({ api, onXPUpdate }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [families, setFamilies] = useState([])
  const [selectedFamilyId, setSelectedFamilyId] = useState('')
  
  // React Flow states
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  
  // Quiz states
  const [currentQuiz, setCurrentQuiz] = useState(null)
  const [quizOptions, setQuizOptions] = useState([])
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [quizStatus, setQuizStatus] = useState(null) // 'correct', 'wrong'
  const [xpEarned, setXpEarned] = useState(0)

  useEffect(() => {
    loadFamilies()
  }, [])

  useEffect(() => {
    if (selectedFamilyId) {
      const selected = families.find(f => f.family_id === selectedFamilyId)
      if (selected) {
        renderFamilyTree(selected)
        setupQuiz(selected)
      }
    }
  }, [selectedFamilyId, families])

  async function loadFamilies() {
    try {
      setLoading(true)
      setError(null)
      const data = await api('/vocabulary/practice/word-family')
      if (data && data.families && data.families.length > 0) {
        setFamilies(data.families)
        setSelectedFamilyId(data.families[0].family_id)
      } else {
        setFamilies([])
      }
    } catch (err) {
      setError(err.message || 'Failed to load word families')
    } finally {
      setLoading(false)
    }
  }

  function renderFamilyTree(family) {
    // Basic Layouting: Root at top-middle, others spread out underneath
    const renderedNodes = family.nodes.map((node, idx) => {
      const isRoot = node.label.toLowerCase() === family.root_word.toLowerCase()
      let x = 250
      let y = 50

      if (!isRoot) {
        // Spaced out horizontally
        const totalNonRoot = family.nodes.length - 1
        const positionIndex = family.nodes.filter((n, i) => i < idx && n.label.toLowerCase() !== family.root_word.toLowerCase()).length
        const spacing = 160
        const startX = 250 - ((totalNonRoot - 1) * spacing) / 2
        x = startX + positionIndex * spacing
        y = 200
      }

      return {
        id: node.id,
        type: 'familyNode',
        position: { x, y },
        data: {
          label: node.label,
          pos: node.part_of_speech,
          meaning: node.meaning,
          rank: node.mastery_rank || 'F',
          isDiscovered: node.is_discovered
        }
      }
    })

    const renderedEdges = family.edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      style: { stroke: 'var(--primary)', strokeWidth: 2 },
      labelStyle: { fill: 'var(--text-muted)', fontSize: 10, fontWeight: 700 }
    }))

    setNodes(renderedNodes)
    setEdges(renderedEdges)
  }

  function setupQuiz(family) {
    setSelectedAnswer(null)
    setQuizStatus(null)
    
    // 1. Try to find preset questions for fallbacks
    const fallbackQs = QUIZ_QUESTIONS[family.family_id]
    if (fallbackQs && fallbackQs.length > 0) {
      const randomQ = fallbackQs[Math.floor(Math.random() * fallbackQs.length)]
      const options = family.nodes.map(n => n.label)
      setCurrentQuiz({
        sentence: randomQ.sentence,
        correct: randomQ.correct,
        isCustom: false
      })
      setQuizOptions(options.sort(() => 0.5 - Math.random()))
    } else {
      // 2. Generate a dynamic quiz for custom DB family
      // Ask to choose correct part of speech of the root word
      const nonRoots = family.nodes.filter(n => n.label.toLowerCase() !== family.root_word.toLowerCase())
      if (nonRoots.length > 0) {
        const target = nonRoots[Math.floor(Math.random() * nonRoots.length)]
        setCurrentQuiz({
          sentence: `Select the ${target.part_of_speech || 'derived'} form of '${family.root_word}':`,
          correct: target.label,
          isCustom: true
        })
        const options = family.nodes.map(n => n.label)
        setQuizOptions(options.sort(() => 0.5 - Math.random()))
      } else {
        setCurrentQuiz(null)
      }
    }
  }

  async function handleAnswer(opt) {
    if (selectedAnswer !== null) return
    setSelectedAnswer(opt)

    if (opt.toLowerCase() === currentQuiz.correct.toLowerCase()) {
      setQuizStatus('correct')
      setXpEarned(prev => prev + 10)
      
      // Save practice success back to DB
      try {
        await api('/vocabulary/practice/record-success', {
          method: 'POST',
          body: {
            words: [currentQuiz.correct],
            xp_gained: 10
          }
        })
        if (onXPUpdate) {
          onXPUpdate(10)
        }
      } catch (err) {
        console.error('Failed to log practice success:', err)
      }
    } else {
      setQuizStatus('wrong')
    }
  }

  if (loading) {
    return <div className="vocab-loader">Analysing Word Roots...</div>
  }

  if (error) {
    return (
      <div className="vocab-empty-state">
        <p className="text-amber">{error}</p>
        <button className="system-button mt-2" onClick={loadFamilies}>Try Again</button>
      </div>
    )
  }

  if (families.length === 0) {
    return (
      <div className="vocab-empty-state">
        <p>No word families available. Connect words via "word_family" relations in Codex to start.</p>
      </div>
    )
  }

  const selectedFamily = families.find(f => f.family_id === selectedFamilyId)

  return (
    <div className="word-family-evolution">
      <div className="family-header">
        <h3>WORD FAMILY EVOLUTION</h3>
        <p>Analyze how root words morph into different parts of speech.</p>
        
        <div className="family-selector mt-3">
          <label>Select Word Root: </label>
          <select 
            value={selectedFamilyId} 
            onChange={(e) => setSelectedFamilyId(e.target.value)}
            className="system-select"
          >
            {families.map(f => (
              <option key={f.family_id} value={f.family_id}>
                {f.root_word.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="family-grid mt-4">
        {/* React Flow Canvas */}
        <div className="family-canvas-wrapper">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#333" gap={16} />
            <Controls />
          </ReactFlow>
        </div>

        {/* Practice/Info Sidebar Panel */}
        <div className="family-sidebar">
          {selectedFamily && (
            <div className="family-info-box">
              <h4>Root: {selectedFamily.root_word}</h4>
              <p className="text-muted">Total family members: {selectedFamily.nodes.length}</p>
              
              <div className="family-members-details mt-3">
                {selectedFamily.nodes.map(n => (
                  <div key={n.id} className={`member-row ${n.is_discovered ? 'active' : 'locked'}`}>
                    <strong>{n.label}</strong>
                    <span className="member-pos">({n.part_of_speech || 'unknown'})</span>
                    {n.meaning && <p className="member-meaning">{n.meaning}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentQuiz && (
            <div className="family-quiz-box mt-4">
              <h5>FAMILY PRACTICE</h5>
              <div className="quiz-sentence mt-3 mb-3">
                {currentQuiz.isCustom ? (
                  <p>{currentQuiz.sentence}</p>
                ) : (
                  <p style={{ fontStyle: 'italic' }}>
                    "{currentQuiz.sentence}"
                  </p>
                )}
              </div>

              <div className="quiz-options-vertical">
                {quizOptions.map((opt, idx) => {
                  let btnClass = 'system-button system-button--outline quiz-option-item'
                  if (selectedAnswer === opt) {
                    btnClass += quizStatus === 'correct' ? ' quiz-correct' : ' quiz-wrong'
                  } else if (selectedAnswer !== null && opt.toLowerCase() === currentQuiz.correct.toLowerCase()) {
                    btnClass += ' quiz-correct-reveal'
                  }

                  return (
                    <button
                      key={idx}
                      className={btnClass}
                      onClick={() => handleAnswer(opt)}
                      disabled={selectedAnswer !== null}
                    >
                      {opt}
                    </button>
                  )
                })}
              </div>

              {selectedAnswer !== null && (
                <div className="quiz-feedback mt-3">
                  {quizStatus === 'correct' ? (
                    <div className="text-success">✔ Correct! +10 XP Persistent Reward</div>
                  ) : (
                    <div className="text-danger">✘ Wrong! Try reviewing the tree layout.</div>
                  )}
                  <button 
                    className="system-button system-button--primary mt-3 w-full"
                    onClick={() => setupQuiz(selectedFamily)}
                  >
                    Next Question
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default WordFamilyEvolution
