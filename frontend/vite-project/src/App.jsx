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
  const [darkMode, setDarkMode] = useState(() => {
    try {
      const saved = localStorage.getItem('darkMode')
      return saved ? JSON.parse(saved) : false
    } catch (error) {
      console.warn('Failed to parse darkMode from localStorage:', error)
      return false
    }
  })
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('theme')
      return saved ? JSON.parse(saved) : 'default'
    } catch (error) {
      console.warn('Failed to parse theme from localStorage:', error)
      return 'default'
    }
  })
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

  const themes = [
    { value: 'default', label: 'Default', icon: '🎨' },
    { value: 'ocean', label: 'Ocean', icon: '🌊' },
    { value: 'sunset', label: 'Sunset', icon: '🌅' },
    { value: 'forest', label: 'Forest', icon: '🌲' },
    { value: 'purple', label: 'Purple', icon: '💜' },
    { value: 'cyber', label: 'Cyber', icon: '🤖' }
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

  // Save dark mode preference
  useEffect(() => {
    try {
      localStorage.setItem('darkMode', JSON.stringify(darkMode))
    } catch (error) {
      console.warn('Failed to save darkMode to localStorage:', error)
    }
  }, [darkMode])

  // Save theme preference
  useEffect(() => {
    try {
      localStorage.setItem('theme', JSON.stringify(theme))
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error)
    }
  }, [theme])

  // Scroll detection for header glow
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY
      setIsScrolled(scrollPosition > 20)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev)
  }

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
  }

  // Get theme-based background gradient
  const getThemeBackground = () => {
    if (darkMode) {
      switch (theme) {
        case 'ocean':
          return 'bg-gradient-to-br from-blue-900 via-cyan-900 to-teal-900'
        case 'sunset':
          return 'bg-gradient-to-br from-orange-900 via-red-900 to-pink-900'
        case 'forest':
          return 'bg-gradient-to-br from-green-900 via-emerald-900 to-teal-900'
        case 'purple':
          return 'bg-gradient-to-br from-purple-900 via-indigo-900 to-pink-900'
        case 'cyber':
          return 'bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800'
        default:
          return 'bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800'
      }
    } else {
      switch (theme) {
        case 'ocean':
          return 'bg-gradient-to-br from-blue-100 via-cyan-50 to-teal-100'
        case 'sunset':
          return 'bg-gradient-to-br from-orange-100 via-pink-50 to-red-100'
        case 'forest':
          return 'bg-gradient-to-br from-green-100 via-emerald-50 to-teal-100'
        case 'purple':
          return 'bg-gradient-to-br from-purple-100 via-indigo-50 to-pink-100'
        case 'cyber':
          return 'bg-gradient-to-br from-gray-100 via-white to-gray-200'
        default:
          return 'bg-gradient-to-br from-gray-100 via-white to-gray-200'
      }
    }
  }

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
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType || 'audio/webm' })
          await processAudio(audioBlob)
        }
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
    if (!audioBlob || audioBlob.size === 0) {
      setError('No audio data to process')
      setIsProcessing(false)
      return
    }

    setIsProcessing(true)
    const startTime = Date.now()

    try {
      const formData = new FormData()
      const fileExtension = audioBlob.type.includes('webm') ? 'webm' : audioBlob.type.includes('ogg') ? 'ogg' : 'wav'
      formData.append('audio', audioBlob, `recording.${fileExtension}`)
      formData.append('tone', tone)

      const response = await fetch(`${API_BASE_URL}/process/full`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText)
        throw new Error(`Server error: ${response.status} - ${errorText}`)
      }

      let data
      try {
        data = await response.json()
      } catch (parseError) {
        throw new Error('Failed to parse server response')
      }

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
    <div className={`min-h-screen flex flex-col transition-all duration-500 ease-in-out ${getThemeBackground()}`}>
      {/* Header */}
      <header className={`sticky top-0 z-50 backdrop-blur-md border-b transition-all duration-500 ease-in-out transform ${
        isScrolled
          ? 'scale-[0.98] -translate-y-1'
          : 'scale-100 translate-y-0'
      } ${
        isScrolled
          ? darkMode
            ? 'bg-gradient-to-b from-slate-900/15 via-gray-900/12 to-slate-800/10 border-white/8 shadow-2xl shadow-purple-500/20'
            : 'bg-gradient-to-b from-gray-100/15 via-white/12 to-gray-200/10 border-white/20 shadow-2xl shadow-indigo-500/20'
          : darkMode
            ? 'bg-gradient-to-b from-slate-900/8 via-gray-900/6 to-slate-800/5 border-white/5 shadow-lg'
            : 'bg-gradient-to-b from-gray-100/8 via-white/6 to-gray-200/5 border-white/15 shadow-lg'
      }`}>
        <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 bg-transparent transition-all duration-500 ease-in-out ${
          isScrolled ? 'py-4' : 'py-6'
        }`}>
          {/* Theme Controls */}
          <div className="absolute top-4 right-4 sm:right-6 lg:right-8 flex flex-col items-end gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleDarkMode}
              className={`relative w-14 h-7 rounded-full transition-all duration-500 ease-in-out ${
                darkMode ? 'bg-indigo-600' : 'bg-gray-300'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                darkMode ? 'focus:ring-indigo-500' : 'focus:ring-gray-400'
              } shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95`}
              aria-label="Toggle dark mode"
            >
              <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-500 ease-in-out ${
                darkMode ? 'translate-x-7' : 'translate-x-0'
              }`}>
                <span className={`absolute inset-0 flex items-center justify-center text-xs transition-opacity duration-300 ${
                  darkMode ? 'opacity-0' : 'opacity-100'
                }`}>☀️</span>
                <span className={`absolute inset-0 flex items-center justify-center text-xs transition-opacity duration-300 ${
                  darkMode ? 'opacity-100' : 'opacity-0'
                }`}>🌙</span>
              </div>
            </button>
            
            {/* Theme Selector */}
            <select
              value={theme}
              onChange={(e) => handleThemeChange(e.target.value)}
              className={`px-3 py-1.5 text-xs rounded-lg font-medium cursor-pointer transition-all duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-1 shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95 backdrop-blur-sm border ${
                darkMode
                  ? 'bg-gray-800/80 text-gray-200 border-gray-600/50 focus:ring-indigo-400'
                  : 'bg-white/80 text-gray-700 border-gray-300/50 focus:ring-indigo-500'
              }`}
              aria-label="Select theme"
            >
              {themes.map(t => (
                <option key={t.value} value={t.value} className={darkMode ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-700'}>
                  {t.icon} {t.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className={`text-center bg-transparent backdrop-blur-sm rounded-2xl transition-all duration-500 ease-in-out ${
            isScrolled ? 'p-4' : 'p-6'
          } ${
            darkMode
              ? 'shadow-[0_8px_32px_0_rgba(0,0,0,0.3)] border border-white/5'
              : 'shadow-[0_8px_32px_0_rgba(31,38,135,0.2)] border border-white/10'
          }`}>
            <h1 className={`font-bold mb-2 flex items-center justify-center gap-3 transition-all duration-500 ease-in-out ${
              isScrolled 
                ? 'text-2xl sm:text-3xl mb-1 scale-95' 
                : 'text-4xl sm:text-5xl scale-100'
            }`}>
              <span className={`drop-shadow-2xl animate-bounce-slow transition-all duration-500 ${
                isScrolled ? 'text-3xl' : 'text-5xl'
              } ${
                darkMode 
                  ? 'filter drop-shadow-[0_0_15px_rgba(147,51,234,0.6)]' 
                  : 'filter drop-shadow-[0_0_15px_rgba(99,102,241,0.4)]'
              }`}>🎤</span>
              <span className="text-gradient bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent hover:animate-bulge transition-all duration-300 cursor-default inline-block drop-shadow-lg">
                Intelligent Speech Dictation Engine
              </span>
            </h1>
            <p className={`animate-slide-down opacity-100 hover:animate-bulge hover:scale-110 hover:font-semibold hover:drop-shadow-2xl active:scale-105 transition-all duration-500 ease-in-out cursor-pointer select-none font-medium drop-shadow-md ${
              isScrolled ? 'text-sm opacity-80' : 'text-lg opacity-100'
            } ${
              darkMode
                ? 'text-gray-300 hover:text-white'
                : 'text-gray-700 hover:text-gray-900'
            }`}>
              Real-time speech-to-text with intelligent processing
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 bg-transparent">
        {/* Controls Section */}
        <div className={`rounded-2xl shadow-2xl p-6 flex flex-col sm:flex-row justify-between items-center gap-4 animate-scale-in transition-all duration-500 ease-in-out ${
          darkMode
            ? 'bg-gray-800/80 backdrop-blur-lg border border-gray-700/50'
            : 'glass border border-gray-200/50'
        }`}>
          {/* Left Side - Heading */}
          <h2 className={`text-xl sm:text-2xl font-bold transition-all duration-300 ease-out cursor-default inline-block transform origin-left ${
            darkMode ? 'text-gray-200' : 'text-gray-800'
          } hover:scale-110 hover:tracking-widest hover:drop-shadow-2xl hover:brightness-110 hover:-translate-y-1`}>
            Speech Dictation
          </h2>

          {/* Right Side - Controls */}
          <div className="flex flex-wrap items-center gap-3 justify-end w-full sm:w-auto">
            {isRecording && (
              <button
                onClick={stopRecording}
                className="px-6 py-3 bg-gradient-to-r from-pink-500 to-red-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:shadow-pink-500/50 transform hover:scale-110 hover:-translate-y-1 active:scale-95 transition-all duration-300 ease-in-out flex items-center gap-2 animate-pulse hover:brightness-110"
              >
                <span className="text-xl transition-transform duration-300 hover:rotate-12">⏹️</span>
                <span className="transition-all duration-300">Stop Recording ({formatTime(recordingTime)})</span>
              </button>
            )}

            <div className="flex items-center gap-2">
              <label htmlFor="tone-select" className={`font-semibold transition-colors duration-500 whitespace-nowrap ${
                darkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                Tone/Style:
              </label>
              <select
                id="tone-select"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                disabled={isRecording || isProcessing}
                className={`px-4 py-2.5 border-2 rounded-lg font-medium cursor-pointer transition-all duration-300 ease-in-out hover:border-indigo-400 hover:shadow-md hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none ${
                  darkMode
                    ? 'border-gray-600 text-gray-200 bg-gray-700/50'
                    : 'border-gray-200 text-gray-700 bg-white'
                }`}
              >
                {tones.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <button
              onClick={clearAll}
              disabled={isRecording || isProcessing}
              className={`px-6 py-3 font-semibold rounded-xl border-2 transform hover:scale-110 hover:-translate-y-1 active:scale-95 transition-all duration-300 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none hover:shadow-lg ${
                darkMode
                  ? 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600 hover:border-gray-500'
                  : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 hover:border-gray-300'
              }`}
            >
              Clear
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className={`p-4 rounded-xl flex items-center gap-3 animate-slide-down shadow-lg transition-all duration-500 ease-in-out ${
            darkMode
              ? 'bg-red-900/30 border-2 border-red-700/50 text-red-300 backdrop-blur-sm'
              : 'glass bg-red-50 border-2 border-red-200 text-red-700'
          }`}>
            <span className="text-2xl">⚠️</span>
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Latency Metric */}
        {latency !== null && (
          <div className={`rounded-xl shadow-xl p-4 flex flex-wrap items-center gap-4 animate-fade-in transition-all duration-500 ease-in-out ${
            darkMode
              ? 'bg-gray-800/80 backdrop-blur-lg border border-gray-700/50'
              : 'glass'
          }`}>
            <span className={`font-semibold transition-colors duration-500 ${
              darkMode ? 'text-gray-300' : 'text-gray-600'
            }`}>Processing Latency:</span>
            <span className={`text-2xl font-bold transition-colors duration-500 ${
              latency <= 1500 
                ? darkMode ? 'text-green-400' : 'text-green-600'
                : darkMode ? 'text-yellow-400' : 'text-yellow-600'
            }`}>
              {latency} ms
            </span>
            {latency <= 1500 && (
              <span className={`px-3 py-1 rounded-lg text-sm font-semibold animate-scale-in transition-all duration-500 ${
                darkMode
                  ? 'bg-green-500/80 text-white border border-green-400/50'
                  : 'bg-green-500 text-white'
              }`}>
                ✓ Within Target
              </span>
            )}
          </div>
        )}

        {/* Comparison Section */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-6 items-start animate-fade-in">
          {/* Raw Transcript Panel */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-red-500 via-pink-500 to-orange-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-300"></div>
            <div className={`relative rounded-2xl shadow-2xl overflow-hidden flex flex-col min-h-[450px] animate-slide-up transition-all duration-500 ease-in-out ${
              darkMode
                ? 'bg-gray-800/90 backdrop-blur-lg border border-red-500/30'
                : 'glass border border-red-200/50'
            }`}>
              {/* Header */}
              <div className="relative bg-gradient-to-r from-red-600 via-pink-600 to-rose-600 text-white p-5 flex justify-between items-center shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
                    <span className="text-xl">📝</span>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold tracking-tight">Raw Transcript</h2>
                    <p className="text-xs text-white/80 font-medium">Unprocessed STT Output</p>
                  </div>
                </div>
                {rawTranscript && (
                  <button
                    onClick={() => copyToClipboard(rawTranscript, 'raw')}
                    className="p-2.5 rounded-lg bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all duration-300 ease-in-out transform hover:scale-110 hover:rotate-6 active:scale-95 shadow-lg border border-white/20"
                    title="Copy to clipboard"
                  >
                    <span className="inline-block transition-transform duration-300 text-lg">
                      {copied === 'raw' ? '✓' : '📋'}
                    </span>
                  </button>
                )}
              </div>
              
              {/* Content Area */}
              <div className={`flex-1 p-6 border-t overflow-y-auto scrollbar-thin transition-all duration-500 ease-in-out ${
                darkMode
                  ? 'bg-gradient-to-br from-red-950/20 via-pink-950/10 to-orange-950/10 border-red-500/20'
                  : 'bg-gradient-to-br from-red-50 via-pink-50/30 to-orange-50/20 border-red-200/30'
              }`}>
                {rawTranscript ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-md border transition-all duration-500 ${
                        darkMode
                          ? 'bg-red-900/30 text-red-300 border-red-700/50'
                          : 'bg-red-100 text-red-700 border-red-200'
                      }`}>
                        {rawTranscript && rawTranscript.trim() ? rawTranscript.trim().split(/\s+/).length : 0} words
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-md border transition-all duration-500 ${
                        darkMode
                          ? 'bg-red-900/30 text-red-300 border-red-700/50'
                          : 'bg-red-100 text-red-700 border-red-200'
                      }`}>
                        {rawTranscript.length} chars
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className={`text-base leading-7 whitespace-pre-wrap break-words font-medium tracking-wide transition-colors duration-500 ${
                        darkMode ? 'text-gray-200' : 'text-gray-800'
                      }`}>
                        {rawTranscript}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full py-16">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-red-100 to-pink-100 flex items-center justify-center mb-4 shadow-inner">
                      <span className="text-4xl opacity-50">🎤</span>
                    </div>
                    <p className={`italic text-center font-medium transition-colors duration-500 ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    }`}>
                      Raw speech-to-text output will appear here...
                    </p>
                    <p className={`text-sm mt-2 transition-colors duration-500 ${
                      darkMode ? 'text-gray-500' : 'text-gray-400'
                    }`}>Start recording to see transcription</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Arrow Indicator */}
          <div className="hidden lg:flex items-center justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-green-500 rounded-full blur-xl opacity-20 animate-pulse"></div>
              <div className={`relative text-6xl drop-shadow-2xl animate-pulse-slow transform hover:scale-125 transition-all duration-500 filter ${
                darkMode
                  ? 'text-gray-300 drop-shadow-[0_0_20px_rgba(147,51,234,0.5)]'
                  : 'text-gray-700 drop-shadow-[0_0_20px_rgba(0,0,0,0.3)]'
              }`}>
                →
              </div>
            </div>
          </div>
          <div className="lg:hidden flex items-center justify-center py-2">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-green-500 rounded-full blur-xl opacity-20 animate-pulse"></div>
              <div className={`relative text-4xl drop-shadow-2xl animate-pulse-slow transform rotate-90 transition-all duration-500 ${
                darkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                ↓
              </div>
            </div>
          </div>

          {/* Processed Text Panel */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-300"></div>
            <div className={`relative rounded-2xl shadow-2xl overflow-hidden flex flex-col min-h-[450px] animate-slide-up transition-all duration-500 ease-in-out ${
              darkMode
                ? 'bg-gray-800/90 backdrop-blur-lg border border-green-500/30'
                : 'glass border border-green-200/50'
            }`}>
              {/* Header */}
              <div className="relative bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 text-white p-5 flex justify-between items-center shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center">
                    <span className="text-xl">✨</span>
                  </div>
      <div>
                    <h2 className="text-xl font-bold tracking-tight">Processed Text</h2>
                    <p className="text-xs text-white/80 font-medium">Cleaned & Formatted</p>
                  </div>
      </div>
                {processedText && (
                  <button
                    onClick={() => copyToClipboard(processedText, 'processed')}
                    className="p-2.5 rounded-lg bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all duration-300 ease-in-out transform hover:scale-110 hover:rotate-6 active:scale-95 shadow-lg border border-white/20"
                    title="Copy to clipboard"
                  >
                    <span className="inline-block transition-transform duration-300 text-lg">
                      {copied === 'processed' ? '✓' : '📋'}
                    </span>
        </button>
                )}
              </div>
              
              {/* Content Area */}
              <div className={`flex-1 p-6 border-t overflow-y-auto scrollbar-thin transition-all duration-500 ease-in-out ${
                darkMode
                  ? 'bg-gradient-to-br from-green-950/20 via-emerald-950/10 to-teal-950/10 border-green-500/20'
                  : 'bg-gradient-to-br from-green-50 via-emerald-50/30 to-teal-50/20 border-green-200/30'
              }`}>
                {isProcessing ? (
                  <div className="flex flex-col items-center justify-center h-full py-16 gap-4">
                    <div className="relative">
                      <div className={`w-16 h-16 border-4 rounded-full animate-spin shadow-lg transition-colors duration-500 ${
                        darkMode
                          ? 'border-green-800 border-t-green-400'
                          : 'border-green-200 border-t-green-600'
                      }`}></div>
                      <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-emerald-400 rounded-full animate-spin transition-colors duration-500" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
                    </div>
                    <div className="text-center">
                      <p className={`font-semibold text-lg transition-colors duration-500 ${
                        darkMode ? 'text-gray-200' : 'text-gray-700'
                      }`}>Processing...</p>
                      <p className={`text-sm mt-1 transition-colors duration-500 ${
                        darkMode ? 'text-gray-400' : 'text-gray-500'
                      }`}>Cleaning and formatting text</p>
                    </div>
                  </div>
                ) : processedText ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-md border transition-all duration-500 ${
                        darkMode
                          ? 'bg-green-900/30 text-green-300 border-green-700/50'
                          : 'bg-green-100 text-green-700 border-green-200'
                      }`}>
                        {processedText && processedText.trim() ? processedText.trim().split(/\s+/).length : 0} words
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-md border transition-all duration-500 ${
                        darkMode
                          ? 'bg-green-900/30 text-green-300 border-green-700/50'
                          : 'bg-green-100 text-green-700 border-green-200'
                      }`}>
                        {processedText.length} chars
                      </span>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-md border flex items-center gap-1 transition-all duration-500 ${
                        darkMode
                          ? 'bg-emerald-900/30 text-emerald-300 border-emerald-700/50'
                          : 'bg-emerald-100 text-emerald-700 border-emerald-200'
                      }`}>
                        <span>✓</span> Ready
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className={`text-base leading-7 whitespace-pre-wrap break-words font-medium tracking-wide transition-colors duration-500 ${
                        darkMode ? 'text-gray-200' : 'text-gray-800'
                      }`}>
                        {processedText}
        </p>
      </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full py-16">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-100 to-emerald-100 flex items-center justify-center mb-4 shadow-inner">
                      <span className="text-4xl opacity-50">✨</span>
                    </div>
                    <p className={`italic text-center font-medium transition-colors duration-500 ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    }`}>
                      Cleaned, formatted, and tone-adjusted text will appear here...
                    </p>
                    <p className={`text-sm mt-2 transition-colors duration-500 ${
                      darkMode ? 'text-gray-500' : 'text-gray-400'
                    }`}>Processed output will show here</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Section */}
        {processedText && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-fade-in">
            <div className={`rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl ${
              darkMode
                ? 'bg-gray-800/80 backdrop-blur-lg border border-gray-700/50'
                : 'glass'
            }`}>
              <div className={`text-sm font-medium mb-2 transition-colors duration-500 ${
                darkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>Raw Length</div>
              <div className={`text-3xl font-bold transition-all duration-500 hover:scale-110 ${
                darkMode ? 'text-indigo-400' : 'text-indigo-600'
              }`}>{rawTranscript.length} chars</div>
            </div>
            <div className={`rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl ${
              darkMode
                ? 'bg-gray-800/80 backdrop-blur-lg border border-gray-700/50'
                : 'glass'
            }`}>
              <div className={`text-sm font-medium mb-2 transition-colors duration-500 ${
                darkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>Processed Length</div>
              <div className={`text-3xl font-bold transition-all duration-500 hover:scale-110 ${
                darkMode ? 'text-green-400' : 'text-green-600'
              }`}>{processedText.length} chars</div>
            </div>
            <div className={`rounded-xl shadow-xl p-6 text-center transform hover:scale-110 hover:-translate-y-2 transition-all duration-300 ease-in-out cursor-default hover:shadow-2xl ${
              darkMode
                ? 'bg-gray-800/80 backdrop-blur-lg border border-gray-700/50'
                : 'glass'
            }`}>
              <div className={`text-sm font-medium mb-2 transition-colors duration-500 ${
                darkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>Reduction</div>
              <div className={`text-3xl font-bold transition-all duration-500 hover:scale-110 ${
                darkMode ? 'text-purple-400' : 'text-purple-600'
              }`}>
                {rawTranscript.length > 0 && processedText.length >= 0
                  ? `${Math.round((1 - processedText.length / rawTranscript.length) * 100)}%`
                  : '0%'}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className={`border-t py-4 mt-auto transition-all duration-500 ease-in-out ${
        darkMode
          ? 'bg-gray-900/50 backdrop-blur-md border-white/10'
          : 'glass border-white/20'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm bg-transparent">
          <p className={`transition-colors duration-500 ${
            darkMode ? 'text-gray-400' : 'text-gray-600'
          }`}>Intelligent Low-Latency Speech Dictation Engine | Target: ≤1500ms latency</p>
        </div>
      </footer>
    </div>
  )
}

export default App
