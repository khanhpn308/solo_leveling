function SuggestionInboxDropdown({
  open,
  suggestions,
  loading,
  error,
  pendingCount,
  onToggle,
  onApply,
  onDismiss,
}) {
  return (
    <div className="inbox-cluster">
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

      {open ? (
        <section className="inbox-dropdown">
          <header className="inbox-dropdown__header">
            <div>
              <p>Suggestion Inbox</p>
              <strong>{pendingCount} pending</strong>
            </div>
          </header>

          {loading ? <div className="empty-state">Dang tai suggestion...</div> : null}
          {!loading && error ? <div className="empty-state empty-state--warning">{error}</div> : null}

          {!loading && !error ? (
            <div className="suggestion-list">
              {suggestions.length === 0 ? (
                <div className="empty-state">Khong co de xuat dang mo.</div>
              ) : (
                suggestions.map((item) => (
                  <article key={item.key} className={`suggestion-node suggestion-node--${item.severity}`}>
                    <div>
                      <p>{item.skillName}</p>
                      <h3>{item.title}</h3>
                      <span>{item.detail}</span>
                    </div>
                    <div className="suggestion-actions">
                      <button type="button" onClick={() => onApply(item)}>
                        Apply
                      </button>
                      <button type="button" onClick={() => onDismiss(item)}>
                        Dismiss
                      </button>
                    </div>
                  </article>
                ))
              )}
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}

export default SuggestionInboxDropdown
