import { useEffect, useMemo, useState } from "react";

const API = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || `Request failed (${response.status})`);
  }
  return data;
}

function formatDate(value) {
  if (!value) return "Just now";
  return new Date(value).toLocaleString();
}

function App() {
  const [plants, setPlants] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [diagnoses, setDiagnoses] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [latest, setLatest] = useState(null);
  const [species, setSpecies] = useState("Tomato");
  const [cultivar, setCultivar] = useState("");
  const [zone, setZone] = useState("Zone A");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [apiOnline, setApiOnline] = useState(false);

  const selectedPlant = useMemo(
    () => plants.find((plant) => plant.plant_id === selectedId),
    [plants, selectedId]
  );

  async function loadPlants(preferredId = "") {
    const data = await request("/api/plants/");
    const items = data.plants || [];
    setPlants(items);
    const nextId = preferredId || selectedId;
    if (nextId && items.some((plant) => plant.plant_id === nextId)) {
      setSelectedId(nextId);
    } else if (items.length && !selectedId) {
      setSelectedId(items[0].plant_id);
    }
    setApiOnline(true);
  }

  async function loadDiagnoses(plantId) {
    if (!plantId) {
      setDiagnoses([]);
      return;
    }
    const data = await request(`/api/plants/${plantId}/diagnoses`);
    setDiagnoses(data.diagnoses || []);
  }

  useEffect(() => {
    loadPlants().catch((err) => {
      setApiOnline(false);
      setError(`Cannot connect to the backend: ${err.message}`);
    });
  }, []);

  useEffect(() => {
    if (selectedId) {
      loadDiagnoses(selectedId).catch((err) => setError(err.message));
    } else {
      setDiagnoses([]);
    }
  }, [selectedId]);

  function chooseFile(file) {
    if (!file) return;
    setError("");
    setLatest(null);
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Please choose a JPG, PNG, or WebP image.");
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      setError("Image must be 8 MB or smaller.");
      return;
    }
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
  }

  async function createPlant(event) {
    event.preventDefault();
    setCreating(true);
    setError("");
    setNotice("");
    try {
      const data = await request("/api/plants/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          species: species.trim(),
          cultivar: cultivar.trim() || null,
          zone_id: zone.trim() || null,
        }),
      });
      await loadPlants(data.plant.plant_id);
      setNotice("Plant registered successfully.");
      setCultivar("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  async function analyzeImage(event) {
    event.preventDefault();
    if (!selectedId) {
      setError("Register or select a plant first.");
      return;
    }
    if (!selectedFile) {
      setError("Choose a leaf image first.");
      return;
    }

    setLoading(true);
    setError("");
    setNotice("");
    setLatest(null);
    const form = new FormData();
    form.append("image", selectedFile);

    try {
      const data = await request(`/api/plants/${selectedId}/analyze-image`, {
        method: "POST",
        body: form,
      });
      setLatest(data.diagnosis);
      await loadDiagnoses(selectedId);
      setNotice("Image analyzed and diagnosis added to plant history.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function showDiagnosis(diagnosis) {
    setLatest(diagnosis);
  }

  const analysis = latest?.analysis;
  const crop = analysis?.crop_identification;
  const diagnosis = analysis?.diagnosis;
  const guidance = analysis?.condition_information;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div><strong>AgriSphere</strong><span>PLANT INTELLIGENCE</span></div>
        </div>
        <div className="side-label">WORKSPACE</div>
        <a className="nav-item active" href="#overview"><span>◫</span> Overview</a>
        <a className="nav-item" href="#plants"><span>♧</span> Plant registry</a>
        <a className="nav-item" href="#diagnosis"><span>⌕</span> AI diagnosis</a>
        <a className="nav-item" href="#history"><span>◷</span> Diagnosis history</a>
        <div className="sidebar-bottom">
          <div className="status-card">
            <span className={`status-dot ${apiOnline ? "online" : ""}`} />
            <div><b>{apiOnline ? "Backend connected" : "Backend offline"}</b><small>FastAPI service</small></div>
          </div>
          <small className="version">AGROSPHERE AI · MVP 0.3</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">WORKSPACE <span>/</span> OVERVIEW</div>
          <div className="topbar-right"><span className="live-pill"><i /> {apiOnline ? "SYSTEM ONLINE" : "CONNECTING"}</span><div className="avatar">AS</div></div>
        </header>

        <section id="overview" className="page-heading">
          <div><p className="eyebrow">AUTONOMOUS PLANT INTELLIGENCE</p><h1>Greenhouse overview</h1><p className="muted">Monitor your plant records and investigate potential crop health issues.</p></div>
          <div className="date-chip">◷ &nbsp; {new Date().toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", year: "numeric" })}</div>
        </section>

        {error && <div className="alert error">{error}<button onClick={() => setError("")}>×</button></div>}
        {notice && <div className="alert success">{notice}<button onClick={() => setNotice("")}>×</button></div>}

        <section className="stats-grid">
          <article className="stat-card"><div className="stat-top"><span>REGISTERED PLANTS</span><b>♧</b></div><strong>{plants.length}</strong><small>Tracked plant records</small></article>
          <article className="stat-card"><div className="stat-top"><span>AI DIAGNOSES</span><b>⌕</b></div><strong>{diagnoses.length}</strong><small>For selected plant</small></article>
          <article className="stat-card"><div className="stat-top"><span>ACTIVE PLANT</span><b>◎</b></div><strong className="stat-text">{selectedPlant?.profile?.species || "—"}</strong><small>{selectedPlant?.zone_id || "No zone assigned"}</small></article>
          <article className="stat-card"><div className="stat-top"><span>VISION ENGINE</span><b>✳</b></div><strong className="stat-text">Ready</strong><small>Image classification service</small></article>
        </section>

        <div className="content-grid">
          <section id="plants" className="panel plant-panel">
            <div className="panel-heading"><div><p className="eyebrow">PLANT MANAGEMENT</p><h2>Plant registry</h2></div><span className="count-tag">{plants.length} TOTAL</span></div>
            <form className="register-form" onSubmit={createPlant}>
              <div className="form-title">Register a plant</div>
              <label>Crop / species<input value={species} onChange={(e) => setSpecies(e.target.value)} placeholder="e.g. Tomato" required /></label>
              <div className="two-fields">
                <label>Cultivar <span className="optional">OPTIONAL</span><input value={cultivar} onChange={(e) => setCultivar(e.target.value)} placeholder="e.g. Roma" /></label>
                <label>Greenhouse zone<input value={zone} onChange={(e) => setZone(e.target.value)} placeholder="Zone A" /></label>
              </div>
              <button className="primary-button" disabled={creating}>{creating ? "Registering..." : "+ Register plant"}</button>
            </form>
            <div className="plant-list-heading"><b>Registered plants</b><span>{plants.length} records</span></div>
            <div className="plant-list">
              {plants.length === 0 ? <div className="empty-state">No plants registered yet. Add your first plant above.</div> :
                plants.map((plant) => (
                  <button key={plant.plant_id} className={`plant-row ${selectedId === plant.plant_id ? "selected" : ""}`} onClick={() => { setSelectedId(plant.plant_id); setLatest(null); }}>
                    <span className="plant-icon">♧</span><span className="plant-info"><b>{plant.profile.species}</b><small>{plant.profile.cultivar || "Standard cultivar"} · {plant.zone_id || "Unassigned zone"}</small></span><span className="plant-arrow">›</span>
                  </button>
                ))}
            </div>
          </section>

          <section id="diagnosis" className="panel diagnosis-panel">
            <div className="panel-heading"><div><p className="eyebrow">COMPUTER VISION</p><h2>AI plant diagnosis</h2></div><span className="ai-tag">✳ AI POWERED</span></div>
            <div className="selected-plant">
              <div className="selected-icon">♧</div><div><small>ANALYZING PLANT</small><b>{selectedPlant?.profile?.species || "Select a plant"}</b></div>
              <select value={selectedId} onChange={(e) => { setSelectedId(e.target.value); setLatest(null); }} aria-label="Select plant">
                <option value="">Choose plant</option>
                {plants.map((plant) => <option key={plant.plant_id} value={plant.plant_id}>{plant.profile.species} · {plant.plant_id.slice(0, 6)}</option>)}
              </select>
            </div>
            <form onSubmit={analyzeImage}>
              <label className="upload-zone">
                {preview ? <img className="image-preview" src={preview} alt="Selected leaf" /> : <div className="upload-placeholder"><span className="upload-icon">↑</span><b>Upload a leaf image</b><small>Drag an image here or browse files</small><em>JPG · PNG · WEBP · MAX 8 MB</em></div>}
                <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => chooseFile(e.target.files?.[0])} />
              </label>
              <div className="upload-actions"><span>{selectedFile ? selectedFile.name : "No image selected"}</span><button className="primary-button" disabled={loading || !selectedId || !selectedFile}>{loading ? "Analyzing..." : "✳ Analyze leaf image"}</button></div>
            </form>
            {analysis && <div className="result-card">
              <div className="result-header"><div><p className="eyebrow">AI ANALYSIS RESULT</p><h3>{diagnosis?.predicted_condition || "No confident condition"}</h3></div><span className={`result-status ${diagnosis?.status === "possible_disease" ? "warning" : "good"}`}>{diagnosis?.status?.replaceAll("_", " ") || "Uncertain"}</span></div>
              <div className="result-metrics"><div><small>IDENTIFIED CROP</small><b>{crop?.crop || "Uncertain"}</b><strong>{crop?.confidence != null ? `${(crop.confidence * 100).toFixed(1)}%` : "—"}</strong></div><div><small>CONDITION SCORE</small><b>{diagnosis?.predicted_condition || "Uncertain"}</b><strong>{diagnosis?.raw_class_confidence != null ? `${(diagnosis.raw_class_confidence * 100).toFixed(1)}%` : "—"}</strong></div></div>
              {guidance && <div className="guidance"><b>Recommended actions</b><ul>{(guidance.recommended_actions || []).map((item, i) => <li key={i}>{item}</li>)}</ul></div>}
              <p className="disclaimer">AI prediction only — not a confirmed agricultural diagnosis. Confidence scores are not calibrated probabilities.</p>
            </div>}
          </section>
        </div>

        <section id="history" className="panel history-panel">
          <div className="panel-heading"><div><p className="eyebrow">PLANT RECORD</p><h2>Diagnosis history</h2></div><span className="count-tag">{diagnoses.length} RECORDS</span></div>
          {!selectedPlant ? <div className="empty-state">Select a plant to view its diagnosis history.</div> : diagnoses.length === 0 ? <div className="empty-state">No diagnoses saved for {selectedPlant.profile.species} yet. Upload a leaf image to create the first record.</div> :
            <div className="history-list">{diagnoses.map((item) => {
              const a = item.analysis || {};
              return <button key={item.diagnosis_id} className={`history-row ${latest?.diagnosis_id === item.diagnosis_id ? "current" : ""}`} onClick={() => showDiagnosis(item)}>
                <img src={`${API}${item.image_url}`} alt="Plant diagnosis" /><span className="history-info"><b>{a.diagnosis?.predicted_condition || "Uncertain condition"}</b><small>{a.crop_identification?.crop || "Unknown crop"} · {formatDate(item.created_at)}</small></span><span className="history-score">{a.diagnosis?.raw_class_confidence != null ? `${(a.diagnosis.raw_class_confidence * 100).toFixed(1)}%` : "—"}</span><span className="plant-arrow">›</span>
              </button>;
            })}</div>}
        </section>
        <footer>AGRI SPHERE AI <span>·</span> AUTONOMOUS PLANT INTELLIGENCE <span className="footer-note">Prototype dashboard · AI outputs require expert verification</span></footer>
      </main>
    </div>
  );
}

export default App;
