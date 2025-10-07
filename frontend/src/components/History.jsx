import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const operationLabels = {
  sum: "＋",
  sub: "－", 
  mul: "×",
  div: "÷"
};

export default function History(){
  const [items,setItems] = useState([]);
  const [filters,setFilters] = useState({op:"", sort_by:"date", order:"desc"});

  async function load(){
    const q = new URLSearchParams();
    if(filters.op) q.set("op", filters.op);
    q.set("sort_by", filters.sort_by);
    q.set("order", filters.order);
    const r = await fetch(`${API}/api/history?${q.toString()}`);
    const data = await r.json();
    setItems(data.items ?? []);
  }

  useEffect(()=>{ load(); }, []);

  return (
    <div>
      {/* Header */}
      <h3 style={{
        margin: "0 0 24px 0",
        fontSize: "20px",
        fontWeight: "600",
        color: "#333"
      }}>
        Historial de Cálculos
      </h3>

      {/*seccion de filtrado*/}
      <div style={{
        background: "#f8f9fa",
        borderRadius: "12px",
        padding: "16px",
        marginBottom: "24px"
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))",
          gap: "12px",
          marginBottom: "12px"
        }}>
          <select 
            value={filters.op} 
            onChange={e=>setFilters(f=>({...f,op:e.target.value}))}
            style={{
              padding: "8px 12px",
              border: "1px solid #e1e5e9",
              borderRadius: "8px",
              fontSize: "14px",
              background: "#fff",
              outline: "none"
            }}
          >
            <option value="">Todas</option>
            <option value="sum">Suma</option>
            <option value="sub">Resta</option>
            <option value="mul">Multiplicación</option>
            <option value="div">División</option>
          </select>

          <select 
            value={filters.sort_by} 
            onChange={e=>setFilters(f=>({...f,sort_by:e.target.value}))}
            style={{
              padding: "8px 12px",
              border: "1px solid #e1e5e9",
              borderRadius: "8px",
              fontSize: "14px",
              background: "#fff",
              outline: "none"
            }}
          >
            <option value="date">Fecha</option>
            <option value="result">Resultado</option>
          </select>

          <select 
            value={filters.order} 
            onChange={e=>setFilters(f=>({...f,order:e.target.value}))}
            style={{
              padding: "8px 12px",
              border: "1px solid #e1e5e9",
              borderRadius: "8px",
              fontSize: "14px",
              background: "#fff",
              outline: "none"
            }}
          >
            {filters.sort_by === "result" ? (
              <>
                <option value="desc">Mayor resultado</option>
                <option value="asc">Menor resultado</option>
              </>
            ) : (
              <>
                <option value="desc">Más reciente</option>
                <option value="asc">Más antiguo</option>
              </>
            )}
          </select>
        </div>

        <button 
          onClick={load}
          style={{
            width: "100%",
            padding: "10px",
            border: "none",
            borderRadius: "8px",
            background: "#1e3a8a",
            color: "#fff",
            fontSize: "14px",
            fontWeight: "600",
            cursor: "pointer",
            transition: "all 0.2s ease"
          }}
          onMouseDown={(e) => {
            e.target.style.transform = "scale(0.98)";
          }}
          onMouseUp={(e) => {
            e.target.style.transform = "scale(1)";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "scale(1)";
          }}
        >
          Actualizar
        </button>
      </div>

      {/*historial*/}
      <div style={{
        maxHeight: "400px",
        overflowY: "auto"
      }}>
        {items.length === 0 ? (
          <div style={{
            textAlign: "center",
            padding: "40px 20px",
            color: "#666",
            fontSize: "14px"
          }}>
            No hay cálculos en el historial
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {items.map(it=>(
              <div 
                key={it.id}
                style={{
                  background: "#fff",
                  border: "1px solid #e1e5e9",
                  borderRadius: "8px",
                  padding: "12px",
                  fontSize: "14px",
                  transition: "all 0.2s ease"
                }}
                onMouseEnter={(e) => {
                  e.target.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.1)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.boxShadow = "none";
                }}
              >
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "4px"
                }}>
                  <span style={{
                    fontSize: "12px",
                    color: "#888"
                  }}>
                    {new Date(it.created_at).toLocaleString()}
                  </span>
                  <span style={{
                    background: "#f0f0f0",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    fontWeight: "600"
                  }}>
                    {operationLabels[it.op] || it.op}
                  </span>
                </div>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px"
                }}>
                  <span style={{ color: "#666" }}>
                    {it.numbers.join(` ${operationLabels[it.op] || it.op} `)}
                  </span>
                  <span style={{ color: "#888" }}>=</span>
                  <span style={{
                    fontWeight: "600",
                    color: "#333"
                  }}>
                    {it.result}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
