import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import { activateCampaign } from '../api/auth'

const BAND_OPTIONS = ['4.0', '4.5', '5.0', '5.5', '6.0', '6.5', '7.0', '7.5', '8.0', '8.5', '9.0']

const TARGET_SKILLS = [
  { key: 'overall', label: 'Overall' },
  { key: 'listening', label: 'Listening' },
  { key: 'reading', label: 'Reading' },
  { key: 'writing', label: 'Writing' },
  { key: 'speaking', label: 'Speaking' },
]

const EMPTY_TARGETS = {
  overall: '6.5',
  listening: '6.5',
  reading: '6.5',
  writing: '6.5',
  speaking: '6.5',
}

const CAMPAIGN_OPTIONS = [
  {
    code: 'ielts_18_month_foundation',
    title: 'IELTS 18-Month Hunter Roadmap',
    badge: '⭐ Đề xuất',
    duration: '18 tháng',
    desc: 'Lộ trình toàn diện từ B1 lên band 7+. Bao gồm daily quests, rank boss, và chiến lược theo từng kỹ năng.',
    recommended: true,
  },
]

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function Onboarding() {
  const { refreshAuth } = useAuth()
  const navigate = useNavigate()

  // step 1=Welcome, 2=Target, 3=Campaign, 4=StartDate, 5=Confirm
  const [step, setStep] = useState(1)
  const [displayName, setDisplayName] = useState('')
  const [targets, setTargets] = useState(EMPTY_TARGETS)
  const [campaignCode, setCampaignCode] = useState('ielts_18_month_foundation')
  const [startDate, setStartDate] = useState(todayISO())
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function handleTargetChange(key, val) {
    setTargets((prev) => ({ ...prev, [key]: val }))
  }

  async function handleActivate() {
    setSubmitting(true)
    setError('')
    try {
      await activateCampaign(displayName, campaignCode, startDate, targets)
      await refreshAuth()
      navigate('/', { replace: true })
    } catch (err) {
      setError('Có lỗi xảy ra. Vui lòng thử lại.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="onboarding-page">
      <div className="onboarding-card">
        <StepDots current={step} total={5} />

        {step === 1 && (
          <StepWelcome
            displayName={displayName}
            onDisplayNameChange={setDisplayName}
            onNext={() => setStep(2)}
          />
        )}

        {step === 2 && (
          <StepTarget
            targets={targets}
            onChange={handleTargetChange}
            onBack={() => setStep(1)}
            onNext={() => setStep(3)}
          />
        )}

        {step === 3 && (
          <StepCampaign
            selected={campaignCode}
            onSelect={(code) => setCampaignCode(code)}
            onBack={() => setStep(2)}
            onNext={() => setStep(4)}
          />
        )}

        {step === 4 && (
          <StepStartDate
            startDate={startDate}
            onStartDateChange={setStartDate}
            onBack={() => setStep(3)}
            onNext={() => setStep(5)}
          />
        )}

        {step === 5 && (
          <StepConfirm
            displayName={displayName}
            campaignCode={campaignCode}
            startDate={startDate}
            targets={targets}
            submitting={submitting}
            error={error}
            onBack={() => setStep(4)}
            onConfirm={handleActivate}
          />
        )}
      </div>
    </div>
  )
}

function StepDots({ current, total }) {
  return (
    <div className="onboarding-dots">
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={`onboarding-dot${i + 1 === current ? ' is-active' : ''}`} />
      ))}
    </div>
  )
}

function StepWelcome({ displayName, onDisplayNameChange, onNext }) {
  return (
    <>
      <div className="onboarding-icon">⚔️</div>
      <h1 className="onboarding-title">Chào mừng đến IELTS Quest</h1>
      <p className="onboarding-desc">
        Hệ thống sẽ tạo chiến dịch học 18 tháng cá nhân hoá cho bạn. Chỉ mất 1 phút thiết lập.
      </p>
      <div className="onboarding-name-row">
        <label className="onboarding-score-label">Tên hiển thị</label>
        <input
          type="text"
          className="onboarding-score-input onboarding-name-input"
          placeholder="Nhập tên của bạn…"
          maxLength={40}
          value={displayName}
          onChange={(e) => onDisplayNameChange(e.target.value)}
          autoFocus
        />
      </div>
      <div className="onboarding-actions">
        <button className="onboarding-btn-primary" onClick={onNext}>
          Tiếp theo →
        </button>
      </div>
    </>
  )
}

