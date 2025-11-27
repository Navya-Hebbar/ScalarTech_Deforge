import { useState, useRef, useEffect } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [rawTranscript, setRawTranscript] = useState('')
  const [processedText, setProcessedText] = useState('')
  const [tone, setTone] = useState('neutral')
  const [latency, setLatency] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [recordingTime, setRecordingTime] = useState(0)
  const [copied, setCopied] = useState(null)
  const [isScrolled, setIsScrolled] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  const tones = [
    { value: 'neutral', label: 'Neutral' },
    { value: 'formal', label: 'Formal' },
    { value: 'casual', label: 'Casual' },
    { value: 'concise', label: 'Concise' }
  ]

  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [isRecording])

  // Scroll animation effect
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY
      setIsScrolled(scrollPosition > 50)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const startRecording = async () => {
    try {
      setError(null)
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
      setRecordingTime(0)
      setRawTranscript('')
      setProcessedText('')
      setLatency(null)
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.')
      console.error('Error accessing microphone:', err)
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
    const startTime = Date.now()

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')
      formData.append('tone', tone)

      const response = await fetch(`${API_BASE_URL}/process/full`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`)
      }

      const data = await response.json()
      const endTime = Date.now()
      const totalLatency = endTime - startTime

      setRawTranscript(data.raw_transcript || '')
      setProcessedText(data.processed_text || data.text || '')
      setLatency(totalLatency)
      setIsProcessing(false)
    } catch (err) {
      setError(`Processing failed: ${err.message}`)
      setIsProcessing(false)
      console.error('Error processing audio:', err)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(type)
      setTimeout(() => setCopied(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const clearAll = () => {
    setRawTranscript('')
    setProcessedText('')
    setLatency(null)
    setError(null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      {/* Header */}
      <header className={`glass shadow-xl border-b border-white/20 sticky top-0 z-50 transition-all duration-300 ease-in-out ${
        isScrolled 
          ? 'py-3 shadow-2xl backdrop-blur-xl bg-white/98 scale-[0.98]' 
          : 'py-6 scale-100'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`text-center transition-all duration-300 ease-in-out ${
            isScrolled ? 'scale-95 opacity-95' : 'scale-100 opacity-100'
          }`}>
            <h1 className={`font-bold mb-2 flex items-center justify-center gap-3 transition-all duration-300 ease-in-out ${
              isScrolled 
                ? 'text-2xl sm:text-3xl mb-1' 
                : 'text-4xl sm:text-5xl animate-fade-in'
            }`}>
              <span className={`drop-shadow-lg transition-all duration-300 ease-in-out ${
                isScrolled 
                  ? 'text-3xl animate-bounce-slow scale-90' 
                  : 'text-5xl animate-bounce-slow scale-100'
              }`}>🎤</span>
              <span className={`text-gradient bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent hover:animate-wiggle transition-all duration-300 cursor-default inline-block hover:scale-105 ${
                isScrolled ? 'opacity-90' : 'opacity-100'
              }`}>
                Intelligent Speech Dictation Engine
              </span>
            </h1>
            <p className={`text-gray-600 transition-all duration-300 ease-in-out cursor-pointer select-none ${
              isScrolled 
                ? 'text-sm opacity-0 -translate-y-2 h-0 overflow-hidden' 
                : 'text-lg animate-slide-down opacity-100 translate-y-0 h-auto animate-wobble hover:animate-wobble-intense hover:scale-110 hover:text-indigo-600 hover:font-semibold hover:drop-shadow-lg active:scale-105'
            }`}>
              Real-time speech-to-text with intelligent processing
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Controls Section */}
        <div className="glass rounded-2xl shadow-2xl p-6 flex flex-col sm:flex-row justify-between items-center gap-4 animate-scale-in">
          <div className="flex items-center gap-4">
            <label htmlFor="tone-select" className="font-semibold text-gray-700">
              Tone/Style:
            </label>
            <select
              id="tone-select"
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              disabled={isRecording || isProcessing}
              className="px-4 py-2.5 border-2 border-gray-200 rounded-lg font-medium text-gray-700 bg-white cursor-pointer transition-all duration-300 ease-in-out hover:border-indigo-400 hover:shadow-md hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none"
            >
              {tones.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3">
            {!isRecording ? (
              <button
                onClick={startRecording}
                disabled={isProcessing}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:shadow-indigo-500/50 transform hover:scale-110 hover:-translate-y-1 active:scale-95 transition-all duration-300 ease-in-out flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none hover:brightness-110"
              >
                <span className="text-xl transition-transform duration-300 hover:rotate-12">🎙️</span>
                <span className="transition-all duration-300">Start Recording</span>
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="px-6 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:shadow-pink-500/50 transform hover:scale-110 hover:-translate-y-1 active:scale-95 transition-all duration-300 ease-in-out flex items-center gap-2 animate-pulse hover:brightness-110"
              >
                <span className="text-xl transition-transform duration-300 hover:rotate-12">⏹️</span>
                <span className="transition-all duration-300">Stop Recording ({formatTime(recordingTime)})</span>
              </button>
            )}

            <button
              onClick={clearAll}
              disabled={isRecording || isProcessing}
              className="px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl border-2 border-gray-200 hover:bg-gray-200 hover:border-gray-300 transform hover:scale-110 hover:-translate-y-1 active:scale-95 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none hover:shadow-lg"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="glass bg-red-50 border-2 border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3 animate-slide-down shadow-lg">
            <span className="text-2xl">⚠️</span>
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Latency Metric */}
        {latency !== null && (
          <div className="glass rounded-xl shadow-xl p-4 flex flex-wrap items-center gap-4 animate-fade-in">
            <span className="font-semibold text-gray-600">Processing Latency:</span>
            <span className={`text-2xl font-bold ${latency <= 1500 ? 'text-green-600' : 'text-yellow-600'}`}>
              {latency} ms
            </span>
            {latency <= 1500 && (
              <span className="px-3 py-1 bg-green-500 text-white rounded-lg text-sm font-semibold animate-scale-in">
                ✓ Within Target
              </span>
            )}
          </div>
        )}

        {/* Comparison Section */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-6 items-start animate-fade-in">
          {/* Raw Transcript Panel */}
          <div className="glass rounded-2xl shadow-2xl overflow-hidden flex flex-col min-h-[400px] animate-slide-up">
            <div className="bg-gradient-to-r from-red-500 to-pink-500 text-white p-5 flex justify-between items-center">
              <h2 className="text-xl font-bold">Raw Transcript</h2>
              {rawTranscript && (
                <button
                  onClick={() => copyToClipboard(rawTranscript, 'raw')}
                  className="p-2 rounded-lg hover:bg-white/20 transition-all duration-300 ease-in-out transform hover:scale-125 hover:rotate-12 active:scale-95 hover:shadow-lg"
                  title="Copy to clipboard"
                >
                  <span className="inline-block transition-transform duration-300 hover:scale-110">
                    {copied === 'raw' ? '✓' : '📋'}
                  </span>
                </button>
              )}
            </div>
            <div className="flex-1 p-6 bg-red-50/50 border-l-4 border-red-500 overflow-y-auto scrollbar-thin">
              {rawTranscript ? (
                <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap break-words">
                  {rawTranscript}
                </p>
              ) : (
                <p className="text-gray-400 italic text-center py-8">
                  Raw speech-to-text output will appear here...
                </p>
              )}
            </div>
          </div>

          {/* Arrow Indicator */}
          <div className="hidden lg:flex items-center justify-center">
            <div className="text-6xl text-white drop-shadow-2xl animate-pulse-slow transform hover:scale-125 transition-transform duration-300">
              →
            </div>
          </div>
          <div className="lg:hidden flex items-center justify-center py-2">
            <div className="text-4xl text-white drop-shadow-2xl animate-pulse-slow transform rotate-90">
              ↓
            </div>
          </div>

          {/* Processed Text Panel */}
          <div className="glass rounded-2xl shadow-2xl overflow-hidden flex flex-col min-h-[400px] animate-slide-up">
            <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white p-5 flex justify-between items-center">
              <h2 className="text-xl font-bold">Processed Text</h2>
              {processedText && (
                <button
                  onClick={() => copyToClipboard(processedText, 'processed')}
                  className="p-2 rounded-lg hover:bg-white/20 transition-all duration-300 ease-in-out transform hover:scale-125 hover:rotate-12 active:scale-95 hover:shadow-lg"
                  title="Copy to clipboard"
                >
                  <span className="inline-block transition-transform duration-300 hover:scale-110">
                    {copied === 'processed' ? '✓' : '📋'}
                  </span>
                </button>
              )}
            </div>
            <div className="flex-1 p-6 bg-green-50/50 border-l-4 border-green-500 overflow-y-auto scrollbar-thin">
              {isProcessing ? (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                  <div className="w-12 h-12 border-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin"></div>
                  <p className="text-gray-600 font-medium">Processing...</p>
                </div>
              ) : processedText ? (
                <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap break-words">
                  {processedText}
                </p>
              ) : (
                <p className="text-gray-400 italic text-center py-8">
                  Cleaned, formatted, and tone-adjusted text will appear here...
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Statistics Section */}
        {processedText && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-fade-in">
            <div className="glass rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl">
              <div className="text-sm text-gray-600 font-medium mb-2 transition-colors duration-300">Raw Length</div>
              <div className="text-3xl font-bold text-indigo-600 transition-transform duration-300 hover:scale-110">{rawTranscript.length} chars</div>
            </div>
            <div className="glass rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl">
              <div className="text-sm text-gray-600 font-medium mb-2 transition-colors duration-300">Processed Length</div>
              <div className="text-3xl font-bold text-green-600 transition-transform duration-300 hover:scale-110">{processedText.length} chars</div>
            </div>
            <div className="glass rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl">
              <div className="text-sm text-gray-600 font-medium mb-2 transition-colors duration-300">Reduction</div>
              <div className="text-3xl font-bold text-purple-600 transition-transform duration-300 hover:scale-110">
                {rawTranscript.length > 0
                  ? `${Math.round((1 - processedText.length / rawTranscript.length) * 100)}%`
                  : '0%'}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="glass border-t border-white/20 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>Intelligent Low-Latency Speech Dictation Engine | Target: ≤1500ms latency</p>
        </div>
      </footer>
    </div>
  )
}

export default App
