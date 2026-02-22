import { useState } from "react";

function App() {
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("");
  const [minRating, setMinRating] = useState(0);
  const [yearMin, setYearMin] = useState("");
  const [yearMax, setYearMax] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [luckyLoading, setLuckyLoading] = useState(false);

  const genres = [
    "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Horror",
    "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller"
  ];

  const years = Array.from({ length: 2024 - 1900 + 1 }, (_, i) => 1900 + i).reverse();

  const fetchRecommendations = async (movieTitle = title) => {
    if (!movieTitle) return;

    setLoading(true);
    setError("");
    setResults([]);

    let url = `http://127.0.0.1:5000/recommend?title=${encodeURIComponent(movieTitle)}`;
    if (genre) url += `&genre=${genre}`;
    if (minRating) url += `&min_rating=${minRating}`;
    if (yearMin) url += `&year_min=${yearMin}`;
    if (yearMax) url += `&year_max=${yearMax}`;

    try {
      const res = await fetch(url);
      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.recommendations);
      }
    } catch (err) {
      setError("Could not connect to server.");
    }

    setLoading(false);
  };

  const feelingLucky = async () => {
    setLuckyLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/random");
      const data = await res.json();
      setTitle(data.title);
      await fetchRecommendations(data.title);
    } catch (err) {
      setError("Could not connect to server.");
    }
    setLuckyLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#141414",
      color: "white",
      fontFamily: "'Arial', sans-serif",
      padding: "40px 20px"
    }}>
      <div style={{ maxWidth: "900px", margin: "0 auto" }}>

        {/* Header */}
        <h1 style={{ color: "#e50914", fontSize: "36px", marginBottom: "4px", letterSpacing: "1px" }}>
          🎥 CineMatch
        </h1>
        <p style={{ color: "#aaa", marginBottom: "30px" }}>Find movies you'll love</p>

        {/* Search Bar */}
        <input
          type="text"
          placeholder="Enter a movie title e.g. Toy Story"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchRecommendations()}
          style={{
            width: "100%",
            padding: "14px",
            fontSize: "16px",
            borderRadius: "6px",
            border: "1px solid #333",
            backgroundColor: "#1f1f1f",
            color: "white",
            marginBottom: "14px",
            boxSizing: "border-box"
          }}
        />

        {/* Genre Dropdown */}
        <select
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          style={{
            width: "100%",
            padding: "14px",
            fontSize: "16px",
            borderRadius: "6px",
            border: "1px solid #333",
            backgroundColor: "#1f1f1f",
            color: "white",
            marginBottom: "14px",
            boxSizing: "border-box"
          }}
        >
          <option value="">All Genres</option>
          {genres.map((g) => <option key={g} value={g}>{g}</option>)}
        </select>

        {/* Rating Slider */}
        <div style={{ marginBottom: "14px" }}>
          <label style={{ color: "#aaa", fontSize: "14px" }}>
            Minimum Rating: <span style={{ color: "#e50914", fontWeight: "bold" }}>{minRating} ⭐</span>
          </label>
          <input
            type="range"
            min="0" max="5" step="0.5"
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            style={{ width: "100%", accentColor: "#e50914" }}
          />
          <div style={{ display: "flex", justifyContent: "space-between", color: "#555", fontSize: "12px" }}>
            <span>0</span><span>5</span>
          </div>
        </div>

        {/* Year Dropdowns */}
        <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
          <select
            value={yearMin}
            onChange={(e) => setYearMin(e.target.value)}
            style={{
              width: "50%", padding: "14px", fontSize: "16px",
              borderRadius: "6px", border: "1px solid #333",
              backgroundColor: "#1f1f1f", color: yearMin ? "white" : "#555",
              boxSizing: "border-box"
            }}
          >
            <option value="">From Year</option>
            {years.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>

          <select
            value={yearMax}
            onChange={(e) => setYearMax(e.target.value)}
            style={{
              width: "50%", padding: "14px", fontSize: "16px",
              borderRadius: "6px", border: "1px solid #333",
              backgroundColor: "#1f1f1f", color: yearMax ? "white" : "#555",
              boxSizing: "border-box"
            }}
          >
            <option value="">To Year</option>
            {years.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>

        {/* Buttons */}
        <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
          <button
            onClick={() => fetchRecommendations()}
            style={{
              flex: 1, padding: "14px", fontSize: "18px",
              backgroundColor: "#e50914", color: "white",
              border: "none", borderRadius: "6px", cursor: "pointer",
              fontWeight: "bold", letterSpacing: "1px"
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = "#b20710"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#e50914"}
          >
            {loading ? "Searching..." : "Get Recommendations"}
          </button>

          <button
            onClick={feelingLucky}
            style={{
              flex: 1, padding: "14px", fontSize: "18px",
              backgroundColor: "#333", color: "white",
              border: "none", borderRadius: "6px", cursor: "pointer",
              fontWeight: "bold", letterSpacing: "1px"
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = "#555"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#333"}
          >
            {luckyLoading ? "Loading..." : "🎲 I'm Feeling Lucky"}
          </button>
        </div>

        {/* Error */}
        {error && <p style={{ color: "#e50914", textAlign: "center" }}>{error}</p>}

        {/* Results Grid */}
        {results.length > 0 && (
          <div>
            <h2 style={{ color: "#e50914", marginBottom: "16px" }}>Recommendations</h2>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
              gap: "16px"
            }}>
              {results.map((movie, i) => (
                <div key={i} style={{
                  backgroundColor: "#1f1f1f",
                  borderRadius: "8px",
                  overflow: "hidden",
                  textAlign: "center"
                }}>
                  {movie.poster ? (
                    <img
                      src={movie.poster}
                      alt={movie.title}
                      style={{ width: "100%", display: "block" }}
                    />
                  ) : (
                    <div style={{
                      height: "220px",
                      backgroundColor: "#333",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#555",
                      fontSize: "13px"
                    }}>
                      No Poster
                    </div>
                  )}
                  <p style={{
                    padding: "8px",
                    fontSize: "13px",
                    margin: 0,
                    borderTop: "3px solid #e50914"
                  }}>
                    {movie.title}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;