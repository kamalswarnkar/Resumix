import { useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import api from "../services/api";

function Upload() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!file || !jobDescription.trim()) {
      setError("Upload a file and provide a job description");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploadRes = await api.post("/api/resume/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const analyzeRes = await api.post("/api/resume/analyze/", {
        resume_id: uploadRes.data.id,
        job_description: jobDescription,
      });

      setAnalysis(analyzeRes.data);
    } catch (err) {
      setError(JSON.stringify(err.response?.data || "Failed to analyze resume"));
    } finally {
      setLoading(false);
    }
  };

  const chartData = analysis
    ? [
        { metric: "Keyword", value: analysis.keyword_similarity },
        { metric: "Skill", value: analysis.skill_match_score },
        { metric: "Experience", value: analysis.experience_relevance },
        { metric: "ATS", value: analysis.ats_compliance },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <h1 className="mb-4 text-2xl font-semibold">Upload & Analyze Resume</h1>
        <form onSubmit={submit} className="space-y-3">
          <input type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} className="w-full rounded border p-2" />
          <textarea className="h-40 w-full rounded border p-2" placeholder="Paste job description" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button disabled={loading} className="rounded bg-brand px-4 py-2 text-white disabled:opacity-50">
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </form>
      </div>

      {analysis && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-2 text-xl font-semibold">Result</h2>
            <p className="mb-2">Predicted Role: <strong>{analysis.predicted_role}</strong></p>
            <div className="mb-3 h-4 w-full rounded bg-slate-200">
              <div className="h-4 rounded bg-accent" style={{ width: `${analysis.match_score}%` }} />
            </div>
            <p className="mb-2 text-sm">Match Score: {analysis.match_score}%</p>
            <p className="mb-2 text-sm">Skills Found: {analysis.skills_found.join(", ") || "None"}</p>
            <p className="mb-2 text-sm">Missing Skills: {analysis.skills_missing.join(", ") || "None"}</p>
            <p className="text-sm">Suggestions: {analysis.suggestions}</p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-3 text-xl font-semibold">Score Breakdown</h2>
            <div className="h-64">
              <ResponsiveContainer>
                <RadarChart data={chartData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name="Score" dataKey="value" stroke="#1c6e8c" fill="#1c6e8c" fillOpacity={0.5} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Upload;
