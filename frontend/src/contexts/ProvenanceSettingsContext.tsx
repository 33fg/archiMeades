/**
 * WO-47: Provenance settings context - propagates to all provenance consumers.
 */

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import {
  getProvenanceSettings,
  setProvenanceSettings,
  type ProvenanceSettings,
} from '@/lib/provenanceSettings'

const Context = createContext<{
  settings: ProvenanceSettings
  update: (s: Partial<ProvenanceSettings>) => void
} | null>(null)

export function ProvenanceSettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState(getProvenanceSettings)
  const update = useCallback((next: Partial<ProvenanceSettings>) => {
    const merged = { ...getProvenanceSettings(), ...next }
    setProvenanceSettings(merged)
    setSettings(merged)
  }, [])
  return (
    <Context.Provider value={{ settings, update }}>
      {children}
    </Context.Provider>
  )
}

export function useProvenanceSettings() {
  const ctx = useContext(Context)
  return ctx ?? { settings: getProvenanceSettings(), update: () => {} }
}
