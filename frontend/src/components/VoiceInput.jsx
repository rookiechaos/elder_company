import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import './VoiceInput.css'

const VoiceInput = ({ onTranscript, language = 'ja' }) => {
  const { t } = useTranslation(['voiceInput', 'common'])
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        await processAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Error accessing microphone:', err)
      alert(t('voiceInput:micAccessDenied'))
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob) => {
    setIsProcessing(true)
    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.wav')
      formData.append('language', language)

      const response = await api.post('/voice/speech-to-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const text = response.data.text || ''
      setTranscript(text)
      onTranscript?.(text)
    } catch (err) {
      console.error('Error processing audio:', err)
      alert(t('voiceInput:recognitionFailed'))
    } finally {
      setIsProcessing(false)
    }
  }

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  return (
    <div className="voice-input">
      <div className="voice-controls">
        {!isRecording ? (
          <button
            className="voice-button record"
            onClick={startRecording}
            disabled={isProcessing}
          >
            <Mic size={24} />
            <span>{t('voiceInput:startRecording')}</span>
          </button>
        ) : (
          <button
            className="voice-button stop"
            onClick={stopRecording}
          >
            <MicOff size={24} />
            <span>{t('voiceInput:stopRecording')}</span>
          </button>
        )}
        
        {isProcessing && (
          <div className="processing-indicator">
            <Loader2 size={20} className="spinning" />
            <span>{t('voiceInput:processing')}</span>
          </div>
        )}
      </div>

      {transcript && (
        <div className="transcript-result">
          <div className="transcript-label">{t('voiceInput:transcriptLabel')}</div>
          <div className="transcript-text">{transcript}</div>
        </div>
      )}
    </div>
  )
}

export default VoiceInput
