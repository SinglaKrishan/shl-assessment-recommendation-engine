import { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [query, setQuery] = useState("");
  const [remote, setRemote] = useState(null);
  const [adaptive, setAdaptive] = useState(null);
  const [testType, setTestType] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  // Initialize theme from local storage
  useEffect(() => {
    const saved = localStorage.getItem("theme") === "dark";
    setDarkMode(saved);
    document.documentElement.classList.toggle("dark", saved);
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
    localStorage.setItem("theme", newMode ? "dark" : "light");
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await axios.post("https://41167bdda1a0.ngrok-free.app/recommend", {
        query,
        k: 10,
        remote_preferred: remote,
        adaptive_preferred: adaptive,
        test_type_preference: testType,
      });

      setResults(response.data.results);
    } catch (err) {
      setError("Backend not reachable. Start FastAPI.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen transition bg-gray-100 dark:bg-gray-900 dark:text-white px-6 py-10 flex flex-col items-center">

      {/* Header + Theme Toggle */}
      <div className="flex justify-between items-center w-full max-w-5xl mb-8">
        <h1 className="text-3xl md:text-4xl font-bold">
          SHL Assessment Recommendation Engine
        </h1>

        <button
          onClick={toggleTheme}
          className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:scale-105 transition"
        >
          {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

      {/* Search Bar */}
      <div className="flex gap-3 w-full max-w-4xl mb-6">
        <input
          type="text"
          placeholder="software engineering coding test"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-800"
        />
        <button
          onClick={handleSearch}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setRemote(remote === true ? null : true)}
          className={`px-5 py-2 rounded-lg border ${
            remote ? "bg-blue-600 text-white" : "dark:bg-gray-800"
          }`}
        >
          Remote
        </button>

        <button
          onClick={() => setAdaptive(adaptive === true ? null : true)}
          className={`px-5 py-2 rounded-lg border ${
            adaptive ? "bg-blue-600 text-white" : "dark:bg-gray-800"
          }`}
        >
          Adaptive
        </button>

        <select
          value={testType}
          onChange={(e) => setTestType(e.target.value)}
          className="px-4 py-2 rounded-lg border bg-white dark:bg-gray-800 dark:border-gray-600"
        >
          <option value="">Test Type</option>
          <option value="K">Knowledge</option>
          <option value="S">Simulation</option>
          <option value="P">Personality</option>
        </select>
      </div>

      {/* Loader */}
      {loading && <p className="text-lg font-semibold animate-pulse">Searching...</p>}

      {/* Error */}
      {error && <p className="text-red-500">{error}</p>}

      {/* Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full max-w-5xl">
        {results.map((item, idx) => (
          <div
            key={idx}
            className="rounded-xl p-6 bg-white dark:bg-gray-800 shadow-md border dark:border-gray-700 hover:shadow-xl transition"
          >
            <h3 className="text-xl font-bold mb-3">{item.name}</h3>
            <p className="text-sm opacity-80 mb-3">{item.long_description}</p>
            <p className="text-xs opacity-70 mb-3">
              Test Type: {item.test_type} • Remote: {item.remote_support} • Adaptive: {item.adaptive_support}
            </p>

            <button
              onClick={() => window.open(item.url, "_blank")}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
