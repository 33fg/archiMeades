/**
 * Selection context - theory and dataset selection for Header selectors.
 * Frontend Component Hierarchy: TheorySelector, DatasetSelector.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'

const STORAGE_KEY = 'gravitational_selection'

interface SelectionState {
  theoryId: string | null
  observationIds: string[]
}

interface SelectionContextValue extends SelectionState {
  setTheoryId: (id: string | null) => void
  setObservationIds: (ids: string[]) => void
  toggleObservation: (id: string) => void
}

const SelectionContext = createContext<SelectionContextValue | null>(null)

function loadStored(): Partial<SelectionState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}
    return JSON.parse(raw) as Partial<SelectionState>
  } catch {
    return {}
  }
}

function saveStored(s: SelectionState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  } catch {}
}

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SelectionState>(() => ({
    theoryId: null,
    observationIds: [],
    ...loadStored(),
  }))

  useEffect(() => {
    saveStored(state)
  }, [state])

  const setTheoryId = useCallback((id: string | null) => {
    setState((s) => ({ ...s, theoryId: id }))
  }, [])

  const setObservationIds = useCallback((ids: string[]) => {
    setState((s) => ({ ...s, observationIds: ids }))
  }, [])

  const toggleObservation = useCallback((id: string) => {
    setState((s) => {
      const next = s.observationIds.includes(id)
        ? s.observationIds.filter((x) => x !== id)
        : [...s.observationIds, id]
      return { ...s, observationIds: next }
    })
  }, [])

  return (
    <SelectionContext.Provider
      value={{
        ...state,
        setTheoryId,
        setObservationIds,
        toggleObservation,
      }}
    >
      {children}
    </SelectionContext.Provider>
  )
}

export function useSelection() {
  const ctx = useContext(SelectionContext)
  if (!ctx) throw new Error('useSelection must be used within SelectionProvider')
  return ctx
}
