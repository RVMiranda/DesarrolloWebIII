import { useState } from "react"
import Calculator from "./components/Calculator.jsx"
import History from "./components/History.jsx"

export default function App(){
  const [activeTab, setActiveTab] = useState("calculator")

  return (
		<div
			style={{
				minHeight: "100vh",
				background: "linear-gradient(135deg, #2c5aa0 0%, #1e3a8a 100%)",
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				padding: "20px",
				fontFamily:
					"-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
			}}
		>
			<div
				style={{
					background: "rgba(255, 255, 255, 0.95)",
					backdropFilter: "blur(10px)",
					borderRadius: "24px",
					boxShadow: "0 20px 40px rgba(0, 0, 0, 0.1)",
					padding: "32px",
					maxWidth: "400px",
					width: "100%",
					minHeight: "600px",
				}}
			>
				{/* Tab Navigation */}
				<div
					style={{
						display: "flex",
						background: "#f5f5f5",
						borderRadius: "16px",
						padding: "4px",
						marginBottom: "24px",
					}}
				>
					<button
						onClick={() => setActiveTab("calculator")}
						style={{
							flex: 1,
							padding: "12px",
							border: "none",
							borderRadius: "12px",
							background: activeTab === "calculator" ? "#fff" : "transparent",
							color: activeTab === "calculator" ? "#1e3a8a" : "#666",
							fontWeight: activeTab === "calculator" ? "600" : "400",
							cursor: "pointer",
							transition: "all 0.2s ease",
							boxShadow:
								activeTab === "calculator"
									? "0 2px 8px rgba(0, 0, 0, 0.1)"
									: "none",
						}}
					>
						Calculadora
					</button>
					<button
						onClick={() => setActiveTab("history")}
						style={{
							flex: 1,
							padding: "12px",
							border: "none",
							borderRadius: "12px",
							background: activeTab === "history" ? "#fff" : "transparent",
							color: activeTab === "history" ? "#1e3a8a" : "#666",
							fontWeight: activeTab === "history" ? "600" : "400",
							cursor: "pointer",
							transition: "all 0.2s ease",
							boxShadow:
								activeTab === "history"
									? "0 2px 8px rgba(0, 0, 0, 0.1)"
									: "none",
						}}
					>
						Historial
					</button>
				</div>

				{/* secciones */}
				{activeTab === "calculator" && <Calculator />}
				{activeTab === "history" && <History />}
			</div>
			{/* comentario para hacer build */}
		</div>
	);
}
