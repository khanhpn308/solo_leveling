function NavigationDrawer({ open, onClose, onOpenQuestTab, onOpenCertificates, onOpenBoss }) {
  if (!open) return null

  return (
    <div className="drawer-shell">
      <button className="drawer-shell__scrim" type="button" onClick={onClose} aria-label="Close navigation" />
      <aside className="nav-drawer">
        <header className="nav-drawer__header">
          <p>System Access</p>
          <strong>Mission Gates</strong>
        </header>

        <div className="nav-drawer__actions">
          <div className="nav-drawer__group">
            <div className="nav-drawer__group-header">
              <span>Quest</span>
              <small>Main / Daily / Weekly / Archive</small>
            </div>
            <div className="nav-drawer__subactions">
              <button type="button" onClick={() => onOpenQuestTab('main')}>
                Main
              </button>
              <button type="button" onClick={() => onOpenQuestTab('daily')}>
                Daily
              </button>
              <button type="button" onClick={() => onOpenQuestTab('weekly')}>
                Weekly
              </button>
              <button type="button" disabled>
                Archive
              </button>
            </div>
          </div>
          <button type="button" onClick={onOpenCertificates}>
            <span>Certificate</span>
            <small>IELTS / Aptis / TOEIC / TOEFL</small>
          </button>
          <button type="button" onClick={onOpenBoss}>
            <span>Boss</span>
            <small>Current target + timeline</small>
          </button>
        </div>
      </aside>
    </div>
  )
}

export default NavigationDrawer
