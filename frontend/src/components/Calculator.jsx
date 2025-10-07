import { useState } from "react";
import NumbersInput from "./NumbersInput.jsx";
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const operationLabels = {
  sum: "＋",
  sub: "－",
  mul: "×",
  div: "÷"
};

const operationNames = {
  sum: "Suma",
  sub: "Resta", 
  mul: "Multiplicación",
  div: "División"
};

export default function Calculator(){
  const [op,setOp] = useState("sum");
  const [numbers,setNumbers] = useState([0,0]);
  const [result,setResult] = useState(null);
  const [error,setError] = useState(null);

  //cambios en los números
  function handleNumbersChange(newNumbers) {
    setNumbers(newNumbers);
    //limpiar resultado y error cuando cambian los números
    setResult(null);
    setError(null);
  }

  //manejar cambios en la operación
  function handleOperationChange(newOp) {
    setOp(newOp);
    //limpiar resultado y error cuando cambia la operación
    setResult(null);
    setError(null);
  }

  async function calc(){
    setError(null); setResult(null);
    const r = await fetch(`${API}/api/${op}`, {
      method:"POST", headers:{ "Content-Type":"application/json"},
      body: JSON.stringify({numbers})
    });
    const data = await r.json();
    if(!r.ok){ setError(data.detail ?? data); return; }
    setResult(data.result);
  }

  return (
    <div>
      {/* Display Area */}
      <div style={{
        background: "#1a1a1a",
        borderRadius: "16px",
        padding: "24px",
        marginBottom: "24px",
        minHeight: "120px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "flex-end",
        color: "#fff",
        position: "relative"
      }}>
        <div style={{
          fontSize: "14px",
          color: "#888",
          marginBottom: "8px",
          alignSelf: "flex-start"
        }}>
          {operationNames[op]}
        </div>
        
        {result !== null ? (
          <div style={{
            fontSize: "36px",
            fontWeight: "300",
            lineHeight: "1",
            wordBreak: "break-all"
          }}>
            {result}
          </div>
        ) : (
          <div style={{
            fontSize: "24px",
            color: "#666",
            fontWeight: "300"
          }}>
            {numbers.join(` ${operationLabels[op]} `)}
          </div>
        )}

        {error && (
          <div style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            background: "#ff4757",
            color: "#fff",
            padding: "12px",
            borderRadius: "8px",
            fontSize: "14px",
            marginTop: "8px",
            wordBreak: "break-word"
          }}>
            {error.message || error.detail || error || "Error en el cálculo"}
          </div>
        )}
      </div>

      {/* elegir el tipo de operacion*/}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: "8px",
        marginBottom: "24px"
      }}>
        {Object.entries(operationLabels).map(([key, symbol]) => (
          <button
            key={key}
            onClick={() => handleOperationChange(key)}
            style={{
              padding: "16px",
              border: "none",
              borderRadius: "12px",
              background: op === key ? "#1e3a8a" : "#f8f9fa",
              color: op === key ? "#fff" : "#333",
              fontSize: "20px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: op === key ? "0 4px 12px rgba(30, 58, 138, 0.3)" : "0 2px 4px rgba(0, 0, 0, 0.1)"
            }}
          >
            {symbol}
          </button>
        ))}
      </div>

      {/*input de los numeros*/}
      <div style={{ marginBottom: "24px" }}>
        <NumbersInput value={numbers} onChange={handleNumbersChange} />
      </div>

      {/*boton de calucular */}
      <button 
        onClick={calc}
        style={{
          width: "100%",
          padding: "16px",
          border: "none",
          borderRadius: "16px",
          background: "linear-gradient(135deg, #2c5aa0 0%, #1e3a8a 100%)",
          color: "#fff",
          fontSize: "18px",
          fontWeight: "600",
          cursor: "pointer",
          transition: "all 0.2s ease",
          boxShadow: "0 4px 16px rgba(30, 58, 138, 0.3)"
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
        Calcular
      </button>
    </div>
  );
}
