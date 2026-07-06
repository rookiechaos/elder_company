import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { X, ChevronRight, CheckCircle, Circle, ArrowRight, ArrowLeft } from 'lucide-react'
import './Onboarding.css'

const STEP_IDS = ['welcome', 'translation', 'activities', 'customers', 'personalization', 'complete']

const Onboarding = ({ onComplete, skipOnboarding }) => {
  const { t } = useTranslation(['onboarding', 'common', 'translation'])
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState(new Set())

  const renderStepContent = (stepId) => {
    switch (stepId) {
      case 'welcome':
        return (
          <div className="onboarding-content">
            <div className="welcome-icon">🌟</div>
            <h3>{t('onboarding:steps.welcome.missionTitle')}</h3>
            <p>{t('onboarding:steps.welcome.missionText')}</p>
            <ul>
              {[0, 1, 2].map((i) => (
                <li key={i}>{t(`onboarding:steps.welcome.items.${i}`)}</li>
              ))}
            </ul>
          </div>
        )
      case 'translation':
        return (
          <div className="onboarding-content">
            <div className="feature-demo">
              <div className="demo-box">
                <div className="demo-input">{t('onboarding:steps.translation.demoInput')}</div>
                <ArrowRight size={24} className="demo-arrow" />
                <div className="demo-output">{t('onboarding:steps.translation.demoOutput')}</div>
              </div>
            </div>
            <h3>{t('onboarding:steps.translation.featuresTitle')}</h3>
            <ul>
              {[0, 1, 2, 3].map((i) => (
                <li key={i}>{t(`onboarding:steps.translation.items.${i}`)}</li>
              ))}
            </ul>
          </div>
        )
      case 'activities':
        return (
          <div className="onboarding-content">
            <div className="feature-demo">
              <div className="activity-card">
                <h4>{t('onboarding:steps.activities.demoTitle')}</h4>
                <p>{t('onboarding:steps.activities.demoSubtitle')}</p>
                <span className="activity-tag">{t('onboarding:steps.activities.recommended')}</span>
              </div>
            </div>
            <h3>{t('onboarding:steps.activities.featuresTitle')}</h3>
            <ul>
              {[0, 1, 2, 3].map((i) => (
                <li key={i}>{t(`onboarding:steps.activities.items.${i}`)}</li>
              ))}
            </ul>
          </div>
        )
      case 'customers':
        return (
          <div className="onboarding-content">
            <div className="feature-demo">
              <div className="customer-card">
                <div className="customer-avatar">👴</div>
                <div className="customer-info">
                  <h4>{t('onboarding:steps.customers.demoName')}</h4>
                  <p>{t('onboarding:steps.customers.demoInfo')}</p>
                  <div className="customer-tags">
                    <span>{t('onboarding:steps.customers.demoTags.0')}</span>
                    <span>{t('onboarding:steps.customers.demoTags.1')}</span>
                  </div>
                </div>
              </div>
            </div>
            <h3>{t('onboarding:steps.customers.featuresTitle')}</h3>
            <ul>
              {[0, 1, 2, 3].map((i) => (
                <li key={i}>{t(`onboarding:steps.customers.items.${i}`)}</li>
              ))}
            </ul>
          </div>
        )
      case 'personalization':
        return (
          <div className="onboarding-content">
            <div className="feature-demo">
              <div className="settings-preview">
                <div className="setting-item">
                  <label>{t('onboarding:steps.personalization.defaultLanguage')}</label>
                  <select>
                    <option>{t('translation:languages.ja')}</option>
                    <option>{t('translation:languages.en')}</option>
                  </select>
                </div>
                <div className="setting-item">
                  <label>{t('onboarding:steps.personalization.translationStyle')}</label>
                  <select>
                    <option>{t('onboarding:steps.personalization.styleFormal')}</option>
                    <option>{t('onboarding:steps.personalization.styleFriendly')}</option>
                    <option>{t('onboarding:steps.personalization.styleConcise')}</option>
                  </select>
                </div>
              </div>
            </div>
            <h3>{t('onboarding:steps.personalization.featuresTitle')}</h3>
            <ul>
              {[0, 1, 2, 3].map((i) => (
                <li key={i}>{t(`onboarding:steps.personalization.items.${i}`)}</li>
              ))}
            </ul>
          </div>
        )
      case 'complete':
        return (
          <div className="onboarding-content">
            <div className="complete-icon">🎉</div>
            <h3>{t('onboarding:steps.complete.nextStepsTitle')}</h3>
            <div className="next-steps">
              {[1, 2, 3].map((n) => (
                <div key={n} className="step-card">
                  <CheckCircle size={24} />
                  <div>
                    <h4>{t(`onboarding:steps.complete.step${n}Title`)}</h4>
                    <p>{t(`onboarding:steps.complete.step${n}Text`)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      default:
        return null
    }
  }

  useEffect(() => {
    const completed = localStorage.getItem('onboarding_completed')
    if (completed === 'true' && skipOnboarding) {
      onComplete()
    }
  }, [onComplete, skipOnboarding])

  const handleNext = () => {
    const newCompleted = new Set(completedSteps)
    newCompleted.add(currentStep)
    setCompletedSteps(newCompleted)

    if (currentStep < STEP_IDS.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = () => {
    localStorage.setItem('onboarding_completed', 'true')
    onComplete()
  }

  const handleSkip = () => {
    if (window.confirm(t('onboarding:skipConfirm'))) {
      handleComplete()
    }
  }

  const progress = ((currentStep + 1) / STEP_IDS.length) * 100
  const stepId = STEP_IDS[currentStep]

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        <div className="onboarding-header">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <button className="skip-button" onClick={handleSkip}>
            <X size={20} /> {t('common:skip')}
          </button>
        </div>

        <div className="onboarding-body">
          <div className="step-indicator">
            {STEP_IDS.map((id, index) => (
              <div
                key={id}
                className={`step-dot ${index === currentStep ? 'active' : ''} ${completedSteps.has(index) ? 'completed' : ''}`}
                onClick={() => setCurrentStep(index)}
              >
                {completedSteps.has(index) ? (
                  <CheckCircle size={16} />
                ) : (
                  <Circle size={16} />
                )}
              </div>
            ))}
          </div>

          <div className="step-content">
            <h2>{t(`onboarding:steps.${stepId}.title`)}</h2>
            <p className="step-description">{t(`onboarding:steps.${stepId}.description`)}</p>
            {renderStepContent(stepId)}
          </div>
        </div>

        <div className="onboarding-footer">
          {currentStep > 0 && (
            <button className="nav-button prev" onClick={handlePrevious}>
              <ArrowLeft size={20} /> {t('common:back')}
            </button>
          )}
          <div className="step-counter">
            {currentStep + 1} / {STEP_IDS.length}
          </div>
          <button className="nav-button next" onClick={handleNext}>
            {currentStep === STEP_IDS.length - 1 ? t('common:start') : t('common:next')}
            {currentStep < STEP_IDS.length - 1 && <ChevronRight size={20} />}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Onboarding
