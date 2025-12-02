const API_BASE = "http://localhost:8000";

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed: ${res.status} ${text}`);
  }

  return res.json();
}

export function createExperimentPlan(snapshot) {
  return apiPost("/experiment-plan", snapshot);
}

export function generateCreatives(plan) {
  return apiPost("/creative-variants", plan);
}

export function scoreCreatives(creatives) {
  return apiPost("/score-creatives", creatives);
}

export function submitResults(results) {
  return apiPost("/results", results);
}
