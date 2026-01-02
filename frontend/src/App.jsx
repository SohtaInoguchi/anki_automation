import { useState } from "react";
import "./App.css";

function App() {
  // State management
  const [words, setWords] = useState("");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Get API base URL from environment variable (same as your original code)
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  // Validate input before submitting
  const validateInput = () => {
    const wordList = words.split("\n").filter(w => w.trim());
    if (wordList.length === 0) {
      setError("Please enter at least one word");
      return false;
    }
    return true;
  };

  // Main function to generate Anki deck (updated from your pingBackend)
  const submitWords = async () => {
    // Reset states
    setError(null);
    setSuccess(false);
    setDownloadUrl(null);

    // Validate input
    if (!validateInput()) {
      return;
    }

    setLoading(true);

    try {
      const wordList = words.split("\n").filter(w => w.trim());

      // Call your backend API
      const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          words: wordList
        })
      });

      // Check if response is ok (this was missing in the original issue code!)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.download_url) {
        setDownloadUrl(`${API_BASE}${data.download_url}`);
        setSuccess(true);
      } else {
        throw new Error("No download URL received from server");
      }

    } catch (err) {
      console.error("Error generating deck:", err);
      setError(err.message || "Failed to generate Anki deck. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Clear form function
  const handleClear = () => {
    setWords("");
    setError(null);
    setSuccess(false);
    setDownloadUrl(null);
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🎴 Anki Card Generator</h1>
        <p className="subtitle">
          Enter Korean words (one per line) to generate an Anki deck with definitions and example sentences
        </p>

        <div className="form-group">
          <label htmlFor="words-input">
            Enter Words:
          </label>
          <textarea
            id="words-input"
            rows={12}
            className="textarea"
            placeholder="고양이&#10;강아지&#10;학교&#10;컴퓨터&#10;친구"
            value={words}
            onChange={e => setWords(e.target.value)}
            disabled={loading}
          />
          <div className="word-count">
            {words.split("\n").filter(w => w.trim()).length} word(s)
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <strong>✅ Success:</strong> Your Anki deck has been generated!
          </div>
        )}

        <div className="button-group">
          <button
            className="btn btn-primary"
            onClick={submitWords}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Generating...
              </>
            ) : (
              "Generate Anki Deck"
            )}
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>

        {downloadUrl && (
          <div className="download-section">
            <a
              href={downloadUrl}
              download
              className="btn btn-download"
            >
              📥 Download ZIP File
            </a>
            <p className="help-text">
              Extract the ZIP file and import the .apkg file into Anki
            </p>
          </div>
        )}

        <div className="info-section">
          <h3>ℹ️ How to use:</h3>
          <ol>
            <li>Enter Korean words, one per line</li>
            <li>Click "Generate Anki Deck"</li>
            <li>Download the ZIP file</li>
            <li>Extract and import the .apkg file into Anki</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default App;