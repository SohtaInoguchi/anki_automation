import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");
  const [words, setWords] = useState("cat, dog, school");
  const [loading, setLoading] = useState(false);

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

  const generateCards = async () => {
    setLoading(true);
    try {
      const wordList = words.split(",").map((w) => w.trim()).filter((w) => w);
      const res = await fetch(`${API_BASE}/generate-cards`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ words: wordList }),
      });

      const data = await res.json();
      if (data.success) {
        setResponse(`Successfully generated ${data.cards.length} cards!`);
      } else {
        setResponse(`Error: ${data.error}`);
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Anki Card Generator</h1>

      <div style={{ marginBottom: 20 }}>
        <button onClick={pingBackend}>
          Ping backend
        </button>

        {response && (
          <p>
            <strong>Response:</strong> {response}
          </p>
        )}
      </div>

      <div style={{ marginBottom: 20 }}>
        <label>
          <strong>Enter words (comma-separated):</strong>
          <br />
          <textarea
            value={words}
            onChange={(e) => setWords(e.target.value)}
            rows={3}
            cols={50}
          />
        </label>
        <br />
        <button onClick={generateCards} disabled={loading}>
          {loading ? "Generating..." : "Generate Cards"}
        </button>
      </div>
    </div>
  );
}

export default App;
