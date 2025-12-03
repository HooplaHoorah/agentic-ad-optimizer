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

// Call the regenerate-image endpoint to update an existing creative's image. The
// body should include the creative_id and optionally a spec_patch with the
// updated prompt or other fields as defined by the backend.
export function regenerateImage(req) {
  return apiPost("/regenerate-image", req);
}
