import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");
  const [words, setWords] = useState("cat, dog, school");
  const [loading, setLoading] = useState(false);
  const [cards, setCards] = useState([]);

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
        setCards(data.cards);
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

  const downloadImage = (imageFile) => {
    if (!imageFile) return;
    const filename = imageFile.split("/").pop();
    const url = `${API_BASE}/images/${filename}`;
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
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

      {cards.length > 0 && (
        <div>
          <h2>Generated Cards</h2>
          <table
            style={{
              borderCollapse: "collapse",
              border: "1px solid #ccc",
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f0f0f0" }}>
                <th style={{ border: "1px solid #ccc", padding: 8 }}>Word</th>
                <th style={{ border: "1px solid #ccc", padding: 8 }}>
                  Translation
                </th>
                <th style={{ border: "1px solid #ccc", padding: 8 }}>Image</th>
              </tr>
            </thead>
            <tbody>
              {cards.map((card, idx) => (
                <tr key={idx}>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {card.word}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {card.translation}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {card.image ? (
                      <button onClick={() => downloadImage(card.image)}>
                        Download {card.word}.jpeg
                      </button>
                    ) : (
                      "No image"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
