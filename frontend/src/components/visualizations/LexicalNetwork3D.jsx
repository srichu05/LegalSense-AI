import React, { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { Eye, EyeOff, RotateCcw, ZoomIn, ZoomOut, Info } from 'lucide-react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'

export function LexicalNetwork3D({
  term,
  candidateSenses = [],
  selectedSense = null,
  onSelectSense = null,
}) {
  const containerRef = useRef(null)
  const [selectedNodeInfo, setSelectedNodeInfo] = useState(null)
  const [showAccessibleFallback, setShowAccessibleFallback] = useState(false)
  const [autoRotate, setAutoRotate] = useState(true)

  // Track three.js internals in refs for cleanup
  const sceneRef = useRef(null)
  const rendererRef = useRef(null)
  const animFrameId = useRef(null)
  const cameraRef = useRef(null)
  const nodesRef = useRef([])

  useEffect(() => {
    if (showAccessibleFallback || !containerRef.current) return

    const container = containerRef.current
    const width = container.clientWidth || 600
    const height = 400

    // 1. Scene & Camera
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0f172a) // deep navy backdrop
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
    camera.position.set(0, 0, 18)
    cameraRef.current = camera

    // 2. Renderer
    let renderer
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(width, height)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      container.innerHTML = ''
      container.appendChild(renderer.domElement)
      rendererRef.current = renderer
    } catch (err) {
      console.warn('WebGL initialization failed, falling back to accessible 2D view:', err)
      setShowAccessibleFallback(true)
      return
    }

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
    scene.add(ambientLight)

    const pointLight = new THREE.PointLight(0xffd54f, 1.5, 100)
    pointLight.position.set(10, 15, 20)
    scene.add(pointLight)

    const pointLight2 = new THREE.PointLight(0x38bdf8, 1.2, 100)
    pointLight2.position.set(-10, -10, -15)
    scene.add(pointLight2)

    // 4. Construct Graph Data from real API candidates
    const group = new THREE.Group()
    scene.add(group)

    const nodes = []
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.6 })

    // Target Node (Center)
    const targetGeo = new THREE.SphereGeometry(1.2, 32, 32)
    const targetMat = new THREE.MeshStandardMaterial({
      color: 0xd97706, // Brass Gold
      roughness: 0.3,
      metalness: 0.6,
      emissive: 0x78350f,
      emissiveIntensity: 0.2,
    })
    const targetMesh = new THREE.Mesh(targetGeo, targetMat)
    targetMesh.position.set(0, 0, 0)
    targetMesh.userData = {
      type: 'target',
      title: term,
      description: `Target word for disambiguation (${candidateSenses.length} candidate synsets)`,
    }
    group.add(targetMesh)
    nodes.push(targetMesh)

    // Ring 1: Candidate Senses
    const candidateCount = Math.min(candidateSenses.length, 8)
    const radius1 = 7.0

    candidateSenses.slice(0, candidateCount).forEach((candidate, i) => {
      const angle = (i / candidateCount) * Math.PI * 2
      const cx = Math.cos(angle) * radius1
      const cy = Math.sin(angle) * radius1
      const cz = (Math.sin(angle * 3) * 1.5)

      const isSelected = selectedSense && selectedSense.synset_id === candidate.synset_id

      const senseGeo = new THREE.SphereGeometry(isSelected ? 0.9 : 0.7, 24, 24)
      const senseMat = new THREE.MeshStandardMaterial({
        color: isSelected ? 0x10b981 : 0x38bdf8, // emerald if selected, sky blue if candidate
        roughness: 0.4,
        metalness: 0.4,
        emissive: isSelected ? 0x064e3b : 0x075985,
        emissiveIntensity: 0.3,
      })
      const senseMesh = new THREE.Mesh(senseGeo, senseMat)
      senseMesh.position.set(cx, cy, cz)
      senseMesh.userData = {
        type: 'candidate',
        title: candidate.synset_id,
        candidate,
        description: `Rank #${candidate.rank} (Score: ${candidate.score.toFixed(4)}): ${candidate.definition}`,
      }
      group.add(senseMesh)
      nodes.push(senseMesh)

      // Line from center to candidate
      const points = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(cx, cy, cz)]
      const lineGeo = new THREE.BufferGeometry().setFromPoints(points)
      const line = new THREE.Line(lineGeo, lineMaterial)
      group.add(line)

      // Ring 2: Lexical Relations (Synonyms, Hypernyms)
      const relations = candidate.relations || {}
      const relItems = [
        ...(relations.synonyms || []).slice(0, 2).map(name => ({ name, type: 'synonym', color: 0xa855f7 })),
        ...(relations.hypernyms || []).slice(0, 2).map(name => ({ name, type: 'hypernym', color: 0x3b82f6 })),
      ]

      relItems.forEach((rel, rIdx) => {
        const relAngle = angle + (rIdx - 0.5) * 0.4
        const rx = cx + Math.cos(relAngle) * 3.0
        const ry = cy + Math.sin(relAngle) * 3.0
        const rz = cz + (rIdx === 0 ? 0.8 : -0.8)

        const relGeo = new THREE.SphereGeometry(0.35, 16, 16)
        const relMat = new THREE.MeshStandardMaterial({
          color: rel.color,
          roughness: 0.5,
          metalness: 0.2,
        })
        const relMesh = new THREE.Mesh(relGeo, relMat)
        relMesh.position.set(rx, ry, rz)
        relMesh.userData = {
          type: rel.type,
          title: rel.name,
          parent: candidate.synset_id,
          description: `${rel.type === 'hypernym' ? 'Hypernym of' : 'Synonym of'} ${candidate.synset_id}`,
        }
        group.add(relMesh)
        nodes.push(relMesh)

        // Line from sense to relation
        const relPoints = [new THREE.Vector3(cx, cy, cz), new THREE.Vector3(rx, ry, rz)]
        const relLineGeo = new THREE.BufferGeometry().setFromPoints(relPoints)
        const relLine = new THREE.Line(relLineGeo, lineMaterial)
        group.add(relLine)
      })
    })

    nodesRef.current = nodes

    // 5. Raycasting for Click / Node Inspection
    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()

    const onPointerDown = event => {
      const rect = renderer.domElement.getBoundingClientRect()
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(nodes)
      if (intersects.length > 0) {
        const clicked = intersects[0].object.userData
        setSelectedNodeInfo(clicked)
        if (clicked.candidate && onSelectSense) {
          onSelectSense(clicked.candidate)
        }
      }
    }

    renderer.domElement.addEventListener('pointerdown', onPointerDown)

    // 6. Animation Loop with Reduced-Motion Guard
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let isDragging = false
    let prevMouseX = 0
    let prevMouseY = 0

    const onMouseDown = e => {
      isDragging = true
      prevMouseX = e.clientX
      prevMouseY = e.clientY
    }
    const onMouseMove = e => {
      if (!isDragging) return
      const deltaX = e.clientX - prevMouseX
      const deltaY = e.clientY - prevMouseY
      group.rotation.y += deltaX * 0.008
      group.rotation.x += deltaY * 0.008
      prevMouseX = e.clientX
      prevMouseY = e.clientY
    }
    const onMouseUp = () => {
      isDragging = false
    }

    renderer.domElement.addEventListener('mousedown', onMouseDown)
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)

    const animate = () => {
      animFrameId.current = requestAnimationFrame(animate)

      if (autoRotate && !isDragging && !prefersReducedMotion) {
        group.rotation.y += 0.002
      }

      renderer.render(scene, camera)
    }

    animate()

    // Resize handler
    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current || !cameraRef.current) return
      const w = containerRef.current.clientWidth
      cameraRef.current.aspect = w / height
      cameraRef.current.updateProjectionMatrix()
      rendererRef.current.setSize(w, height)
    }
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animFrameId.current)
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('mouseup', onMouseUp)
      if (renderer.domElement) {
        renderer.domElement.removeEventListener('pointerdown', onPointerDown)
        renderer.domElement.removeEventListener('mousedown', onMouseDown)
      }
      renderer.dispose()
      scene.clear()
    }
  }, [term, candidateSenses, selectedSense, showAccessibleFallback, autoRotate])

  const handleResetCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.position.set(0, 0, 18)
      cameraRef.current.lookAt(0, 0, 0)
    }
    if (sceneRef.current) {
      const group = sceneRef.current.children.find(c => c.type === 'Group')
      if (group) {
        group.rotation.set(0, 0, 0)
      }
    }
  }

  const handleZoom = delta => {
    if (cameraRef.current) {
      cameraRef.current.position.z = Math.max(8, Math.min(30, cameraRef.current.position.z + delta))
    }
  }

  if (candidateSenses.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-900 text-slate-300 rounded-lg border border-slate-800">
        <p className="text-sm">No candidate senses available to generate lexical network.</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0f172a] overflow-hidden text-slate-100 shadow-lg">
      {/* Header & Controls */}
      <div className="px-4 py-3 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 bg-slate-950/60">
        <div className="flex items-center gap-2">
          <span className="font-serif font-bold text-sm text-amber-400">Lexical Network 3D:</span>
          <span className="font-mono text-xs text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            "{term}"
          </span>
          <Badge variant="navy" className="text-[10px]">
            {candidateSenses.length} Senses Mapped
          </Badge>
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setAutoRotate(!autoRotate)}
            className="text-slate-300 hover:text-white hover:bg-slate-800 h-7 text-xs"
          >
            {autoRotate ? 'Pause Rotation' : 'Auto Rotate'}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleZoom(-3)}
            className="text-slate-300 hover:text-white hover:bg-slate-800 h-7 w-7 p-0"
            title="Zoom in"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleZoom(3)}
            className="text-slate-300 hover:text-white hover:bg-slate-800 h-7 w-7 p-0"
            title="Zoom out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleResetCamera}
            className="text-slate-300 hover:text-white hover:bg-slate-800 h-7 w-7 p-0"
            title="Reset View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setShowAccessibleFallback(!showAccessibleFallback)}
            className="h-7 text-xs ml-1"
          >
            {showAccessibleFallback ? (
              <>
                <Eye className="w-3 h-3 mr-1" /> View 3D WebGL
              </>
            ) : (
              <>
                <EyeOff className="w-3 h-3 mr-1" /> View 2D Table
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Canvas or Fallback */}
      {!showAccessibleFallback ? (
        <div className="relative">
          <div ref={containerRef} className="w-full h-[400px] cursor-grab active:cursor-grabbing select-none" />

          {/* Node Inspection Card overlay */}
          {selectedNodeInfo && (
            <div className="absolute bottom-3 left-3 right-3 sm:right-auto sm:max-w-md bg-slate-900/90 backdrop-blur-md p-3.5 rounded-lg border border-slate-700 text-xs shadow-xl transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono font-bold text-amber-400 text-sm">
                  {selectedNodeInfo.title}
                </span>
                <Badge variant="outline" className="text-[10px] bg-slate-800 text-slate-300 border-slate-600">
                  {selectedNodeInfo.type}
                </Badge>
              </div>
              <p className="text-slate-300 leading-relaxed font-sans">{selectedNodeInfo.description}</p>
            </div>
          )}

          {/* Legend */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-2 text-[10px] bg-slate-950/70 p-2 rounded border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Target Word
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Selected Sense
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400 inline-block" /> Candidate Synset
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" /> Hypernym
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block" /> Synonym
            </span>
          </div>
        </div>
      ) : (
        /* Accessible 2D Table Fallback */
        <div className="p-4 bg-slate-900 text-slate-200 text-xs max-h-[400px] overflow-y-auto">
          <div className="flex items-center gap-2 mb-3 text-amber-400 font-semibold">
            <Info className="w-4 h-4" />
            <span>Accessible Lexical Relation Table (2D Representation)</span>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="py-2 px-3">Rank / Synset</th>
                <th className="py-2 px-3">Score</th>
                <th className="py-2 px-3">Definition</th>
                <th className="py-2 px-3">Relations</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-[11px]">
              {candidateSenses.map(c => (
                <tr key={c.synset_id} className="hover:bg-slate-800/50">
                  <td className="py-2 px-3 font-semibold text-sky-400">
                    #{c.rank} {c.synset_id}
                  </td>
                  <td className="py-2 px-3 text-emerald-400 font-bold">{c.score.toFixed(4)}</td>
                  <td className="py-2 px-3 font-sans text-slate-300 max-w-xs">{c.definition}</td>
                  <td className="py-2 px-3 font-sans text-slate-400">
                    {c.relations?.synonyms?.length ? `Syn: ${c.relations.synonyms.join(', ')}` : ''}
                    {c.relations?.hypernyms?.length ? ` | Hyp: ${c.relations.hypernyms.join(', ')}` : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
