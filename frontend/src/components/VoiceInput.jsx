import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function VoiceInput({ onTranscript }) {
  const [listening, setListening] = useState(false)
  const recognitionRef = useRef(null)

  const toggle = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice input not supported in this browser. Try Chrome.')
      return
    }

    if (listening) {
      recognitionRef.current?.stop()
      setListening(false)
      return
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SR()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setListening(true)
      toast.success('Listening… speak your article')
    }

    recognition.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map(r => r[0].transcript)
        .join(' ')
      onTranscript(transcript)
    }

    recognition.onerror = (e) => {
      toast.error(`Voice error: ${e.error}`)
      setListening(false)
    }

    recognition.onend = () => setListening(false)

    recognition.start()
    recognitionRef.current = recognition
  }

  return (
    <button
      onClick={toggle}
      title="Voice Input"
      className={`relative p-2.5 rounded-xl border transition-all ${
        listening
          ? 'bg-danger/15 border-danger/40 text-danger shadow-neon-red'
          : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
      }`}
    >
      {listening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
      <AnimatePresence>
        {listening && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-danger rounded-full animate-pulse"
          />
        )}
      </AnimatePresence>
    </button>
  )
}
