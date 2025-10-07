import { useState, useEffect } from "react";

export default function NumbersInput({ value, onChange }) {
  const [nums, setNums] = useState(value ?? [0, 0]);

  useEffect(()=>{ if(onChange) onChange(nums) }, [nums]);

  function set(i, v) {
    const next = [...nums]; next[i] = Number(v); setNums(next);
  }
  function add() { setNums(s=>[...s, 0]); }
  function remove(i) { setNums(s=>s.filter((_,idx)=>idx!==i)); }
  
  function increment(i) {
    const next = [...nums]; next[i] = Number(next[i]) + 1; setNums(next);
  }
  
  function decrement(i) {
    const next = [...nums]; next[i] = Number(next[i]) - 1; setNums(next);
  }

  return (
    <div>
      <label style={{
        display: "block",
        fontSize: "16px",
        fontWeight: "600",
        color: "#555",
        marginBottom: "16px"
      }}>
        Números
      </label>
      
      {nums.map((n,i)=>(
        <div key={i} style={{
          display: "flex",
          gap: "8px",
          marginBottom: "16px",
          alignItems: "center",
          justifyContent: "center"
        }}>
          {/*decrementar */}
          <button
            type="button"
            onClick={() => decrement(i)}
            style={{
              width: "48px",
              height: "48px",
              border: "2px solid #e1e5e9",
              borderRadius: "12px",
              background: "#fff",
              color: "#1e3a8a",
              fontSize: "20px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s ease",
              userSelect: "none",
              flexShrink: 0
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#1e3a8a";
              e.target.style.color = "#fff";
              e.target.style.borderColor = "#1e3a8a";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#fff";
              e.target.style.color = "#1e3a8a";
              e.target.style.borderColor = "#e1e5e9";
            }}
            onMouseDown={(e) => {
              e.target.style.transform = "scale(0.95)";
            }}
            onMouseUp={(e) => {
              e.target.style.transform = "scale(1)";
            }}
          >
            −
          </button>

          {/*input principal */}
          <input 
            type="number" 
            step="any" 
            value={n}
            onChange={e=>set(i,e.target.value)}
            style={{
              width: "120px",
              padding: "16px 12px",
              border: "2px solid #e1e5e9",
              borderRadius: "16px",
              fontSize: "20px",
              fontWeight: "600",
              textAlign: "center",
              transition: "all 0.2s ease",
              outline: "none",
              background: "#fff",
              minHeight: "56px",
              flexShrink: 0
            }}
            onFocus={(e) => {
              e.target.style.borderColor = "#1e3a8a";
              e.target.style.boxShadow = "0 0 0 4px rgba(30, 58, 138, 0.1)";
            }}
            onBlur={(e) => {
              e.target.style.borderColor = "#e1e5e9";
              e.target.style.boxShadow = "none";
            }}
          />

          {/*incrementar */}
          <button
            type="button"
            onClick={() => increment(i)}
            style={{
              width: "48px",
              height: "48px",
              border: "2px solid #e1e5e9",
              borderRadius: "12px",
              background: "#fff",
              color: "#1e3a8a",
              fontSize: "20px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s ease",
              userSelect: "none",
              flexShrink: 0
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#1e3a8a";
              e.target.style.color = "#fff";
              e.target.style.borderColor = "#1e3a8a";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#fff";
              e.target.style.color = "#1e3a8a";
              e.target.style.borderColor = "#e1e5e9";
            }}
            onMouseDown={(e) => {
              e.target.style.transform = "scale(0.95)";
            }}
            onMouseUp={(e) => {
              e.target.style.transform = "scale(1)";
            }}
          >
            +
          </button>

          {/*eliminar solo si hay más de un número */}
          {nums.length > 1 && (
            <button 
              type="button" 
              onClick={() => remove(i)}
              style={{
                width: "48px",
                height: "48px",
                border: "none",
                borderRadius: "12px",
                background: "#ff4757",
                color: "#fff",
                cursor: "pointer",
                fontSize: "18px",
                fontWeight: "600",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "all 0.2s ease",
                flexShrink: 0,
                marginLeft: "4px"
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "#ff3742";
                e.target.style.transform = "scale(1.05)";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "#ff4757";
                e.target.style.transform = "scale(1)";
              }}
              onMouseDown={(e) => {
                e.target.style.transform = "scale(0.95)";
              }}
              onMouseUp={(e) => {
                e.target.style.transform = "scale(1.05)";
              }}
            >
              ✕
            </button>
          )}
        </div>
      ))}
      
      <button 
        type="button" 
        onClick={add}
        style={{
          width: "100%",
          padding: "16px",
          border: "2px dashed #1e3a8a",
          borderRadius: "16px",
          background: "transparent",
          color: "#1e3a8a",
          fontSize: "16px",
          fontWeight: "600",
          cursor: "pointer",
          transition: "all 0.2s ease",
          minHeight: "56px"
        }}
        onMouseEnter={(e) => {
          e.target.style.background = "#1e3a8a";
          e.target.style.color = "#fff";
          e.target.style.borderStyle = "solid";
        }}
        onMouseLeave={(e) => {
          e.target.style.background = "transparent";
          e.target.style.color = "#1e3a8a";
          e.target.style.borderStyle = "dashed";
        }}
      >
        + Agregar número
      </button>
    </div>
  );
}