function StepTarget({ targets, onChange, onBack, onNext }) {
  return (
    <>
      <div className="onboarding-icon">🎯</div>
      <h2 className="onboarding-title">Mục tiêu IELTS của bạn</h2>
      <p className="onboarding-desc">
        Chọn band mục tiêu cho từng kỹ năng. Thông tin này chỉ để lên kế hoạch — không ảnh hưởng đến rank khởi đầu.
      </p>
      <div className="onboarding-scores">
        {TARGET_SKILLS.map(({ key, label }) => (
          <label key={key} className="onboarding-score-row">
            <span className="onboarding-score-label">{label}</span>
            <select
              className="onboarding-score-input"
              value={targets[key]}
              onChange={(e) => onChange(key, e.target.value)}
            >
              {BAND_OPTIONS.map((band) => (
                <option key={band} value={band}>
                  {band}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <div className="onboarding-actions">
        <button className="onboarding-btn-ghost" onClick={onBack}>
          ← Quay lại
        </button>
        <button className="onboarding-btn-primary" onClick={onNext}>
          Tiếp theo →
        </button>
      </div>
    </>
  )
}

function StepCampaign({ selected, onSelect, onBack, onNext }) {
  return (
    <>
      <h2 className="onboarding-title">Chọn chiến dịch</h2>
      <p className="onboarding-desc">
        Chọn lộ trình phù hợp với mục tiêu của bạn. Bạn có thể xem lại sau khi vào dashboard.
      </p>
      <div className="onboarding-campaign-list">
        {CAMPAIGN_OPTIONS.map((opt) => (
          <button
            key={opt.code}
            type="button"
            className={`onboarding-campaign-card${selected === opt.code ? ' is-selected' : ''}`}
            onClick={() => onSelect(opt.code)}
          >
            <div className="onboarding-campaign-header">
              <span className="onboarding-campaign-title">{opt.title}</span>
              {opt.recommended && <span className="onboarding-campaign-badge">{opt.badge}</span>}
            </div>
            <p className="onboarding-campaign-desc">{opt.desc}</p>
            <div className="onboarding-campaign-meta">
              <span>⏱ {opt.duration}</span>
            </div>
          </button>
        ))}
      </div>
      <div className="onboarding-actions">
        <button className="onboarding-btn-ghost" onClick={onBack}>
          ← Quay lại
        </button>
        <button className="onboarding-btn-primary" onClick={onNext} disabled={!selected}>
          Tiếp theo →
        </button>
      </div>
    </>
  )
}

function StepStartDate({ startDate, onStartDateChange, onBack, onNext }) {
  const today = todayISO()
  const isToday = startDate === today

  return (
    <>
      <h2 className="onboarding-title">Ngày bắt đầu chiến dịch</h2>
      <p className="onboarding-desc">
        Chọn ngày bắt đầu lộ trình 18 tháng. Hệ thống sẽ căn chỉnh quest và roadmap theo ngày này.
      </p>
      <div className="onboarding-startdate-options">
        <button
          type="button"
          className={`onboarding-startdate-option${isToday ? ' is-selected' : ''}`}
          onClick={() => onStartDateChange(today)}
        >
          <span className="onboarding-startdate-icon">📅</span>
          <span className="onboarding-startdate-label">Hôm nay</span>
          <span className="onboarding-startdate-sub">{today}</span>
        </button>
        <button
          type="button"
          className={`onboarding-startdate-option${!isToday ? ' is-selected' : ''}`}
          onClick={() => !isToday || onStartDateChange('')}
        >
          <span className="onboarding-startdate-icon">🗓️</span>
          <span className="onboarding-startdate-label">Chọn ngày khác</span>
        </button>
      </div>
      {!isToday && (
        <div className="onboarding-startdate-picker">
          <input
            type="date"
            className="onboarding-score-input onboarding-date-input"
            value={startDate}
            min="2020-01-01"
            max="2030-12-31"
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </div>
      )}
      <div className="onboarding-actions">
        <button className="onboarding-btn-ghost" onClick={onBack}>
          ← Quay lại
        </button>
        <button className="onboarding-btn-primary" onClick={onNext} disabled={!startDate}>
          Tiếp theo →
        </button>
      </div>
    </>
  )
}

function StepConfirm({ displayName, campaignCode, startDate, targets, submitting, error, onBack, onConfirm }) {
  const campaign = CAMPAIGN_OPTIONS.find((o) => o.code === campaignCode)
  return (
    <>
      <div className="onboarding-icon">🎯</div>
      <h2 className="onboarding-title">Xác nhận thiết lập</h2>
      <div className="onboarding-summary">
        {displayName.trim() && (
          <div className="onboarding-confirm-row">
            <span className="onboarding-confirm-label">Tên</span>
            <span className="onboarding-confirm-value">{displayName.trim()}</span>
          </div>
        )}
        <div className="onboarding-confirm-row onboarding-confirm-row--scores">
          <span className="onboarding-confirm-label">Mục tiêu</span>
          <span className="onboarding-score-summary">
            {TARGET_SKILLS.map(({ key, label }) => (
              <span key={key} className="onboarding-score-chip">
                {label}: <strong>{targets[key]}</strong>
              </span>
            ))}
          </span>
        </div>
        {campaign && (
          <div className="onboarding-confirm-row">
            <span className="onboarding-confirm-label">Chiến dịch</span>
            <span className="onboarding-confirm-value">{campaign.title}</span>
          </div>
        )}
        {startDate && (
          <div className="onboarding-confirm-row">
            <span className="onboarding-confirm-label">Bắt đầu</span>
            <span className="onboarding-confirm-value">{startDate}</span>
          </div>
        )}
        <div className="onboarding-confirm-row">
          <span className="onboarding-confirm-label">Rank khởi đầu</span>
          <span className="onboarding-confirm-value">F (tất cả kỹ năng)</span>
        </div>
      </div>
      {error && <p className="onboarding-error">{error}</p>}
      <div className="onboarding-actions">
        <button className="onboarding-btn-ghost" onClick={onBack} disabled={submitting}>
          ← Quay lại
        </button>
        <button className="onboarding-btn-primary" onClick={onConfirm} disabled={submitting}>
          {submitting ? 'Đang kích hoạt…' : 'Kích hoạt chiến dịch ⚡'}
        </button>
      </div>
    </>
  )
}
