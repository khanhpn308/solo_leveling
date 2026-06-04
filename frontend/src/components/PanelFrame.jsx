function PanelFrame({ title, tag, children, actions, className = '' }) {
  const classes = ['panel-frame', className].filter(Boolean).join(' ')

  return (
    <section className={classes}>
      <header className="panel-frame__header">
        <div>
          <p className="panel-frame__eyebrow">System Panel</p>
          <h2>{title}</h2>
        </div>
        <div className="panel-frame__meta">
          {tag ? <span className="panel-chip">{tag}</span> : null}
          {actions}
        </div>
      </header>
      <div className="panel-frame__body">{children}</div>
    </section>
  )
}

export default PanelFrame
