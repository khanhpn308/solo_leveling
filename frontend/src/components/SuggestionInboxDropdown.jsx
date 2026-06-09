import { usePresenceLayer } from './usePresenceLayer'

function SuggestionInboxDropdown({
  open,
  suggestions,
  loading,
  error,
  pendingCount,
  pendingByKey,
  onToggle,
  onClose,
  onApply,
  onDismiss,
}) {
  const { isMounted, phase, rootRef } = usePresenceLayer({
    open,
    onClose,
    closeOnInteractOutside: true,
  })

  return (
    <div ref={rootRef} className="inbox-cluster">
      <button
        className={`system-icon-button system-icon-button--bell ${open ? 'is-active' : ''}`}
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-label={`Suggestion inbox ${pendingCount} pending`}
      >
        <i className="icon-bell" aria-hidden="true" />
        {pendingCount > 0 ? <span className="system-badge">{pendingCount}</span> : null}
      </button>

      {isMounted ? (
        <section
          className={`inbox-dropdown ${phase === 'open' ? 'is-open' : phase === 'entering' ? 'is-entering' : 'is-closing'}`}
          aria-label="Suggestion inbox"
          data-presence={phase}
        >
          <header className="inbox-dropdown__header">
            <div>
              <p>Suggestion Inbox</p>
            </div>
          </header>

          {loading ? <div className="empty-state">Loading suggestions...</div> : null}
          {!loading && error ? <div className="empty-state empty-state--warning">{error}</div> : null}

          {!loading && !error ? (
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
                            onClick={() => onApply(item)}
                          >
                            {pendingByKey[item.key] === 'apply' ? 'Applying...' : 'Apply'}
                          </button>
                          <button
                            type="button"
                            disabled={Boolean(pendingByKey[item.key])}
                            onClick={() => onDismiss(item)}
                          >
                            {pendingByKey[item.key] === 'dismiss' ? 'Dismissing...' : 'Dismiss'}
                          </button>
                        </div>
                      </article>
                    ))}
                </>
              )}
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}

export default SuggestionInboxDropdown
