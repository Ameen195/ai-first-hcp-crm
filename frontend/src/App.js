import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const API_BASE_URL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : `${window.location.origin}/api`);

function App() {
  const dispatch = useDispatch();
  const { interaction, loading, error } = useSelector((state) => state);

  const [formData, setFormData] = useState({
    hcp_name: '',
    specialty: '',
    objective: '',
    notes: '',
    channel: 'phone',
    next_step: '',
    follow_up_date: '',
    chat_message: '',
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const submitInteraction = async (event) => {
    event.preventDefault();
    dispatch({ type: 'interaction/loading' });
    try {
      const response = await fetch(`${API_BASE_URL}/interaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      dispatch({ type: 'interaction/success', payload: data });
    } catch (err) {
      dispatch({ type: 'interaction/error', payload: err.message || 'Unable to reach backend service.' });
    }
  };

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">AI-first CRM • HCP Module</p>
          <h1>Log Interaction Screen</h1>
          <p className="subtext">Capture HCP engagements through a structured form or a conversational chat workflow.</p>
        </div>
      </header>

      <main className="content-grid">
        <section className="panel">
          <h2>Structured entry</h2>
          <form onSubmit={submitInteraction}>
            <label>
              HCP Name
              <input name="hcp_name" value={formData.hcp_name} onChange={handleChange} placeholder="Dr. Maya Singh" />
            </label>
            <label>
              Specialty
              <input name="specialty" value={formData.specialty} onChange={handleChange} placeholder="Oncology" />
            </label>
            <label>
              Objective
              <input name="objective" value={formData.objective} onChange={handleChange} placeholder="Discuss trial access and follow-up" />
            </label>
            <label>
              Channel
              <select name="channel" value={formData.channel} onChange={handleChange}>
                <option value="phone">Phone</option>
                <option value="email">Email</option>
                <option value="video">Video</option>
                <option value="in_person">In-person</option>
              </select>
            </label>
            <label>
              Notes
              <textarea name="notes" value={formData.notes} onChange={handleChange} placeholder="Capture insight gathered from the conversation" />
            </label>
            <label>
              Chat message
              <textarea name="chat_message" value={formData.chat_message} onChange={handleChange} placeholder="Or describe the interaction conversationally" />
            </label>
            <button type="submit">Log interaction</button>
          </form>
        </section>

        <section className="panel">
          <h2>LangGraph agent output</h2>
          {loading && <p>Processing with LangGraph and Groq...</p>}
          {error && <p className="error">{error}</p>}
          {interaction && (
            <div className="result-card">
              <p><strong>Mode:</strong> {interaction.mode}</p>
              <p><strong>Intent:</strong> {interaction.intent}</p>
              <p><strong>Summary:</strong> {interaction.summary}</p>
              <div>
                <strong>Tools used</strong>
                <ul>
                  {interaction.tools_used.map((tool) => <li key={tool}>{tool}</li>)}
                </ul>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;