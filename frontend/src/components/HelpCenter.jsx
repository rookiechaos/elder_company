import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, HelpCircle, MessageCircle, ChevronRight, ThumbsUp, ThumbsDown, X } from 'lucide-react'
import api from '../utils/api'
import './HelpCenter.css'

const HelpCenter = () => {
  const { t } = useTranslation(['helpCenter', 'common'])
  const [searchQuery, setSearchQuery] = useState('')
  const [articles, setArticles] = useState([])
  const [faqs, setFaqs] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [selectedArticle, setSelectedArticle] = useState(null)
  const [selectedFaq, setSelectedFaq] = useState(null)
  const [loading, setLoading] = useState(true)
  const [language, setLanguage] = useState('ja')

  useEffect(() => {
    loadData()
  }, [selectedCategory, language])

  const loadData = async () => {
    setLoading(true)
    try {
      const categoriesRes = await api.get('/help/categories')
      setCategories(categoriesRes.data?.categories || [])

      const articlesParams = { language }
      if (selectedCategory) articlesParams.category = selectedCategory
      const articlesRes = await api.get('/help/articles', { params: articlesParams })
      setArticles(articlesRes.data?.articles || [])

      const faqsParams = { language }
      if (selectedCategory) faqsParams.category = selectedCategory
      const faqsRes = await api.get('/help/faqs', { params: faqsParams })
      setFaqs(faqsRes.data?.faqs || [])
    } catch (err) {
      console.error('Failed to load help data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadData()
      return
    }

    setLoading(true)
    try {
      const res = await api.get('/help/search', {
        params: { q: searchQuery, language }
      })
      setArticles(res.data?.articles || [])
      setFaqs(res.data?.faqs || [])
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleArticleClick = async (articleId) => {
    try {
      const res = await api.get(`/help/articles/${articleId}`, {
        params: { language }
      })
      setSelectedArticle(res.data)
      setSelectedFaq(null)
    } catch (err) {
      console.error('Failed to load article:', err)
    }
  }

  const handleFaqClick = async (faqId) => {
    try {
      const res = await api.get(`/help/faqs/${faqId}`, {
        params: { language }
      })
      setSelectedFaq(res.data)
      setSelectedArticle(null)
    } catch (err) {
      console.error('Failed to load FAQ:', err)
    }
  }

  const handleFeedback = async (type, articleId = null, faqId = null) => {
    try {
      await api.post('/help/feedback', {
        article_id: articleId,
        faq_id: faqId,
        feedback_type: type
      })
      if (articleId && selectedArticle) {
        if (type === 'helpful') {
          setSelectedArticle({ ...selectedArticle, helpful_count: (selectedArticle.helpful_count || 0) + 1 })
        } else if (type === 'not_helpful') {
          setSelectedArticle({ ...selectedArticle, not_helpful_count: (selectedArticle.not_helpful_count || 0) + 1 })
        }
      }
      if (faqId && selectedFaq) {
        if (type === 'helpful') {
          setSelectedFaq({ ...selectedFaq, helpful_count: (selectedFaq.helpful_count || 0) + 1 })
        }
      }
    } catch (err) {
      console.error('Failed to submit feedback:', err)
    }
  }

  return (
    <div className="help-center">
      <div className="help-header">
        <h1>{t('helpCenter:title')}</h1>
        <p>{t('helpCenter:subtitle')}</p>
      </div>

      <div className="help-search">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder={t('helpCenter:searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>{t('helpCenter:searchButton')}</button>
        </div>
        <div className="language-selector">
          <button
            className={language === 'ja' ? 'active' : ''}
            onClick={() => setLanguage('ja')}
          >
            {t('helpCenter:languageJa')}
          </button>
          <button
            className={language === 'en' ? 'active' : ''}
            onClick={() => setLanguage('en')}
          >
            {t('helpCenter:languageEn')}
          </button>
        </div>
      </div>

      <div className="help-content">
        <div className="help-sidebar">
          <div className="category-filter">
            <h3>{t('helpCenter:categories')}</h3>
            <button
              className={!selectedCategory ? 'active' : ''}
              onClick={() => setSelectedCategory(null)}
            >
              {t('helpCenter:all')}
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                className={selectedCategory === cat ? 'active' : ''}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="help-main">
          {selectedArticle ? (
            <div className="article-detail">
              <button className="back-button" onClick={() => setSelectedArticle(null)}>
                <X size={20} /> {t('helpCenter:back')}
              </button>
              <h2>{selectedArticle.title}</h2>
              <div className="article-meta">
                <span>{selectedArticle.category}</span>
                <span>{t('helpCenter:views', { count: selectedArticle.view_count })}</span>
              </div>
              <div className="article-content" dangerouslySetInnerHTML={{ __html: selectedArticle.content.replace(/\n/g, '<br/>') }} />
              <div className="article-feedback">
                <p>{t('helpCenter:articleHelpful')}</p>
                <div className="feedback-buttons">
                  <button onClick={() => handleFeedback('helpful', selectedArticle.article_id)}>
                    <ThumbsUp size={16} /> {t('common:yes')} ({selectedArticle.helpful_count || 0})
                  </button>
                  <button onClick={() => handleFeedback('not_helpful', selectedArticle.article_id)}>
                    <ThumbsDown size={16} /> {t('common:no')} ({selectedArticle.not_helpful_count || 0})
                  </button>
                </div>
              </div>
            </div>
          ) : selectedFaq ? (
            <div className="faq-detail">
              <button className="back-button" onClick={() => setSelectedFaq(null)}>
                <X size={20} /> {t('helpCenter:back')}
              </button>
              <h2>{selectedFaq.question}</h2>
              <div className="faq-content" dangerouslySetInnerHTML={{ __html: selectedFaq.answer.replace(/\n/g, '<br/>') }} />
              <div className="article-feedback">
                <p>{t('helpCenter:faqHelpful')}</p>
                <button onClick={() => handleFeedback('helpful', null, selectedFaq.faq_id)}>
                  <ThumbsUp size={16} /> {t('common:yes')} ({selectedFaq.helpful_count || 0})
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="help-section">
                <h2>
                  <HelpCircle size={24} /> {t('helpCenter:helpArticles')}
                </h2>
                {loading ? (
                  <div className="loading">{t('helpCenter:loading')}</div>
                ) : articles.length > 0 ? (
                  <div className="articles-list">
                    {articles.map((article) => (
                      <div
                        key={article.article_id}
                        className="article-item"
                        onClick={() => handleArticleClick(article.article_id)}
                      >
                        <div className="article-header">
                          <h3>{article.title}</h3>
                          {article.is_featured && <span className="featured">{t('helpCenter:featured')}</span>}
                        </div>
                        <div className="article-meta">
                          <span>{article.category}</span>
                          <span>{t('helpCenter:views', { count: article.view_count })}</span>
                        </div>
                        <ChevronRight size={20} className="chevron" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">{t('helpCenter:noArticles')}</div>
                )}
              </div>

              <div className="help-section">
                <h2>
                  <MessageCircle size={24} /> {t('helpCenter:faqs')}
                </h2>
                {loading ? (
                  <div className="loading">{t('helpCenter:loading')}</div>
                ) : faqs.length > 0 ? (
                  <div className="faqs-list">
                    {faqs.map((faq) => (
                      <div
                        key={faq.faq_id}
                        className="faq-item"
                        onClick={() => handleFaqClick(faq.faq_id)}
                      >
                        <div className="faq-question">
                          <h3>{faq.question}</h3>
                          {faq.is_featured && <span className="featured">{t('helpCenter:featured')}</span>}
                        </div>
                        <ChevronRight size={20} className="chevron" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">{t('helpCenter:noFaqs')}</div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default HelpCenter
