import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Save, X, Plus, Trash2 } from 'lucide-react'
import './ActivityCustomization.css'

const ActivityCustomization = ({ template, onSave, onCancel }) => {
  const { t } = useTranslation(['activityCustomization', 'common'])
  const [customized, setCustomized] = useState({
    title_zh: template?.title_zh || '',
    title_ja: template?.title_ja || '',
    description_zh: template?.description_zh || '',
    steps: template?.steps || [],
    materials: template?.required_materials || [],
    duration: template?.duration_minutes || 30,
    difficulty: template?.difficulty_level || 'medium',
    notes: ''
  })

  const [newStep, setNewStep] = useState('')
  const [newMaterial, setNewMaterial] = useState('')

  const handleAddStep = () => {
    if (newStep.trim()) {
      setCustomized({
        ...customized,
        steps: [...customized.steps, newStep]
      })
      setNewStep('')
    }
  }

  const handleRemoveStep = (index) => {
    setCustomized({
      ...customized,
      steps: customized.steps.filter((_, i) => i !== index)
    })
  }

  const handleAddMaterial = () => {
    if (newMaterial.trim()) {
      setCustomized({
        ...customized,
        materials: [...customized.materials, newMaterial]
      })
      setNewMaterial('')
    }
  }

  const handleRemoveMaterial = (index) => {
    setCustomized({
      ...customized,
      materials: customized.materials.filter((_, i) => i !== index)
    })
  }

  const handleSave = async () => {
    try {
      if (template?.activity_id) {
        await api.post('/activities/enhanced/customize', {
          template_id: template.activity_id,
          customizations: customized
        })
      }
      onSave?.(customized)
    } catch (err) {
      console.error('Failed to save customization:', err)
      alert(t('activityCustomization:saveFailed'))
    }
  }

  return (
    <div className="activity-customization">
      <div className="customization-header">
        <h3>{t('activityCustomization:title')}</h3>
        <div className="header-actions">
          <button className="btn-secondary" onClick={onCancel}>
            <X size={18} />
            {t('common:cancel')}
          </button>
          <button className="btn-primary" onClick={handleSave}>
            <Save size={18} />
            {t('common:save')}
          </button>
        </div>
      </div>

      <div className="customization-form">
        <div className="form-group">
          <label>{t('activityCustomization:activityNameEnglish')}</label>
          <input
            type="text"
            value={customized.title_zh}
            onChange={(e) => setCustomized({ ...customized, title_zh: e.target.value })}
            placeholder={t('activityCustomization:activityNamePlaceholder')}
          />
        </div>

        <div className="form-group">
          <label>{t('activityCustomization:activityDescription')}</label>
          <textarea
            value={customized.description_zh}
            onChange={(e) => setCustomized({ ...customized, description_zh: e.target.value })}
            placeholder={t('activityCustomization:activityDescriptionPlaceholder')}
            rows={3}
          />
        </div>

        <div className="form-group">
          <label>{t('activityCustomization:activitySteps')}</label>
          <div className="steps-list">
            {customized.steps.map((step, index) => (
              <div key={index} className="step-item">
                <span className="step-number">{index + 1}</span>
                <span className="step-text">{step}</span>
                <button
                  className="btn-icon"
                  onClick={() => handleRemoveStep(index)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
            <div className="add-step">
              <input
                type="text"
                value={newStep}
                onChange={(e) => setNewStep(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddStep()}
                placeholder={t('activityCustomization:addStepPlaceholder')}
              />
              <button className="btn-icon" onClick={handleAddStep}>
                <Plus size={18} />
              </button>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>{t('activityCustomization:materials')}</label>
          <div className="materials-list">
            {customized.materials.map((material, index) => (
              <div key={index} className="material-item">
                <span>{material}</span>
                <button
                  className="btn-icon"
                  onClick={() => handleRemoveMaterial(index)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
            <div className="add-material">
              <input
                type="text"
                value={newMaterial}
                onChange={(e) => setNewMaterial(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddMaterial()}
                placeholder={t('activityCustomization:addMaterialPlaceholder')}
              />
              <button className="btn-icon" onClick={handleAddMaterial}>
                <Plus size={18} />
              </button>
            </div>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>{t('activityCustomization:durationMinutes')}</label>
            <input
              type="number"
              value={customized.duration}
              onChange={(e) => setCustomized({ ...customized, duration: parseInt(e.target.value) })}
              min="5"
              max="180"
            />
          </div>

          <div className="form-group">
            <label>{t('activityCustomization:difficulty')}</label>
            <select
              value={customized.difficulty}
              onChange={(e) => setCustomized({ ...customized, difficulty: e.target.value })}
            >
              <option value="easy">{t('common:easy')}</option>
              <option value="medium">{t('common:medium')}</option>
              <option value="hard">{t('common:hard')}</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>{t('activityCustomization:notes')}</label>
          <textarea
            value={customized.notes}
            onChange={(e) => setCustomized({ ...customized, notes: e.target.value })}
            placeholder={t('activityCustomization:notesPlaceholder')}
            rows={2}
          />
        </div>
      </div>
    </div>
  )
}

export default ActivityCustomization
