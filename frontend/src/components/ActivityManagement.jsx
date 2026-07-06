import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Activity, Search, Star, Clock, Users, Heart, TrendingUp, Edit, Share2, BarChart3, Mic } from 'lucide-react'
import ActivityCustomization from './ActivityCustomization'
import CollaborativeDesign from './CollaborativeDesign'
import VoiceInput from './VoiceInput'
import LazyImage from './LazyImage'
import './ActivityManagement.css'

const ActivityManagement = () => {
  const { t } = useTranslation(['activity', 'common'])
  const [activities, setActivities] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('templates')
  const [searchTerm, setSearchTerm] = useState('')
  const [customizingActivity, setCustomizingActivity] = useState(null)
  const [showCollaborativeDesign, setShowCollaborativeDesign] = useState(false)
  const [showVoiceInput, setShowVoiceInput] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState(null)

  const tabs = [
    { id: 'templates', icon: Activity, labelKey: 'tabs.templates' },
    { id: 'recommendations', icon: TrendingUp, labelKey: 'tabs.recommendations' },
    { id: 'records', icon: Heart, labelKey: 'tabs.records' },
    { id: 'plans', icon: Clock, labelKey: 'tabs.plans' },
    { id: 'shared', icon: Share2, labelKey: 'tabs.shared' },
  ]

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'templates') {
        const response = await api.get('/activities/templates')
        setActivities(response.data?.templates || response.data || [])
      } else if (activeTab === 'recommendations') {
        try {
          const response = await api.post('/activities/recommend', {
            caregiver_id: 'current_user',
            elder_profile: {
              interests: [],
              abilities: [],
              health_conditions: [],
              mobility_level: 'normal',
              cognitive_level: 'normal'
            }
          })
          setRecommendations([response.data] || [])
        } catch (err) {
          console.error('Failed to load recommendations:', err)
          setRecommendations([])
        }
      } else if (activeTab === 'records') {
        const response = await api.get('/activities/records')
        setRecords(response.data?.records || response.data || [])
      } else if (activeTab === 'plans') {
        await api.get('/activities/enhanced/plans')
      } else if (activeTab === 'shared') {
        const response = await api.get('/activities/enhanced/shared')
        setActivities(response.data?.activities || [])
      }
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredActivities = activities.filter(activity =>
    activity.title_zh?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    activity.category?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="activity-management">
      <div className="activity-header">
        <div className="header-content">
          <Activity size={24} />
          <h2>{t('activity:title')}</h2>
        </div>
      </div>

      <div className="activity-tabs">
        {tabs.map(({ id, icon: Icon, labelKey }) => (
          <button
            key={id}
            className={`tab-button ${activeTab === id ? 'active' : ''}`}
            onClick={() => setActiveTab(id)}
          >
            <Icon size={18} />
            {t(`activity:${labelKey}`)}
          </button>
        ))}
      </div>

      <div className="activity-actions">
        <button
          className="action-button"
          onClick={() => setShowCollaborativeDesign(true)}
        >
          <Users size={18} />
          {t('activity:collaborativeDesign')}
        </button>
        <button
          className="action-button"
          onClick={() => setShowVoiceInput(!showVoiceInput)}
        >
          <Mic size={18} />
          {t('activity:voiceInput')}
        </button>
      </div>

      {showVoiceInput && (
        <div className="voice-input-container">
          <VoiceInput
            language="ja"
            onTranscript={() => {
              setShowVoiceInput(false)
            }}
          />
        </div>
      )}

      {showCollaborativeDesign && (
        <div className="collaborative-design-container">
          <CollaborativeDesign
            elderId="elder_001"
            caregiverId="caregiver_001"
            onSave={() => {
              setShowCollaborativeDesign(false)
              loadData()
            }}
          />
        </div>
      )}

      {customizingActivity && (
        <div className="customization-container">
          <ActivityCustomization
            template={customizingActivity}
            onSave={() => {
              setCustomizingActivity(null)
              loadData()
            }}
            onCancel={() => setCustomizingActivity(null)}
          />
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="templates-view">
          <div className="search-bar">
            <Search size={20} />
            <input
              type="text"
              placeholder={t('activity:searchPlaceholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          {loading ? (
            <div className="loading-state">{t('common:loading')}</div>
          ) : (
            <div className="activity-grid">
              {filteredActivities.length === 0 ? (
                <div className="empty-state">
                  <Activity size={48} />
                  <p>{t('activity:noTemplates')}</p>
                </div>
              ) : (
                filteredActivities.map((activity) => (
                  <div key={activity.id} className="activity-card">
                    <div className="activity-card-header">
                      <div className="category-badge">{activity.category}</div>
                      <div className="difficulty-badge">{activity.difficulty_level}</div>
                    </div>
                    <h3>{activity.title_zh}</h3>
                    {activity.description_zh && (
                      <p className="activity-description">{activity.description_zh}</p>
                    )}
                    <div className="activity-meta">
                      <div className="meta-item">
                        <Clock size={16} />
                        <span>{t('activity:durationMinutes', { count: activity.duration_minutes || 30 })}</span>
                      </div>
                      <div className="meta-item">
                        <Users size={16} />
                        <span>{t('activity:participants', { count: activity.participant_count || '1-2' })}</span>
                      </div>
                      {activity.rating > 0 && (
                        <div className="meta-item">
                          <Star size={16} />
                          <span>{activity.rating.toFixed(1)}</span>
                        </div>
                      )}
                    </div>
                    {activity.tags && activity.tags.length > 0 && (
                      <div className="activity-tags">
                        {activity.tags.map((tag, idx) => (
                          <span key={idx} className="tag">{tag}</span>
                        ))}
                      </div>
                    )}
                    <div className="activity-actions-inline">
                      <button
                        className="activity-button"
                        onClick={() => setCustomizingActivity(activity)}
                      >
                        <Edit size={16} />
                        {t('activity:customize')}
                      </button>
                      <button
                        className="activity-button secondary"
                        onClick={async () => {
                          try {
                            await api.post(`/activities/enhanced/${activity.activity_id}/share`, {
                              share_type: 'public',
                              allow_copy: true
                            }, {
                              params: { shared_by: 'current_user' }
                            })
                            alert(t('activity:sharedSuccess'))
                          } catch (err) {
                            console.error('Failed to share:', err)
                          }
                        }}
                      >
                        <Share2 size={16} />
                        {t('activity:share')}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="recommendations-view">
          {loading ? (
            <div className="loading-state">{t('common:loading')}</div>
          ) : (
            <div className="recommendations-list">
              {recommendations.length === 0 ? (
                <div className="empty-state">
                  <TrendingUp size={48} />
                  <p>{t('activity:noRecommendations')}</p>
                </div>
              ) : (
                recommendations.map((rec) => (
                  <div key={rec.id} className="recommendation-card">
                    <div className="recommendation-header">
                      <h3>{t('activity:personalizedRecommendation')}</h3>
                      <span className="recommendation-date">
                        {new Date(rec.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="recommendation-reason">{rec.reason}</p>
                    <div className="recommended-activities">
                      {rec.activities.map((activity) => (
                        <div key={activity.id} className="recommended-activity">
                          <div className="activity-info">
                            <h4>{activity.title}</h4>
                            <div className="activity-badges">
                              <span className="category-badge small">{activity.category}</span>
                              <span className="difficulty-badge small">{activity.difficulty}</span>
                            </div>
                          </div>
                          <button className="btn-small">{t('activity:select')}</button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'records' && (
        <div className="records-view">
          {loading ? (
            <div className="loading-state">{t('common:loading')}</div>
          ) : (
            <div className="records-list">
              {records.length === 0 ? (
                <div className="empty-state">
                  <Heart size={48} />
                  <p>{t('activity:noRecords')}</p>
                </div>
              ) : (
                records.map((record) => (
                  <div key={record.id} className="record-card">
                    <div className="record-header">
                      <h3>{record.activity_title}</h3>
                      <span className="record-date">
                        {new Date(record.activity_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="record-details">
                      <div className="detail-item">
                        <Clock size={16} />
                        <span>{t('activity:durationLabel', { count: record.duration_minutes })}</span>
                      </div>
                      {record.elder_engagement && (
                        <div className="detail-item">
                          <Heart size={16} />
                          <span>{t('activity:engagementLabel', { level: record.elder_engagement })}</span>
                        </div>
                      )}
                    </div>
                    {record.photos && record.photos.length > 0 && (
                      <div className="record-photos">
                        {record.photos.map((photo, idx) => (
                          <LazyImage
                            key={idx}
                            src={photo}
                            alt={t('activity:photoAlt', { index: idx + 1 })}
                            className="record-photo"
                          />
                        ))}
                      </div>
                    )}
                    {record.notes && (
                      <p className="record-notes">{record.notes}</p>
                    )}
                    <div className="record-actions">
                      <button
                        className="btn-small"
                        onClick={() => setSelectedRecord(record)}
                      >
                        <BarChart3 size={16} />
                        {t('activity:effectAnalysis')}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'plans' && (
        <div className="plans-view">
          <div className="empty-state">
            <Clock size={48} />
            <p>{t('activity:plansInDevelopment')}</p>
            <button className="btn-primary" onClick={() => {}}>
              {t('activity:createPlan')}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'shared' && (
        <div className="shared-view">
          {loading ? (
            <div className="loading-state">{t('common:loading')}</div>
          ) : (
            <div className="activity-grid">
              <div className="empty-state">
                <Share2 size={48} />
                <p>{t('activity:noShared')}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ActivityManagement
