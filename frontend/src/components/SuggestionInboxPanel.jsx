import PanelFrame from './PanelFrame'

function SuggestionInboxPanel({ suggestions = [], pendingByKey = {}, onApply, onDismiss }) {
  return (
    <PanelFrame title="Suggestion Inbox">
      <div className="suggestion-list">
        {suggestions.length === 0 ? (
          <div className="empty-state">No open suggestions.</div>
        ) : (
          <>
            {suggestions
              .map((item) => (
                <article key={item.key} className={`suggestion-node suggestion-node--${item.severity}`}>
                  <div>
                    <p>{item.skillName}</p>
                    <h3>{item.title}</h3>
                    <span>{item.detail}</span>
                  </div>
                  <div className="suggestion-actions">
                    <button
                      type="button"
                      disabled={Boolean(pendingByKey[item.key])}
                      onClick={() => onApply?.(item)}
                    >
                      {pendingByKey[item.key] === 'apply' ? 'Applying...' : 'Apply'}
                    </button>
                    <button
                      type="button"
                      disabled={Boolean(pendingByKey[item.key])}
                      onClick={() => onDismiss?.(item)}
                    >
                      {pendingByKey[item.key] === 'dismiss' ? 'Dismissing...' : 'Dismiss'}
                    </button>
                  </div>
                </article>
              ))}
          </>
        )}
      </div>
    </PanelFrame>
  )
}

export default SuggestionInboxPanel
