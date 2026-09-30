import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client'

export function useVoice(onTranscript: (text: string) => void, onState: (state: 'LISTENING' | 'TRANSCRIBING' | 'ERROR') => void) {
  const recorder = useRef<MediaRecorder | null>(null)
  const stream = useRef<MediaStream | null>(null)
  const chunks = useRef<Blob[]>([])
  const [seconds, setSeconds] = useState(0)
  useEffect(() => { if (!recorder.current || recorder.current.state !== 'recording') return; const id = window.setInterval(() => setSeconds(s => s + 1), 1000); return () => window.clearInterval(id) }, [seconds > 0])
  const start = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) throw new Error('Audio recording is not supported in this browser.')
      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunks.current = []; setSeconds(0)
      recorder.current = new MediaRecorder(stream.current)
      recorder.current.ondataavailable = event => { if (event.data.size) chunks.current.push(event.data) }
      recorder.current.onstop = async () => {
        stream.current?.getTracks().forEach(track => track.stop()); onState('TRANSCRIBING')
        try { const result = await api.transcribe(new Blob(chunks.current, { type: recorder.current?.mimeType || 'audio/webm' })); onTranscript(result.transcript) }
        catch (error) { onState('ERROR'); window.dispatchEvent(new CustomEvent('riptide-error', { detail: error instanceof Error ? error.message : 'Transcription failed.' })) }
      }
      recorder.current.start(); onState('LISTENING')
    } catch (error) { onState('ERROR'); window.dispatchEvent(new CustomEvent('riptide-error', { detail: error instanceof Error ? error.message : 'Microphone access failed.' })) }
  }
  const stop = () => { if (recorder.current?.state === 'recording') recorder.current.stop() }
  return { start, stop, seconds }
}
