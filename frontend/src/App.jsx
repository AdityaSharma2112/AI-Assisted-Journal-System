import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'
function App() {
  const [userId, setUserId] = useState("123"); // default user
  const [ambience, setAmbience] = useState(""); 
  const [text, setText] = useState("");
  const [entries, setEntries] = useState([]);
  const [insights, setInsights] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const fetchEntries = async ()=>{
    const response = (await axios.get(`http://localhost:8000/api/journal/${userId}`)).data
    setEntries(response)
  }
  useEffect(()=>{
    fetchEntries();
    getInsights();
  },[])

  async function saveEntry() {
    const response = await axios.post("http://localhost:8000/api/journal", {
      userId:userId,
      ambience: ambience,
      text: text
    })
    fetchEntries()
  }

  async function analyze(){
    const response = (await axios.post("http://localhost:8000/api/journal/analyze",{
      text: text
    })).data
    console.log(response)
    setAnalysis(response)
  }

  async function getInsights(){
    const response = (await axios.get(`http://localhost:8000/api/journal/insights/${userId}`)).data
    setInsights(response)
  }

  return (
    <>
      <div className="min-h-screen bg-gray-100 flex justify-center p-6">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-xl p-6">
        <h1 className="text-2xl font-bold mb-4">My Journal</h1>

        <input type="text" value={userId} onChange={(e) => setUserId(String(e.target.value))} placeholder="User ID" className="w-full border rounded-lg p-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-400"/>
        <input type="text" value={ambience} onChange={(e) => setAmbience(e.target.value)} placeholder="Ambience (e.g., rain, cafe)" className="w-full border rounded-lg p-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-400"/>
        <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Write your thoughts..." rows={4} className="w-full border rounded-lg p-3 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-400"></textarea>

        <div className="flex gap-3 mb-6">
          <button onClick={saveEntry} className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
            Save Entry
          </button>

          <button onClick={analyze} className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg">
            Analyze
          </button>
        </div>
        {analysis && (
          <>
            <h2 className="text-xl font-semibold mt-6 mb-2">Analyze</h2>
            <div className="bg-purple-50 p-4 rounded-lg text-gray-700 space-y-2">
              <p><b>Emotion:</b> {analysis.emotion}</p>
              <p><b>Keywords:</b> {analysis.keywords.join(", ")}</p>
              <p><b>Summary:</b> {analysis.summary}</p>
            </div>
          </>
        )}
        {/* Insights */}
        {insights && (
          <>
            <h2 className="text-xl font-semibold mt-6 mb-2">Insights</h2>
            <div className="bg-blue-50 p-4 rounded-lg text-gray-700">
              <p><b>Total Entries:</b> {insights.totalEntries}</p>
              <p><b>Top Emotion:</b> {insights.topEmotion}</p>
              <p><b>Ambience:</b> {insights.mostUsedAmbience}</p>
              <p><b>Keywords:</b> {insights.recentKeywords.join(", ")}</p>
            </div>
          </>
        )}

        {/* Previous Entries */}
        <h2 className="text-xl font-semibold mb-2">Previous Entries</h2>
        <div className="space-y-2">
          {entries.map((e, idx) => (
            <div key={idx} className="bg-gray-100 p-3 rounded-lg">
              <p>{e.text}</p>
              {e.ambience && (
                <span className="text-sm text-gray-500">Ambience: {e.ambience}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
    </>
  )
}

export default App
