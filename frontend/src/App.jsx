import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");

  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  const pingBackend = async () => {
    const res = await fetch(`${API_BASE}/ping`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: "hello backend" }),
    });

    const data = await res.json();
    setResponse(data.reply);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Frontend ↔ Backend Test</h1>

      <button onClick={pingBackend}>
        Ping backend
      </button>

      {response && (
        <p>
          <strong>Response:</strong> {response}
        </p>
      )}
    </div>
  );
}

export default App;
