import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Users, UserPlus, Search, Edit, Trash2, Heart, UserCheck, AlertCircle } from 'lucide-react'
import './CustomerManagement.css'

const CustomerManagement = () => {
  const { t } = useTranslation(['customer', 'common'])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState(null)
  const [formData, setFormData] = useState({
    customer_type: 'caregiver',
    name: '',
    name_ja: '',
    name_en: '',
    email: '',
    phone: '',
    language_abilities: {},
    role: '',
    experience_years: '',
    specialties: [],
    health_conditions: [],
    interests: [],
    mobility_level: 'independent'
  })

  const emptyFormData = {
    customer_type: 'caregiver',
    name: '',
    name_ja: '',
    name_en: '',
    email: '',
    phone: '',
    language_abilities: {},
    role: '',
    experience_years: '',
    specialties: [],
    health_conditions: [],
    interests: [],
    mobility_level: 'independent'
  }

  const customerTypeLabels = {
    caregiver: t('common:caregiver'),
    elder: t('common:elder'),
    family: t('common:family'),
  }

  const mobilityLabels = {
    independent: t('common:independent'),
    limited: t('common:limited'),
    wheelchair: t('common:wheelchair'),
    bedridden: t('common:bedridden'),
  }

  useEffect(() => {
    loadCustomers()
  }, [])

  const loadCustomers = async () => {
    setLoading(true)
    setError(null)
    try {
      const mockCustomers = [
        {
          id: '1',
          customer_type: 'caregiver',
          name: 'Taro Tanaka',
          name_ja: '田中太郎',
          role: 'Care worker',
          experience_years: 5,
          specialties: ['Dementia care', 'Rehabilitation']
        },
        {
          id: '2',
          customer_type: 'elder',
          name: 'Hanako Tanaka',
          name_ja: '田中花子',
          health_conditions: ['Dementia'],
          interests: ['Crafts', 'Music'],
          mobility_level: 'limited'
        }
      ]
      setCustomers(mockCustomers)
    } catch (err) {
      setError(err.message || t('customer:loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      if (editingCustomer) {
        await api.put(`/customers/${editingCustomer.id}`, formData)
      } else {
        await api.post('/customers', formData)
      }
      setShowForm(false)
      setEditingCustomer(null)
      setFormData(emptyFormData)
      loadCustomers()
    } catch (err) {
      setError(err.message || t('customer:saveFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (customer) => {
    setEditingCustomer(customer)
    setFormData({
      customer_type: customer.customer_type,
      name: customer.name || '',
      name_ja: customer.name_ja || '',
      name_en: customer.name_en || '',
      email: customer.email || '',
      phone: customer.phone || '',
      role: customer.role || '',
      experience_years: customer.experience_years || '',
      specialties: customer.specialties || [],
      health_conditions: customer.health_conditions || [],
      interests: customer.interests || [],
      mobility_level: customer.mobility_level || 'independent'
    })
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(t('customer:confirmDelete'))) return
    
    try {
      await api.delete(`/customers/${id}`)
      loadCustomers()
    } catch (err) {
      setError(err.message || t('customer:deleteFailed'))
    }
  }

  const filteredCustomers = customers.filter(customer => {
    const searchLower = searchTerm.toLowerCase()
    return (
      customer.name?.toLowerCase().includes(searchLower) ||
      customer.name_ja?.toLowerCase().includes(searchLower) ||
      customer.role?.toLowerCase().includes(searchLower) ||
      customer.customer_type?.toLowerCase().includes(searchLower)
    )
  })

  return (
    <div className="customer-management">
      <div className="customer-header">
        <div className="header-content">
          <Users size={24} />
          <h2>{t('customer:title')}</h2>
        </div>
        <button
          className="btn-primary"
          onClick={() => {
            setShowForm(true)
            setEditingCustomer(null)
            setFormData(emptyFormData)
          }}
        >
          <UserPlus size={18} />
          {t('customer:addCustomer')}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="search-bar">
        <Search size={20} />
        <input
          type="text"
          placeholder={t('customer:searchPlaceholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{editingCustomer ? t('customer:editCustomer') : t('customer:addCustomer')}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>{t('customer:customerType')}</label>
                <select
                  value={formData.customer_type}
                  onChange={(e) => setFormData({ ...formData, customer_type: e.target.value })}
                  className="form-input"
                >
                  <option value="caregiver">{t('common:caregiver')}</option>
                  <option value="elder">{t('common:elder')}</option>
                  <option value="family">{t('common:family')}</option>
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>{t('customer:nameEnglish')}</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="form-input"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('customer:nameJapanese')}</label>
                  <input
                    type="text"
                    value={formData.name_ja}
                    onChange={(e) => setFormData({ ...formData, name_ja: e.target.value })}
                    className="form-input"
                  />
                </div>
              </div>

              {formData.customer_type === 'caregiver' && (
                <div className="form-row">
                  <div className="form-group">
                    <label>{t('common:role')}</label>
                    <input
                      type="text"
                      value={formData.role}
                      onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                      className="form-input"
                      placeholder={t('customer:rolePlaceholder')}
                    />
                  </div>
                  <div className="form-group">
                    <label>{t('customer:experienceYears')}</label>
                    <input
                      type="number"
                      value={formData.experience_years}
                      onChange={(e) => setFormData({ ...formData, experience_years: e.target.value })}
                      className="form-input"
                    />
                  </div>
                </div>
              )}

              {formData.customer_type === 'elder' && (
                <div className="form-group">
                  <label>{t('customer:mobilityLevel')}</label>
                  <select
                    value={formData.mobility_level}
                    onChange={(e) => setFormData({ ...formData, mobility_level: e.target.value })}
                    className="form-input"
                  >
                    {Object.entries(mobilityLabels).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                  {t('common:cancel')}
                </button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? t('common:saving') : t('common:save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="customer-grid">
        {loading && !customers.length ? (
          <div className="loading-state">{t('common:loading')}</div>
        ) : filteredCustomers.length === 0 ? (
          <div className="empty-state">
            <Users size={48} />
            <p>{t('customer:noCustomers')}</p>
          </div>
        ) : (
          filteredCustomers.map((customer) => (
            <div key={customer.id} className="customer-card">
              <div className="customer-card-header">
                <div className="customer-type-badge">
                  {customer.customer_type === 'caregiver' ? (
                    <UserCheck size={16} />
                  ) : (
                    <Heart size={16} />
                  )}
                  <span>{customerTypeLabels[customer.customer_type] || customer.customer_type}</span>
                </div>
                <div className="customer-actions">
                  <button
                    className="icon-button"
                    onClick={() => handleEdit(customer)}
                    aria-label={t('common:edit')}
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    className="icon-button danger"
                    onClick={() => handleDelete(customer.id)}
                    aria-label={t('common:delete')}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <div className="customer-info">
                <h3>{customer.name}</h3>
                {customer.name_ja && <p className="name-ja">{customer.name_ja}</p>}
                {customer.role && (
                  <div className="info-item">
                    <span className="label">{t('common:role')}:</span>
                    <span>{customer.role}</span>
                  </div>
                )}
                {customer.experience_years && (
                  <div className="info-item">
                    <span className="label">{t('common:experience')}:</span>
                    <span>{customer.experience_years} {t('common:years')}</span>
                  </div>
                )}
                {customer.specialties && customer.specialties.length > 0 && (
                  <div className="info-item">
                    <span className="label">{t('common:specialties')}:</span>
                    <div className="tags">
                      {customer.specialties.map((spec, idx) => (
                        <span key={idx} className="tag">{spec}</span>
                      ))}
                    </div>
                  </div>
                )}
                {customer.health_conditions && customer.health_conditions.length > 0 && (
                  <div className="info-item">
                    <span className="label">{t('common:healthConditions')}:</span>
                    <div className="tags">
                      {customer.health_conditions.map((cond, idx) => (
                        <span key={idx} className="tag health">{cond}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default CustomerManagement
