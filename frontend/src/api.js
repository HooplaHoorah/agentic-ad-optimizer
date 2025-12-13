const API_BASE = "http://localhost:8000";

/**
 * Enhanced API wrapper with friendly error messages
 * Implements Fix B from instructions5.md - no raw "Failed to fetch" errors
 */
async function apiPost(path, body) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();

      // Try to parse error details if backend provides them
      let errorMessage = `Request failed with status ${res.status}`;
      try {
        const errorJson = JSON.parse(text);
        if (errorJson.detail) {
          errorMessage = errorJson.detail;
        }
      } catch {
        // If not JSON, use the text as-is if it's short enough
        if (text.length < 200) {
          errorMessage = text || errorMessage;
        }
      }

      throw new Error(errorMessage);
    }

    return res.json();
  } catch (err) {
    // Detect network failures and provide actionable guidance
    if (err.message.includes('fetch') || err.name === 'TypeError') {
      throw new Error(
        `Backend not reachable at ${API_BASE}. Make sure the backend server is running (uvicorn backend.app.main:app --reload --port 8000) and try again.`
      );
    }

    // Re-throw other errors (HTTP errors, JSON parsing errors, etc.)
    throw err;
  }
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

// Call the regenerate-image endpoint to update an existing creative's image.
// The body should include the full variant object and a spec_patch with optional
// fields (prompt, lighting_style, color_palette, etc.) to override in the fibo_spec.
export function regenerateImage(req) {
  return apiPost("/regenerate-image", req);
}

// Phase 3.1 Task B: Explore visual variants
// Generate 8 variants by exploring combinations of FIBO parameters
export function exploreVariants(req) {
  return apiPost("/explore-variants", req);
}

// Phase 3.2 Task A: Backend Health Check
export async function checkHealth() {
  try {
    // Set a short timeout for health checks so the UI doesn't hang
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const res = await fetch(`${API_BASE}/health`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`Backend returned status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("Health check failed:", err);
    throw err;
  }
}


// Phase 3.3 Task A: Auto-fix guardrails
export function applyGuardrails(req) {
  return apiPost("/apply-guardrails", req);
}
