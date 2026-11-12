import { useEffect, useMemo, useState } from 'react'
import { Activity, ArrowUpRight, CheckCircle2, ChevronDown, CircleAlert, FileImage, Fingerprint, Gauge, ImagePlus, Loader2, ScanFace, ShieldCheck, Sparkles, UploadCloud, X } from 'lucide-react'
import type { Analysis, CategoryResult } from './types'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const groups: Record<string,string> = { major_structure:'Facial structure', eyes:'Eyes', nose:'Nose', jaw_chin:'Jaw & chin', mouth:'Mouth & lips', upper_face:'Upper face', skin:'Skin' }

export default function App() {
  const [file,setFile]=useState<File|null>(null)
  const [preview,setPreview]=useState('')
  const [busy,setBusy]=useState(false)
  const [error,setError]=useState('')
  const [result,setResult]=useState<Analysis|null>(null)
  const [expanded,setExpanded]=useState<string|null>(null)
  const [drag,setDrag]=useState(false)

  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview)
  }, [preview])

  const grouped=useMemo(()=> {
    const out:Record<string,CategoryResult[]>={}
    result?.categories.forEach(c=>{(out[c.weight_group] ||= []).push(c)})
    return out
  },[result])

  function choose(f?:File) {
    if(!f) return
    if(!['image/jpeg','image/png','image/webp'].includes(f.type)){setError('Choose a JPG, PNG, or WEBP image.');return}
    if(f.size>10*1024*1024){setError('Image must be smaller than 10 MB.');return}
    setFile(f);setPreview(URL.createObjectURL(f));setResult(null);setError('')
  }
  async function analyze() {
    if(!file)return
    setBusy(true);setError('');setResult(null)
    try {
      const body=new FormData();body.append('file',file)
      const res=await fetch(`${API}/analyze`,{method:'POST',body})
      const data=await res.json()
      if(!res.ok) throw new Error(data.detail || 'Analysis failed. Check that the INFINITY backend is running.')
      setResult(data)
    } catch(e) {setError(e instanceof Error?e.message:'Unable to connect to the analysis server.')}
    finally {setBusy(false)}
  }
  function reset(){setFile(null);setPreview('');setResult(null);setError('')}
  const score=result?.overall_score

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="#"><span className="brand-mark"><Fingerprint size={21}/></span><span>INFINITY<span className="brand-dot">.</span></span></a>
      <nav><a href="#how">How it works</a><a href="#method">Methodology</a><span className="api-status"><i/> Reference analysis</span></nav>
    </header>

    <main>
      <section className="hero">
        <div className="eyebrow"><span className="eyebrow-line"/> MULTI-CATEGORY FACIAL ANALYSIS <span className="eyebrow-line"/></div>
        <h1>Understand your features.<br/><em>One reference at a time.</em></h1>
        <p className="hero-copy">A category-by-category facial analysis system. Each measurable feature is compared with its own dedicated reference — never one generic face score.</p>
        <div className="hero-tags"><span><ScanFace size={14}/> 34 categories</span><span><Activity size={14}/> Landmark-based</span><span><ShieldCheck size={14}/> Transparent scoring</span></div>
      </section>

      <section className="workspace">
        <div className="section-head"><div><span className="step">01 / UPLOAD</span><h2>Start with a photograph</h2></div><span className="file-limit">JPG · PNG · WEBP / MAX 10 MB</span></div>
        <div className={`upload-card ${drag?'dragging':''} ${preview?'has-preview':''}`} onDragOver={e=>{e.preventDefault();setDrag(true)}} onDragLeave={()=>setDrag(false)} onDrop={e=>{e.preventDefault();setDrag(false);choose(e.dataTransfer.files[0])}}>
          {preview ? <div className="preview-wrap"><img src={preview} alt="Selected facial photo"/><div className="preview-overlay"><span><CheckCircle2 size={15}/> Image ready for analysis</span><button className="icon-button" onClick={reset} aria-label="Remove image"><X size={17}/></button></div></div> :
          <label className="upload-prompt"><span className="upload-icon"><UploadCloud size={27}/></span><strong>Drop your photo here</strong><span>or <u>browse files</u> from your device</span><small>One face · Front-facing · Neutral expression</small><input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>choose(e.target.files?.[0])}/></label>}
        </div>
        <div className="capture-hints"><span><CheckCircle2 size={14}/> Face fully visible</span><span><CheckCircle2 size={14}/> Even natural lighting</span><span><CheckCircle2 size={14}/> Camera at eye level</span><span><CheckCircle2 size={14}/> No beauty filters</span></div>
        {error && <div className="error-banner"><CircleAlert size={17}/>{error}</div>}
        <div className="action-row"><div className="privacy-note"><ShieldCheck size={16}/><span>Your photo is processed by your configured backend. The default backend does not retain uploads.</span></div><button className="primary-button" disabled={!file||busy} onClick={analyze}>{busy?<><Loader2 className="spin" size={17}/> Analyzing features</>:<>Analyze photograph <ArrowUpRight size={17}/></>}</button></div>
      </section>

      {result && <section className="results" id="results">
        <div className="section-head"><div><span className="step">02 / YOUR REPORT</span><h2>Analysis overview</h2></div><button className="text-button" onClick={reset}>New analysis <ArrowUpRight size={15}/></button></div>
        <div className="score-grid">
          <div className="score-card">
            <div className="score-card-top"><span>REFERENCE MATCH SCORE</span><span className="score-icon"><Gauge size={17}/></span></div>
            <div className="score-number">{score===null?'—':score?.toFixed(2)}<small>/ 10</small></div>
            <div className="score-caption">{score===null?'Not enough valid references':'Experimental similarity to configured references'}</div>
            <div className="score-track"><span style={{width:`${score===null?0:score*10}%`}}/></div>
          </div>
          <div className="metric-card"><span>ANALYZED CATEGORIES</span><strong>{result.analyzed_categories}<small> / 34</small></strong><p>Categories with a usable reference and measurement</p></div>
          <div className="metric-card"><span>REFERENCE COVERAGE</span><strong>{result.coverage_percent}<small>%</small></strong><p>Configured category weight represented in this result</p></div>
          <div className="metric-card"><span>OVERALL CONFIDENCE</span><strong>{Math.round(result.overall_confidence*100)}<small>%</small></strong><p>Image and landmark confidence, not attractiveness</p></div>
        </div>
        <div className="notice"><Sparkles size={17}/><p><strong>How to read this report</strong> Scores measure similarity to your own configured references. They are experimental, not scientifically validated attractiveness ratings. Missing references and unsupported measurements are not scored.</p></div>
        <div className="results-layout">
          <div className="category-panel">
            <div className="panel-title"><div><span className="step">CATEGORY BREAKDOWN</span><h3>Individual comparisons</h3></div><span className="count-pill">{result.categories.length} TOTAL</span></div>
            {Object.entries(grouped).map(([group,items])=><div className="category-group" key={group}>
              <div className="group-heading"><span>{groups[group]||group}</span><span>{items.filter(x=>x.score!==null).length}/{items.length} scored</span></div>
              {items.map(item=><div className="category-row" key={item.category_id}>
                <button className="category-main" onClick={()=>setExpanded(expanded===item.category_id?null:item.category_id)}>
                  <span className="category-name">{item.name}<small>{item.status==='experimental'?'Experimental comparison':item.status==='reference_missing'?'Reference missing':'Not assessable'}</small></span>
                  <span className={`category-score ${item.score===null?'muted':''}`}>{item.score===null?'—':item.score.toFixed(1)}<small>{item.score===null?'':'/10'}</small></span><ChevronDown className={expanded===item.category_id?'rotated':''} size={16}/>
                </button>
                {expanded===item.category_id&&<div className="category-detail"><p>{item.explanation}</p>{item.score!==null&&<div className="detail-meta"><span>Confidence <b>{Math.round(item.confidence*100)}%</b></span>{item.distance!==undefined&&<span>Feature distance <b>{item.distance}</b></span>}</div>}</div>}
              </div>)}
            </div>)}
          </div>
          <aside className="side-panel">
            <div className="side-card"><span className="step">IMAGE QUALITY</span><h3>Capture diagnostics</h3><div className="quality-line"><span>Resolution</span><b>{result.image_quality.width} × {result.image_quality.height}</b></div><div className="quality-line"><span>Brightness</span><b>{result.image_quality.brightness}</b></div><div className="quality-line"><span>Blur variance</span><b>{result.image_quality.blur_variance}</b></div>{result.image_quality.warnings.length>0?<ul className="warning-list">{result.image_quality.warnings.map(w=><li key={w}>{w}</li>)}</ul>:<p className="good-note"><CheckCircle2 size={14}/> No basic quality warnings</p>}</div>
            <div className="side-card"><span className="step">LIMITATIONS</span><h3>Read before interpreting</h3><ul className="limitation-list">{result.limitations.map(x=><li key={x}>{x}</li>)}</ul></div>
          </aside>
        </div>
      </section>}

      <section className="how-section" id="how"><div className="section-head"><div><span className="step">THE PROCESS</span><h2>Independent by design</h2></div></div><div className="process-grid"><article><span>01</span><ScanFace/><h3>Detect & measure</h3><p>Face landmarks are extracted and normalized to reduce scale and position differences.</p></article><article><span>02</span><FileImage/><h3>Compare by category</h3><p>Each supported category is compared against its own dedicated reference image.</p></article><article><span>03</span><Gauge/><h3>Weight & report</h3><p>Valid category scores contribute to a weighted result. Missing data is excluded.</p></article></div></section>

      <section className="method-section" id="method"><div className="method-copy"><span className="step">METHODOLOGY & TRANSPARENCY</span><h2>Similarity is not a universal standard.</h2><p>INFINITY is designed as a reference comparison tool. The choice of reference images influences the result. The current engine uses facial landmarks and experimental feature-distance mappings; it is not a clinically or scientifically validated attractiveness model.</p><p>Some characteristics — including depth, projection, skin texture, and hidden features — cannot be reliably measured from a single frontal photograph. These are reported as unavailable until a suitable method and input view are implemented.</p></div><div className="method-stamp"><Fingerprint size={34}/><strong>INFINITY</strong><span>MEASURE · COMPARE · DISCLOSE</span></div></section>
    </main>
    <footer><a className="brand" href="#"><span className="brand-mark"><Fingerprint size={18}/></span><span>INFINITY<span className="brand-dot">.</span></span></a><span>Reference-based facial feature analysis</span><span>Experimental · Not a universal attractiveness measure</span></footer>
  </div>
}
