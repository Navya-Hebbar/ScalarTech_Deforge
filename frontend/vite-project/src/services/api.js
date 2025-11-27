/**
 * API service for communicating with the backend speech dictation engine
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Process audio file through the full pipeline
 * @param {Blob} audioBlob - Audio blob from MediaRecorder
 * @param {string} tone - Tone/style preference (neutral, formal, casual, concise)
 * @returns {Promise<Object>} Response with raw_transcript, processed_text, and latency
 */
export const processAudio = async (audioBlob, tone = 'neutral') => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.wav')
  formData.append('tone', tone)

  const response = await fetch(`${API_BASE_URL}/process/full`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Server error: ${response.status} - ${errorText || response.statusText}`)
  }

  return await response.json()
}

/**
 * Process text through the full pipeline
 * @param {string} text - Raw text to process
 * @param {string} tone - Tone/style preference (neutral, formal, casual, concise)
 * @returns {Promise<Object>} Response with processed_text
 */
export const processText = async (text, tone = 'neutral') => {
  const response = await fetch(`${API_BASE_URL}/process/full`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text, tone })
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Server error: ${response.status} - ${errorText || response.statusText}`)
  }

  return await response.json()
}

/**
 * Stream audio for real-time transcription
 * @param {Blob} audioChunk - Audio chunk from MediaRecorder
 * @returns {Promise<Object>} Partial or final transcript
 */
export const streamTranscript = async (audioChunk) => {
  const formData = new FormData()
  formData.append('audio', audioChunk, 'chunk.wav')

  const response = await fetch(`${API_BASE_URL}/asr/stream`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error(`Streaming error: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * Check if backend API is available
 * @returns {Promise<boolean>} True if API is reachable
 */
export const checkApiHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    })
    return response.ok
  } catch (error) {
    return false
  }
}

