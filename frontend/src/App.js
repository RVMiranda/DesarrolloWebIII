import React, { useEffect, useMemo, useState, useCallback } from "react";
import "./App.css";

const DEFAULT_API = "http://127.0.0.1:8089";

export default function App() {
  // Config
  const [apiUrl, setApiUrl] = useState(
    localStorage.getItem("API_URL") || DEFAULT_API
  );
  const baseApi = useMemo(() => apiUrl.replace(/\/$/, ""), [apiUrl]);
  const [savingApi, setSavingApi] = useState(false);

  // Calc
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [resultado, setResultado] = useState(null);

  // Historial
  const [historial, setHistorial] = useState([]);
  const [limit, setLimit] = useState(20);

  // UI state
  const [cargando, setCargando] = useState(false);
  const [cargandoHist, setCargandoHist] = useState(false);
  const [error, setError] = useState("");

  const guardarApi = () => {
    const clean = baseApi;
    localStorage.setItem("API_URL", clean);
    setApiUrl(clean);
    setSavingApi(true);
    setTimeout(() => setSavingApi(false), 600);
  };

  const formatDate = (dateString) => {
    try {
      const d = new Date(dateString);
      if (isNaN(d.getTime())) return dateString;
      return d.toLocaleString();
    } catch {
      return dateString;
    }
  };

  const obtenerHistorial = useCallback(
    async (customLimit) => {
      setError("");
      setCargandoHist(true);
      try {
        const url = new URL(`${baseApi}/calculadora/historial`);
        url.searchParams.set("limit", String(customLimit ?? limit));
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setHistorial(Array.isArray(data.historial) ? data.historial : []);
      } catch (e) {
        console.error(e);
        setError(
          "No se pudo obtener el historial. Verifica la conexión con el backend."
        );
      } finally {
        setCargandoHist(false);
      }
    },
    [baseApi, limit]
  );

  const calcularSuma = async (e) => {
    e?.preventDefault?.();
    setError("");
    setResultado(null);
    setCargando(true);
    try {
      const aNum = a === "" ? 0 : Number(a);
      const bNum = b === "" ? 0 : Number(b);
      if (Number.isNaN(aNum) || Number.isNaN(bNum)) {
        throw new Error("Ingresa números válidos.");
      }
      const url = new URL(`${baseApi}/calculadora/sum`);
      url.searchParams.set("a", String(aNum));
      url.searchParams.set("b", String(bNum));
      const res = await fetch(url.toString());
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResultado(data.resultado);
      await obtenerHistorial();
    } catch (e) {
      console.error(e);
      setError(
        "No se pudo calcular la suma. Revisa que el backend esté funcionando y CORS habilitado."
      );
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    obtenerHistorial();
  }, [obtenerHistorial]);

  const limpiar = () => {
    setA("");
    setB("");
    setResultado(null);
    setError("");
  };

  return (
    <div className="layout">
      {/* Topbar */}
      <header className="topbar">
        <div className="brand">
          <span className="logo">Σ</span>
          <div className="brand-text">
            <h1>Calculadora simple con FastAPI + Mongo</h1>
            <p className="sub"></p>
          </div>
        </div>

        
      </header>

      {/* Content */}
      <main className="content">
        {/* Left: Calculator Card */}
        <section className="panel calc-card">
          <div className="panel-head">
            <h2>Calculadora</h2>
            <p className="muted">Suma de dos valores y registro en historial</p>
          </div>

          <form className="calc-form" onSubmit={calcularSuma}>
            <div className="field">
              <label>Valor A</label>
              <input
                type="number"
                className="input big"
                value={a}
                onChange={(e) => setA(e.target.value)}
                inputMode="decimal"
                placeholder="Ej. 12.5"
              />
            </div>

            <div className="op-plus">+</div>

            <div className="field">
              <label>Valor B</label>
              <input
                type="number"
                className="input big"
                value={b}
                onChange={(e) => setB(e.target.value)}
                inputMode="decimal"
                placeholder="Ej. 30"
              />
            </div>

            <div className="actions">
              <button type="submit" className="btn primary" disabled={cargando}>
                {cargando ? "Calculando…" : "Calcular"}
              </button>
              <button
                type="button"
                className="btn ghost"
                onClick={limpiar}
                disabled={cargando}
              >
                Limpiar
              </button>
            </div>
          </form>

          <div className="result-area">
            {error ? (
              <div className="alert error">{error}</div>
            ) : resultado !== null ? (
              <div className="result-card">
                <div className="label">Resultado</div>
                <div className="value">{resultado}</div>
              </div>
            ) : (
              <div className="placeholder">
                Ingresa valores y presiona <strong>Calcular</strong>
              </div>
            )}
          </div>

          <div className="api-foot">
            API actual: <span className="mono">{baseApi}</span>
          </div>
        </section>

        {/* Right: History */}
        <section className="panel hist-card">
          <div className="panel-head row">
            <h2>Historial</h2>
            <div className="hist-controls">
              <label>Límite</label>
              <input
                type="number"
                min={1}
                max={200}
                className="input small"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value) || 1)}
              />
              <button
                className="btn outline"
                onClick={() => obtenerHistorial()}
                disabled={cargandoHist}
              >
                {cargandoHist ? "Cargando…" : "Actualizar"}
              </button>
            </div>
          </div>

          {historial.length === 0 ? (
            <div className="empty">
              {cargandoHist ? "Cargando historial…" : "No hay registros aún."}
            </div>
          ) : (
            <div className="list">
              {historial.map((op, i) => (
                <div className="item" key={`${op._id || i}-${op.date || i}`}>
                  <div className="item-left">
                    <div className="expr">
                      <span className="mono">
                        {op.a} + {op.b} ={" "}
                      </span>
                      <strong className="accent">{op.resultado}</strong>
                    </div>
                    <div className="date muted">{formatDate(op.date)}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <span>Hecho con React · FastAPI · MongoDB</span>
      </footer>
    </div>
  );
}
