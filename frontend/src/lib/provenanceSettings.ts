/**
 * WO-47: Provenance settings - persisted to localStorage.
 * Function changes (provenance features) surface in Settings.
 */

const STORAGE_KEY = 'archimeades-provenance-settings'

export interface ProvenanceSettings {
  showExportButton: boolean
  verificationEnabled: boolean
}

const defaults: ProvenanceSettings = {
  showExportButton: true,
  verificationEnabled: true,
}

export function getProvenanceSettings(): ProvenanceSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<ProvenanceSettings>
      return { ...defaults, ...parsed }
    }
  } catch {
    /* ignore */
  }
  return defaults
}

export function setProvenanceSettings(settings: Partial<ProvenanceSettings>): void {
  const current = getProvenanceSettings()
  const next = { ...current, ...settings }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}
