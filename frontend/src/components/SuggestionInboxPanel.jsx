import PanelFrame from './PanelFrame'

function SuggestionInboxPanel({ suggestions }) {
  return (
    <PanelFrame title="Suggestion Inbox" tag={`Active ${suggestions.length}`}>
      <div className="suggestion-list">
        {suggestions.length === 0 ? (
          <div className="empty-state">No open suggestions.</div>
        ) : (
          suggestions.map((item) => (
            <article key={item.id} className={`suggestion-node suggestion-node--${item.severity}`}>
              <div>
                <p>{item.skill}</p>
                <h3>{item.title}</h3>
                <span>{item.detail}</span>
              </div>
              <div className="suggestion-actions">
                <button type="button">Apply</button>
                <button type="button">Dismiss</button>
              </div>
            </article>
          ))
        )}
      </div>
    </PanelFrame>
  )
}

export default SuggestionInboxPanel
