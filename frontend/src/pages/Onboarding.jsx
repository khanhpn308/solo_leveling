import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import { activateCampaign, postManualCertificate } from '../api/auth'

const SKILLS = [
  { key: 'overall_score', label: 'Overall' },
  { key: 'listening_score', label: 'Listening' },
  { key: 'reading_score', label: 'Reading' },
  { key: 'writing_score', label: 'Writing' },
  { key: 'speaking_score', label: 'Speaking' },
]

const EMPTY_SCORES = {
  overall_score: '',
  listening_score: '',
  reading_score: '',
  writing_score: '',
  speaking_score: '',
}

const CAMPAIGN_OPTIONS = [
  {
    code: 'ielts_18_month_foundation',
    title: 'IELTS 18-Month Hunter Roadmap',
    badge: '⭐ Đề xuất',
    target: '7.0 – 7.5',
    targetBand: '7.0-7.5',
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

  // step 1=Welcome/Name, 2=Campaign, 3=StartDate, 4=Certificate, 5=Confirm
  const [step, setStep] = useState(1)
  const [displayName, setDisplayName] = useState('')
  const [campaignCode, setCampaignCode] = useState('ielts_18_month_foundation')
  const [campaignTargetBand, setCampaignTargetBand] = useState(CAMPAIGN_OPTIONS[0]?.targetBand ?? '')
  const [startDate, setStartDate] = useState(todayISO())   // ISO string YYYY-MM-DD
  const [scores, setScores] = useState(EMPTY_SCORES)
  const [hasCert, setHasCert] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function handleScoreChange(key, val) {
    setScores((prev) => ({ ...prev, [key]: val }))
  }

  function handleSkipCert() {
    setScores(EMPTY_SCORES)
    setHasCert(false)
    setStep(5)
  }

  function handleUseCert() {
    const filled = SKILLS.some((s) => scores[s.key] !== '')
    if (!filled) {
      setError('Nhập ít nhất một điểm để tiếp tục, hoặc nhấn Bỏ qua.')
      return
    }
    setError('')
    setHasCert(true)
    setStep(5)
  }

  async function handleActivate() {
    setSubmitting(true)
    setError('')
    try {
      if (hasCert) {
        const payload = {}
        SKILLS.forEach(({ key }) => {
          const v = parseFloat(scores[key])
          if (!isNaN(v)) payload[key] = v
        })
        await postManualCertificate(payload)
      }
      await activateCampaign(displayName, campaignCode, startDate, campaignTargetBand)
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
          <StepCampaign
            selected={campaignCode}
            onSelect={(code, targetBand) => {
              setCampaignCode(code)
              setCampaignTargetBand(targetBand)
            }}
            onBack={() => setStep(1)}
            onNext={() => setStep(3)}
          />
        )}

        {step === 3 && (
          <StepStartDate
            startDate={startDate}
            onStartDateChange={setStartDate}
            onBack={() => setStep(2)}
            onNext={() => setStep(4)}
          />
        )}

        {step === 4 && (
          <StepCertificate
            scores={scores}
            onChange={handleScoreChange}
            onSkip={handleSkipCert}
            onNext={handleUseCert}
            onBack={() => setStep(3)}
            error={error}
          />
        )}

        {step === 5 && (
          <StepConfirm
            displayName={displayName}
            campaignCode={campaignCode}
            startDate={startDate}
            hasCert={hasCert}
            scores={scores}
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
            onClick={() => onSelect(opt.code, opt.targetBand)}
          >
            <div className="onboarding-campaign-header">
              <span className="onboarding-campaign-title">{opt.title}</span>
              {opt.recommended && <span className="onboarding-campaign-badge">{opt.badge}</span>}
            </div>
            <p className="onboarding-campaign-desc">{opt.desc}</p>
            <div className="onboarding-campaign-meta">
              <span>🎯 Band {opt.target}</span>
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

function StepCertificate({ scores, onChange, onSkip, onNext, onBack, error }) {
  return (
    <>
      <h2 className="onboarding-title">Điểm IELTS của bạn?</h2>
      <p className="onboarding-desc">
        Nhập điểm thi IELTS gần nhất để hệ thống calibrate rank ban đầu. Bỏ qua nếu chưa thi.
      </p>
      <div className="onboarding-scores">
        {SKILLS.map(({ key, label }) => (
          <label key={key} className="onboarding-score-row">
            <span className="onboarding-score-label">{label}</span>
            <input
              type="number"
              min="0"
              max="9"
              step="0.5"
              placeholder="–"
              value={scores[key]}
              onChange={(e) => onChange(key, e.target.value)}
              className="onboarding-score-input"
            />
          </label>
        ))}
      </div>
      {error && <p className="onboarding-error">{error}</p>}
      <div className="onboarding-actions">
        <button className="onboarding-btn-ghost" onClick={onBack}>
          ← Quay lại
        </button>
        <button className="onboarding-btn-ghost" onClick={onSkip}>
          Bỏ qua
        </button>
        <button className="onboarding-btn-primary" onClick={onNext}>
          Tiếp theo →
        </button>
      </div>
    </>
  )
}

function StepConfirm({ displayName, campaignCode, startDate, hasCert, scores, submitting, error, onBack, onConfirm }) {
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
        {hasCert ? (
          <div className="onboarding-confirm-row onboarding-confirm-row--scores">
            <span className="onboarding-confirm-label">Điểm IELTS</span>
            <span className="onboarding-score-summary">
              {SKILLS.map(({ key, label }) =>
                scores[key] !== '' ? (
                  <span key={key} className="onboarding-score-chip">
                    {label}: <strong>{scores[key]}</strong>
                  </span>
                ) : null,
              )}
            </span>
          </div>
        ) : (
          <div className="onboarding-confirm-row">
            <span className="onboarding-confirm-label">Rank khởi đầu</span>
            <span className="onboarding-confirm-value">F (tất cả kỹ năng)</span>
          </div>
        )}
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
