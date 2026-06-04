import PanelFrame from './PanelFrame'
import { TRACKER_MODULES } from '../dashboard-data'

function TrackersPanel() {
  return (
    <PanelFrame title="Trackers" tag="MVP Modules">
      <div className="tracker-list">
        {TRACKER_MODULES.map((item) => (
          <article key={item.key} className="tracker-node">
            <div>
              <p>{item.status}</p>
              <h3>{item.title}</h3>
              <span>{item.description}</span>
            </div>
            <button type="button">Open</button>
          </article>
        ))}
      </div>
    </PanelFrame>
  )
}

export default TrackersPanel
