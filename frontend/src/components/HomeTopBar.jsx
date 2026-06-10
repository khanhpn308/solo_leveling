import SuggestionInboxDropdown from './SuggestionInboxDropdown'

function HomeTopBar({
  player,
  hostDateTime,
  pendingCount,
  isInboxOpen,
  inboxItems,
  suggestionsLoading,
  suggestionsError,
  suggestionPendingByKey,
  onToggleInbox,
  onCloseInbox,
  onApplySuggestion,
  onDismissSuggestion,
  hasPendingClaims,
  onOpenNav,
  onOpenStatus,
}) {
  return (
    <header className="home-topbar">
      <button className="system-icon-button system-icon-button--menu" type="button" onClick={onOpenNav} aria-label="Open navigation">
        <i className="icon-menu" aria-hidden="true" />
        {hasPendingClaims ? <span className="system-notify-dot" aria-hidden="true" /> : null}
      </button>

      <div className="topbar-cluster">
        <div className="topbar-level">
          <strong>{player.level}</strong>
          <span>{player.rank}</span>
        </div>

        <button className="avatar-trigger" type="button" onClick={onOpenStatus} aria-label="Open status center">
          <span className="avatar-trigger__core">{player.displayName.slice(0, 1).toUpperCase()}</span>
        </button>

        <SuggestionInboxDropdown
          open={isInboxOpen}
          suggestions={inboxItems}
          loading={suggestionsLoading}
          error={suggestionsError}
          pendingCount={pendingCount}
          pendingByKey={suggestionPendingByKey}
          onToggle={onToggleInbox}
          onClose={onCloseInbox}
          onApply={onApplySuggestion}
          onDismiss={onDismissSuggestion}
        />

        <div className="topbar-clock">
          <span>Host</span>
          <strong>{hostDateTime}</strong>
        </div>
      </div>
    </header>
  )
}

export default HomeTopBar
