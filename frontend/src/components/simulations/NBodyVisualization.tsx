/**
 * N-body particle visualization - Three.js for smooth 3D rendering.
 * Replaces Plotly with WebGL particle system, OrbitControls, frame interpolation.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import { useTheme } from '@/contexts/ThemeContext'
import { Play, Pause, RotateCcw } from 'lucide-react'
import { apiRequest } from '@/lib/api'
import { Button } from '@/components/ui/button'

interface NBodyOutputData {
  observational_dataset?: {
    particle_positions?: number[][][]  // frames × particles × [x,y,z]
    n_particles?: number
    n_steps?: number
  }
}

interface NBodyVisualizationProps {
  simulationId: string
  paramsJson: string | null
  className?: string
  fullHeight?: boolean
}

/** Normalize positions to fit in view. Returns scaled positions and scale factor. */
function normalizeFrames(
  frames: number[][][]
): { positions: Float32Array[]; scale: number } {
  let minX = Infinity
  let maxX = -Infinity
  let minY = Infinity
  let maxY = -Infinity
  let minZ = Infinity
  let maxZ = -Infinity
  for (const frame of frames) {
    for (const p of frame) {
      const x = p[0] ?? 0
      const y = p[1] ?? 0
      const z = p[2] ?? 0
      minX = Math.min(minX, x)
      maxX = Math.max(maxX, x)
      minY = Math.min(minY, y)
      maxY = Math.max(maxY, y)
      minZ = Math.min(minZ, z)
      maxZ = Math.max(maxZ, z)
    }
  }
  const range = Math.max(
    maxX - minX || 1,
    maxY - minY || 1,
    maxZ - minZ || 1,
    1e-10
  )
  const cx = (minX + maxX) / 2
  const cy = (minY + maxY) / 2
  const cz = (minZ + maxZ) / 2
  // Scale so cloud fills view: extent ±1.4, camera sees full scene
  const scale = 2.8 / range
  const positions = frames.map((frame) => {
    const arr = new Float32Array(frame.length * 3)
    for (let i = 0; i < frame.length; i++) {
      const p = frame[i]
      arr[i * 3] = ((p[0] ?? 0) - cx) * scale
      arr[i * 3 + 1] = ((p[1] ?? 0) - cy) * scale
      arr[i * 3 + 2] = ((p[2] ?? 0) - cz) * scale
    }
    return arr
  })
  return { positions, scale }
}

/** Updates scene background based on theme. */
function SceneBackground() {
  const { scene } = useThree()
  const { resolved } = useTheme()
  useEffect(() => {
    scene.background = new THREE.Color(resolved === 'dark' ? '#0f172a' : '#f8fafc')
  }, [scene, resolved])
  return null
}

function ParticleCloud({
  frames,
  frameIndex,
  playing,
  onFrameChange,
}: {
  frames: Float32Array[]
  frameIndex: number
  playing: boolean
  onFrameChange: (f: number) => void
}) {
  const pointsRef = useRef<THREE.Points>(null)
  const accumRef = useRef(0)
  const nFrames = frames.length

  useEffect(() => {
    if (!pointsRef.current || !frames[frameIndex]) return
    const geom = pointsRef.current.geometry
    geom.setAttribute('position', new THREE.BufferAttribute(frames[frameIndex], 3))
    geom.attributes.position.needsUpdate = true
  }, [frameIndex, frames])

  useFrame((_, delta) => {
    if (nFrames <= 1 || !playing) return
    accumRef.current += delta
    if (accumRef.current >= 0.08) {
      accumRef.current = 0
      onFrameChange((frameIndex + 1) % nFrames)
    }
  })

  if (!frames[0]) return null
  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[frames[0], 3]} />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#6366f1"
        transparent
        opacity={0.95}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  )
}

