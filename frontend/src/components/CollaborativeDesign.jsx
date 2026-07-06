import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Users, MessageSquare, Save, Plus } from 'lucide-react'
import './CollaborativeDesign.css'

const CollaborativeDesign = ({ elderId, caregiverId, onSave }) => {
  const { t } = useTranslation(['collaborativeDesign', 'common'])
  const [participants, setParticipants] = useState([
    { user_id: caregiverId, role: 'caregiver', nameKey: 'roles.caregiver' },
    { user_id: elderId, role: 'elder', nameKey: 'roles.elder' }
  ])
  
  const [designData, setDesignData] = useState({
    title_zh: '',
    description_zh: '',
    steps: [],
    materials: []
  })
  
  const [notes, setNotes] = useState('')
  const [newStep, setNewStep] = useState('')
  const [newMaterial, setNewMaterial] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')

  const handleAddParticipant = (role) => {
    const nameKey = role === 'family' ? 'roles.family' : role === 'caregiver' ? 'roles.caregiver' : 'roles.elder'
    const newParticipant = {
      user_id: `user_${Date.now()}`,
      role: role,
      nameKey
    }
    setParticipants([...participants, newParticipant])
  }

  const handleAddStep = () => {
    if (newStep.trim()) {
      setDesignData({
        ...designData,
        steps: [...designData.steps, newStep]
      })
      setNewStep('')
    }
  }

  const handleAddMaterial = () => {
    if (newMaterial.trim()) {
      setDesignData({
        ...designData,
        materials: [...designData.materials, newMaterial]
      })
      setNewMaterial('')
    }
  }

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      setChatMessages([
        ...chatMessages,
        {
          id: Date.now(),
          user: t('collaborativeDesign:roles.caregiver'),
          message: newMessage,
          timestamp: new Date().toISOString()
        }
      ])
      setNewMessage('')
    }
  }

  const handleSave = async () => {
    try {
      await api.post('/activities/enhanced/collaborate/design', {
        participants: participants,
        design_data: designData,
        notes: notes
      })
      onSave?.()
      alert(t('collaborativeDesign:savedSuccess'))
    } catch (err) {
      console.error('Failed to save collaborative design:', err)
      alert(t('collaborativeDesign:saveFailed'))
    }
  }

  return (
    <div className="collaborative-design">
      <div className="design-header">
        <div className="header-left">
          <Users size={24} />
          <h2>{t('collaborativeDesign:title')}</h2>
        </div>
        <button className="btn-primary" onClick={handleSave}>
          <Save size={18} />
          {t('collaborativeDesign:saveDesign')}
        </button>
      </div>

      <div className="design-layout">
        <div className="design-main">
          <div className="design-section">
            <h3>{t('collaborativeDesign:activityDesign')}</h3>
            <div className="form-group">
              <label>{t('collaborativeDesign:activityName')}</label>
              <input
                type="text"
                value={designData.title_zh}
                onChange={(e) => setDesignData({ ...designData, title_zh: e.target.value })}
                placeholder={t('collaborativeDesign:activityNamePlaceholder')}
              />
            </div>
            <div className="form-group">
              <label>{t('collaborativeDesign:activityDescription')}</label>
              <textarea
                value={designData.description_zh}
                onChange={(e) => setDesignData({ ...designData, description_zh: e.target.value })}
                placeholder={t('collaborativeDesign:activityDescriptionPlaceholder')}
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>{t('collaborativeDesign:activitySteps')}</label>
              {designData.steps.map((step, idx) => (
                <div key={idx} className="step-item">
                  <span className="step-number">{idx + 1}</span>
                  <span>{step}</span>
                </div>
              ))}
              <div className="add-item">
                <input
                  type="text"
                  value={newStep}
                  onChange={(e) => setNewStep(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddStep()}
                  placeholder={t('collaborativeDesign:addStepPlaceholder')}
                />
                <button onClick={handleAddStep}>
                  <Plus size={18} />
                </button>
              </div>
            </div>
            <div className="form-group">
              <label>{t('collaborativeDesign:materials')}</label>
              {designData.materials.map((material, idx) => (
                <div key={idx} className="material-tag">{material}</div>
              ))}
              <div className="add-item">
                <input
                  type="text"
                  value={newMaterial}
                  onChange={(e) => setNewMaterial(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddMaterial()}
                  placeholder={t('collaborativeDesign:addMaterialPlaceholder')}
                />
                <button onClick={handleAddMaterial}>
                  <Plus size={18} />
                </button>
              </div>
            </div>
          </div>

          <div className="design-section">
            <h3>{t('collaborativeDesign:designNotes')}</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder={t('collaborativeDesign:notesPlaceholder')}
              rows={4}
            />
          </div>
        </div>

        <div className="design-sidebar">
          <div className="participants-section">
            <h3>{t('collaborativeDesign:participants')}</h3>
            {participants.map((p, idx) => (
              <div key={idx} className="participant-item">
                <div className="participant-avatar">
                  {t(`collaborativeDesign:${p.nameKey}`)[0]}
                </div>
                <div className="participant-info">
                  <div className="participant-name">{t(`collaborativeDesign:${p.nameKey}`)}</div>
                  <div className="participant-role">{p.role}</div>
                </div>
              </div>
            ))}
            <button
              className="btn-add-participant"
              onClick={() => handleAddParticipant('family')}
            >
              <Plus size={16} />
              {t('collaborativeDesign:addFamily')}
            </button>
          </div>

          <div className="chat-section">
            <h3>
              <MessageSquare size={18} />
              {t('collaborativeDesign:discussion')}
            </h3>
            <div className="chat-messages">
              {chatMessages.map((msg) => (
                <div key={msg.id} className="chat-message">
                  <div className="message-author">{msg.user}</div>
                  <div className="message-content">{msg.message}</div>
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder={t('collaborativeDesign:messagePlaceholder')}
              />
              <button onClick={handleSendMessage}>{t('collaborativeDesign:send')}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CollaborativeDesign
