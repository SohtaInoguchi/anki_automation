import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");
  const [words, setWords] = useState("cat, dog, school");
  const [loading, setLoading] = useState(false);
  const [cards, setCards] = useState([]);
  const [csvFile, setCsvFile] = useState(null);

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
        setCsvFile(data.csv_file);
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

  const downloadImage = async (imageFile) => {
    if (!imageFile) return;
    try {
      const filename = imageFile.split("/").pop();
      const url = `${API_BASE}/images/${filename}`;
      
      // Fetch the image as a blob
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch image");
      const blob = await res.blob();
      
      // Create a blob URL and download
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      alert(`Download failed: ${error.message}`);
    }
  };

  const downloadAudio = async (audioFile) => {
    if (!audioFile) return;
    try {
      const filename = audioFile.split("/").pop();
      const url = `${API_BASE}/audio/${filename}`;
      
      // Fetch the audio as a blob
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch audio");
      const blob = await res.blob();
      
      // Create a blob URL and download
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      alert(`Download failed: ${error.message}`);
    }
  };

  const downloadCsv = async () => {
    if (!csvFile) return;
    try {
      const url = `${API_BASE}/images/${csvFile}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch CSV");
      const blob = await res.blob();
      
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = csvFile;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      alert(`CSV download failed: ${error.message}`);
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

      {cards.length > 0 && (
        <div>
          <h2>Generated Cards</h2>
          
          {csvFile && (
            <div style={{ marginBottom: 15 }}>
              <button onClick={downloadCsv} style={{ backgroundColor: "#4CAF50", color: "white", padding: "10px 15px", cursor: "pointer" }}>
                Download CSV
              </button>
            </div>
          )}

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
                <th style={{ border: "1px solid #ccc", padding: 8 }}>Audio Front</th>
                <th style={{ border: "1px solid #ccc", padding: 8 }}>Audio Back</th>
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
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {card.audio_front ? (
                      <button onClick={() => downloadAudio(card.audio_front)}>
                        Download {card.word}_en.mp3
                      </button>
                    ) : (
                      "No audio"
                    )}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {card.audio_back ? (
                      <button onClick={() => downloadAudio(card.audio_back)}>
                        Download {card.word}_fr.mp3
                      </button>
                    ) : (
                      "No audio"
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