export function NBodyVisualization({
  simulationId,
  paramsJson,
  className = '',
  fullHeight = false,
}: NBodyVisualizationProps) {
  const [outputData, setOutputData] = useState<NBodyOutputData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isPreview, setIsPreview] = useState(false)
  const [frame, setFrame] = useState(0)
  const [playing, setPlaying] = useState(false)

  const isNbody = useMemo(() => {
    try {
      const p = paramsJson ? JSON.parse(paramsJson) : {}
      return p.observable_type === 'nbody'
    } catch {
      return false
    }
  }, [paramsJson])

  const params = useMemo(() => {
    try {
      return paramsJson ? JSON.parse(paramsJson) : {}
    } catch {
      return {}
    }
  }, [paramsJson])

  useEffect(() => {
    if (!isNbody) {
      setLoading(false)
      return
    }
    let cancelled = false
    setLoading(true)
    setError(null)
    const nParticles = params.n_particles ?? 48
    const nSteps = params.n_steps ?? 50

    const loadPreview = () =>
      apiRequest<NBodyOutputData>(
        `/api/simulations/nbody-preview?n_particles=${nParticles}&n_steps=${nSteps}&n_points=30`
      )

    const loadData = async () => {
      if (simulationId) {
        try {
          const data = await apiRequest<NBodyOutputData>(
            `/api/simulations/${simulationId}/output-data`
          )
          if (data?.observational_dataset?.particle_positions?.length) {
            return { data, isPreview: false }
          }
        } catch {
          /* fall through */
        }
      }
      const data = await loadPreview()
      return { data, isPreview: true }
    }

    loadData()
      .then(({ data, isPreview: prev }) => {
        if (!cancelled && data?.observational_dataset?.particle_positions?.length) {
          setOutputData(data)
          setIsPreview(prev)
          setFrame(0)
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e?.detail ?? 'Failed to load N-body data')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [simulationId, isNbody, params.n_particles, params.n_steps])

  const frames = outputData?.observational_dataset?.particle_positions ?? []
  const nFrames = frames.length

  const { normalizedPositions } = useMemo(() => {
    if (!nFrames) return { normalizedPositions: [] as Float32Array[] }
    const { positions } = normalizeFrames(frames)
    return { normalizedPositions: positions }
  }, [frames, nFrames])

  const handleRestart = useCallback(() => {
    setFrame(0)
    setPlaying(false)
  }, [])

  if (!isNbody) return null
  if (loading) return <p className="text-sm text-muted-foreground">Loading N-body visualization…</p>
  if (error) return <p className="text-sm text-destructive">{error}</p>
  if (!nFrames) return <p className="text-sm text-muted-foreground">No particle positions in output.</p>

  return (
    <div className={`flex min-h-0 flex-col rounded-lg border border-border bg-card p-4 ${fullHeight ? 'flex-1' : ''} ${className}`}>
      <div className="mb-2 shrink-0 flex items-center justify-between gap-2">
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            N-body particle visualization (3D)
          </p>
          {isPreview && (
            <p className="mt-0.5 text-xs text-muted-foreground">
              Live preview (simulation output unavailable)
            </p>
          )}
          <p className="mt-0.5 text-xs text-muted-foreground">
            Drag to rotate · Scroll to zoom · Use slider or Play to animate
          </p>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setPlaying((p) => !p)}
            disabled={nFrames <= 1}
            title={playing ? 'Pause' : 'Play'}
          >
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleRestart}
            title="Restart"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <div
        className={`min-h-0 w-full min-w-[320px] overflow-hidden rounded-md border border-border bg-background ${
          fullHeight ? 'min-h-[360px] flex-1' : 'h-[440px]'
        }`}
      >
        <Canvas
          camera={{ position: [1.8, 1.8, 1.8], fov: 55 }}
          gl={{ antialias: true }}
          style={{ width: '100%', height: '100%', display: 'block' }}
        >
          <SceneBackground />
          <ambientLight intensity={0.4} />
          <pointLight position={[10, 10, 10]} intensity={0.8} />
          <ParticleCloud
            frames={normalizedPositions}
            frameIndex={frame}
            playing={playing}
            onFrameChange={setFrame}
          />
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={0.8}
            maxDistance={6}
          />
        </Canvas>
      </div>
      <div className="mt-2 shrink-0 flex items-center gap-2">
        <input
          type="range"
          min={0}
          max={Math.max(0, nFrames - 1)}
          value={frame}
          onChange={(e) => {
            setFrame(Number(e.target.value))
            setPlaying(false)
          }}
          className="flex-1"
        />
        <span className="text-xs text-muted-foreground tabular-nums">
          Frame {frame + 1} / {nFrames}
        </span>
      </div>
    </div>
  )
}
