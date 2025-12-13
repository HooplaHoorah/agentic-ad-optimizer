import React, { useState, useEffect } from "react";
import {
  createExperimentPlan,
  generateCreatives,
  scoreCreatives,
  regenerateImage,
  submitResults,
  exploreVariants,
} from "./api";

function Stepper({ step }) {
  const steps = [
    "Business snapshot",
    "Plan & creatives",
    "Results & next moves",
  ];
  return (
    <div className="stepper">
      {steps.map((label, index) => {
        const stepIndex = index + 1;
        const active = stepIndex === step;
        return (
          <div
            key={label}
            className={`step-pill ${active ? "active" : ""}`}
          >
            <span className="step-index">{stepIndex}</span>
            <span>{label}</span>
          </div>
        );
      })}
    </div>
  );
}

function App() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastFailedRequest, setLastFailedRequest] = useState(null); // For retry functionality

  const [snapshot, setSnapshot] = useState(null);
  const [plan, setPlan] = useState(null);
  const [creatives, setCreatives] = useState([]);
  const [scores, setScores] = useState([]);
  const [recommendation, setRecommendation] = useState(null);

  const [formValues, setFormValues] = useState({
    productName: "Math Wars Meta DIY Kit",
    price: 49,
    mainBenefit: "Turns math practice into a co-op board game",
    audienceSegment: "Parents of 7–12 year olds",
    audiencePain: "Kids hate math homework",
  });

  const [resultRows, setResultRows] = useState([]);

  const [patchPrompts, setPatchPrompts] = useState({});
  const [winnerVariantId, setWinnerVariantId] = useState("");
  const [expandedSpecs, setExpandedSpecs] = useState({}); // Track which spec inspectors are expanded
  const [activeExplorationGrid, setActiveExplorationGrid] = useState(null); // Track active exploration grid popout: { variantId, variantName, variants: [] }


  // Fix A: Clear errors when step changes
  useEffect(() => {
    setError("");
    setLastFailedRequest(null);
  }, [step]);

  useEffect(() => {
    if (plan && plan.variants && plan.variants.length > 0) {
      const defaults = plan.variants.map((v, idx) => ({
        variant_id: v.variant_id,
        impressions: 10000,
        clicks: 300 + idx * 50,
        conversions: 20 + idx * 5,
        spend: 300,
        revenue: 800 + idx * 200,
      }));
      setResultRows(defaults);
      setWinnerVariantId(plan.variants[0].variant_id);
    }
  }, [plan]);

  // Campaign Templates for quick scenario selection
  const campaignTemplates = {
    dtc_ecom: {
      name: "DTC E-commerce",
      productName: "LunaGlow Sunscreen SPF 50",
      price: 32,
      mainBenefit: "Reef-safe, non-greasy formula that lasts all day",
      audienceSegment: "Health-conscious millennials aged 25-40",
      audiencePain: "Sunscreens feel heavy and leave white residue",
    },
    saas: {
      name: "SaaS Product",
      productName: "FlowPilot AI Scheduler",
      price: 49,
      mainBenefit: "AI-powered calendar that saves 5+ hours per week",
      audienceSegment: "Busy professionals and team leads",
      audiencePain: "Calendar chaos and back-to-back meetings",
    },
    local_service: {
      name: "Local Service",
      productName: "Austin Mobile Detailing Pro",
      price: 149,
      mainBenefit: "Premium car detailing at your doorstep in 90 minutes",
      audienceSegment: "Austin car owners who value convenience",
      audiencePain: "No time to take car to detailers, long wait times",
    },
  };

  const handleTemplateSelect = (templateKey) => {
    if (templateKey === "") {
      // Reset to default
      setFormValues({
        productName: "Math Wars Meta DIY Kit",
        price: 49,
        mainBenefit: "Turns math practice into a co-op board game",
        audienceSegment: "Parents of 7–12 year olds",
        audiencePain: "Kids hate math homework",
      });
    } else {
      const template = campaignTemplates[templateKey];
      setFormValues({
        productName: template.productName,
        price: template.price,
        mainBenefit: template.mainBenefit,
        audienceSegment: template.audienceSegment,
        audiencePain: template.audiencePain,
      });
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSnapshotSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setRecommendation(null);
    setScores([]);
    setCreatives([]);

    const snapshotBody = {
      products: [
        {
          id: "product_1",
          name: formValues.productName || "Demo Product",
          price: Number(formValues.price) || 0,
          margin: null,
          category: null,
          benefits: formValues.mainBenefit
            ? [formValues.mainBenefit]
            : ["High-converting, AI-optimized offer"],
          objections: ["Budget constraints"],
        },
      ],
      audiences: [
        {
          segment:
            formValues.audienceSegment || "Primary performance marketing audience",
          pain_points: formValues.audiencePain
            ? [formValues.audiencePain]
            : ["Rising CAC", "Creative fatigue"],
          jobs_to_be_done: ["Improve ROAS", "Scale winners with less thrash"],
        },
      ],
      historical_performance: [],
      sales_data: [],
    };

    try {
      const planResponse = await createExperimentPlan(snapshotBody);
      setSnapshot(snapshotBody);
      setPlan(planResponse);
      setStep(2);
      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to create experiment plan.");
      setLastFailedRequest({ action: 'createPlan', payload: snapshotBody });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCreatives = async () => {
    if (!plan) return;
    setError("");
    setLoading(true);
    setScores([]);
    setRecommendation(null);
    try {
      const creativeResponse = await generateCreatives(plan);
      setCreatives(creativeResponse);
      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to generate creatives.");
      setLastFailedRequest({ action: 'generateCreatives', payload: plan });
    } finally {
      setLoading(false);
    }
  };

  const handleScoreCreatives = async () => {
    if (!creatives.length) return;
    setError("");
    setLoading(true);
    setRecommendation(null);
    try {
      const scoresResponse = await scoreCreatives(creatives);
      setScores(scoresResponse);
      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to score creatives.");
      setLastFailedRequest({ action: 'scoreCreatives', payload: creatives });
    } finally {
      setLoading(false);
    }
  };

  const handleResultChange = (idx, field, value) => {
    setResultRows((rows) =>
      rows.map((row, i) =>
        i === idx ? { ...row, [field]: value } : row
      )
    );
  };

  const handleResultsSubmit = async (e) => {
    e.preventDefault();
    if (!plan) return;
    setError("");
    setLoading(true);
    try {
      const resultsPayload = resultRows.map((row) => {
        const impressions = Number(row.impressions) || 0;
        const clicks = Number(row.clicks) || 0;
        const conversions = Number(row.conversions) || 0;
        const spend = Number(row.spend) || 0;
        const revenue = Number(row.revenue) || 0;
        const profit = revenue - spend;
        const cac = conversions > 0 ? spend / conversions : 0;
        const roas = spend > 0 ? revenue / spend : 0;
        return {
          variant_id: row.variant_id,
          impressions,
          clicks,
          conversions,
          spend,
          revenue,
          profit,
          cac,
          roas,
        };
      });

      const body = {
        experiment_id: plan.experiment_id,
        winner_variant_id: winnerVariantId,
        results: resultsPayload,
      };

      const rec = await submitResults(body);
      setRecommendation(rec);
      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to process results.");
      setLastFailedRequest({ action: 'submitResults', payload: body });
    } finally {
      setLoading(false);
    }
  };

  const getScoreForVariant = (variantId) => {
    if (!scores || !scores.length) return null;
    return scores.find((s) => s.creative_id === variantId);
  };


  /**
   * Handle updates to the prompt override for a given creative.
   * @param {string} variantId - The variant ID for which to update the draft prompt.
   * @param {string} value - The new prompt value.
   */
  const handlePatchChange = (variantId, value) => {
    setPatchPrompts((prev) => ({ ...prev, [variantId]: value }));
  };

  const handlePreset = (variantId, presetName) => {
    let presetPrompt = "";
    let presetSpec = {}; // Not used directly here, but could be pre-filled into a spec viewer

    if (presetName === "product") {
      presetPrompt = "Professional product photography, studio lighting, eye level";
    } else if (presetName === "lifestyle") {
      presetPrompt = "Lifestyle photography, warm natural lighting, candid moment";
    } else if (presetName === "punchy") {
      presetPrompt = "Vibrant advertisement, high contrast, dramatic lighting, close up";
    } else if (presetName === "lockLighting") {
      // Task #3: Lock composition, change only lighting - minimal controlled experiment
      presetPrompt = "Same framing, warmer lighting with golden hour glow";
    }
    setPatchPrompts((prev) => ({ ...prev, [variantId]: presetPrompt }));
  };

  /**
   * Toggle the spec inspector for a specific variant
   */
  const toggleSpecInspector = (variantId) => {
    setExpandedSpecs((prev) => ({
      ...prev,
      [variantId]: !prev[variantId]
    }));
  };

  /**
   * Copy the fibo_spec JSON to clipboard
   */
  const copySpecToClipboard = (spec) => {
    const specText = JSON.stringify(spec, null, 2);
    navigator.clipboard.writeText(specText).then(() => {
      // Could show a temporary "Copied!" message here
      console.log('Spec copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy spec:', err);
    });
  };


  /**
   * Trigger regeneration of an image using the regenerate-image endpoint.
   * If a prompt override has been provided for the variant, it is passed in the
   * spec_patch; otherwise an empty spec is sent. On success the updated creative
   * replaces the old creative in state.
   * @param {string} variantId - The variant ID to regenerate.
   */
  const handleRegenerateImage = async (variantId) => {
    setError("");
    setLoading(true);
    try {
      // Find the full variant object to send to the backend
      const variant = creatives.find((c) => c.variant_id === variantId);
      if (!variant) {
        throw new Error(`Variant ${variantId} not found`);
      }

      const specPatch = {};
      const changedFields = []; // Track what changed for display

      if (patchPrompts[variantId]) {
        specPatch.prompt = patchPrompts[variantId];
        changedFields.push('prompt');
      }

      // Apply implicit specs based on keywords to simulate "agentic" choices without full UI controls
      const promptLower = (patchPrompts[variantId] || "").toLowerCase();

      // Special handling for "lock lighting" preset - only change lighting, lock composition
      if (promptLower.includes("same framing") || promptLower.includes("lock")) {
        specPatch.lighting_style = "warm";
        specPatch.color_palette = "warm_golden";
        changedFields.push('lighting_style', 'color_palette');
      } else if (promptLower.includes("studio")) {
        specPatch.background_type = "studio";
        specPatch.lighting_style = "soft";
        changedFields.push('background_type', 'lighting_style');
      } else if (promptLower.includes("lifestyle")) {
        specPatch.background_type = "lifestyle";
        specPatch.lighting_style = "warm";
        changedFields.push('background_type', 'lighting_style');
      } else if (promptLower.includes("dramatic")) {
        specPatch.lighting_style = "dramatic";
        specPatch.color_palette = "vibrant";
        changedFields.push('lighting_style', 'color_palette');
      }

      // Send the full variant object and spec_patch as the backend expects
      const body = {
        variant: variant,
        spec_patch: specPatch,
      };
      const updatedCreative = await regenerateImage(body);
      setCreatives((prev) =>
        prev.map((c) => {
          if (c.variant_id === updatedCreative.variant_id) {
            // Preserve history and track what changed
            return {
              ...updatedCreative,
              previous_image_url: c.image_url,
              previous_timestamp: c.timestamp || new Date().toLocaleTimeString(),
              timestamp: new Date().toLocaleTimeString(),
              changed_fields: changedFields, // Store for display
              spec_patch_used: specPatch // Store the actual patch for reference
            };
          }
          return c;
        })
      );
      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to regenerate image.");
      setLastFailedRequest({ action: 'regenerateImage', payload: body });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Phase 3.1 Task B: Explore 8 visual variants
   * Generates a grid of 8 variants exploring FIBO parameter combinations
   * Opens in a full-width popout panel at the bottom
   */
  const handleExploreVariants = async (variantId) => {
    setError("");
    setLoading(true);
    try {
      const variant = creatives.find((c) => c.variant_id === variantId);
      if (!variant) {
        throw new Error(`Variant ${variantId} not found`);
      }

      const req = {
        base_variant: variant,
        axes: {
          lighting_style: ["warm", "cool"],
          color_palette: ["warm_golden", "pastel"],
          background_type: ["studio", "natural"]
        }
      };

      const response = await exploreVariants(req);

      // Open the exploration grid popout panel
      setActiveExplorationGrid({
        variantId: variant.variant_id,
        variantName: `Variant ${variant.variant_id}`, // e.g., "Variant B"
        variants: response.generated
      });

      console.log(`Explored ${response.meta.count} variants in ${response.meta.runtime_ms}ms`);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to explore variants.");
    } finally {
      setLoading(false);
    }
  };




  /**
   * Fix C: Retry the last failed request
   */
  const handleRetry = async () => {
    if (!lastFailedRequest) return;

    setError("");
    setLoading(true);

    try {
      const { action, payload } = lastFailedRequest;

      switch (action) {
        case 'createPlan':
          const planResponse = await createExperimentPlan(payload);
          setSnapshot(payload);
          setPlan(planResponse);
          setStep(2);
          break;

        case 'generateCreatives':
          const creativeResponse = await generateCreatives(payload);
          setCreatives(creativeResponse);
          break;

        case 'scoreCreatives':
          const scoresResponse = await scoreCreatives(payload);
          setScores(scoresResponse);
          break;

        case 'submitResults':
          const rec = await submitResults(payload);
          setRecommendation(rec);
          break;

        case 'regenerateImage':
          const updatedCreative = await regenerateImage(payload);
          setCreatives((prev) =>
            prev.map((c) => {
              if (c.variant_id === updatedCreative.variant_id) {
                return {
                  ...updatedCreative,
                  previous_image_url: c.image_url,
                  previous_timestamp: c.timestamp || new Date().toLocaleTimeString(),
                  timestamp: new Date().toLocaleTimeString()
                };
              }
              return c;
            })
          );
          break;

        default:
          throw new Error('Unknown action to retry');
      }

      setLastFailedRequest(null); // Clear on success
    } catch (err) {
      console.error('Retry failed:', err);
      setError(err.message || "Retry failed. Please try again.");
      // Keep lastFailedRequest so user can retry again
    } finally {
      setLoading(false);
    }
  };

  const handleStartOver = () => {
    setStep(1);
    setSnapshot(null);
    setPlan(null);
    setCreatives([]);
    setScores([]);
    setRecommendation(null);
    setError("");
  };

  const handleExport = () => {
    // Create exportable artifact bundle
    const exportData = {
      experiment_plan: plan,
      creative_variants: creatives,
      scores: scores,
      recommendation: recommendation,
      spec_patches_used: patchPrompts,
      export_timestamp: new Date().toISOString(),
    };

    // Create a JSON file for download
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `agentic-ad-optimizer-export-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-root">
      <div className="card">
        <div className="header-row">
          <div>
            <h1>Agentic Ad Optimizer</h1>
            <p className="subtitle">
              Bring experiment design, creative generation, and optimization into one agentic loop.
            </p>
          </div>
          <div className="header-actions">
            {loading && <span className="loading-indicator">Working…</span>}
            {step > 1 && (
              <button className="reset-btn" onClick={handleStartOver}>
                ↻ Start over
              </button>
            )}
          </div>
        </div>

        <Stepper step={step} />

        {error && !loading && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            {lastFailedRequest && (
              <button
                className="retry-btn"
                onClick={handleRetry}
                disabled={loading}
              >
                🔄 Retry
              </button>
            )}
          </div>
        )}
        {recommendation && !error && (
          <div className="success-banner">
            ✅ Loop complete. You&apos;ve got a winner and a next test to run.
          </div>
        )}

        {step === 1 && (
          <section className="section">
            <div className="section-title">1. Business snapshot</div>
            <div className="section-subtitle">
              Just enough context for the agent to design a smart test.
            </div>

            <form onSubmit={handleSnapshotSubmit}>
              <label>
                Campaign Template (optional)
                <select
                  onChange={(e) => handleTemplateSelect(e.target.value)}
                  defaultValue=""
                >
                  <option value="">Custom (default)</option>
                  <option value="dtc_ecom">🛍️ DTC E-commerce - LunaGlow Sunscreen</option>
                  <option value="saas">💻 SaaS - FlowPilot AI Scheduler</option>
                  <option value="local_service">🚗 Local Service - Austin Mobile Detailing</option>
                </select>
              </label>

              <label>
                Product name
                <input
                  type="text"
                  name="productName"
                  placeholder="e.g., Math Wars Meta DIY Kit"
                  value={formValues.productName}
                  onChange={handleInputChange}
                />
              </label>

              <div className="field-row">
                <label>
                  Price (USD)
                  <input
                    type="number"
                    name="price"
                    value={formValues.price}
                    onChange={handleInputChange}
                  />
                </label>
                <label>
                  Main benefit
                  <input
                    type="text"
                    name="mainBenefit"
                    placeholder="e.g., Makes math practice feel like a co-op game"
                    value={formValues.mainBenefit}
                    onChange={handleInputChange}
                  />
                </label>
              </div>

              <div className="field-row">
                <label>
                  Audience segment
                  <input
                    type="text"
                    name="audienceSegment"
                    placeholder="e.g., Parents of 7–12 year olds"
                    value={formValues.audienceSegment}
                    onChange={handleInputChange}
                  />
                </label>
                <label>
                  #1 pain point
                  <input
                    type="text"
                    name="audiencePain"
                    placeholder="e.g., Kids hate math homework"
                    value={formValues.audiencePain}
                    onChange={handleInputChange}
                  />
                </label>
              </div>

              <div className="button-row">
                <button type="submit" disabled={loading}>
                  {loading ? "Generating plan…" : "Generate experiment plan"}
                </button>
              </div>
            </form>
          </section>
        )}

        {step === 2 && plan && (
          <section className="section">
            <div className="section-title">2. Plan & creatives</div>
            <div className="section-subtitle">
              Review the experiment plan, then spin up creatives and scores.
            </div>

            <div className="section">
              <div className="section-title">Experiment plan</div>
              <p className="tagline">
                Objective: <strong>{plan.objective}</strong>
                <br />
                Hypothesis: {plan.hypothesis}
              </p>

              <table>
                <thead>
                  <tr>
                    <th>Variant</th>
                    <th>Role</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {plan.variants.map((v) => (
                    <tr key={v.variant_id}>
                      <td>{v.variant_id}</td>
                      <td>{v.control ? <span className="pill">Control</span> : "Test"}</td>
                      <td>{v.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <p className="tagline">
                Metrics: {plan.metrics?.join(", ") || "Not specified"} · Minimum spend per
                variant: {plan.sample_size_rules?.min_spend_per_variant ?? 0} · Minimum
                conversions: {plan.sample_size_rules?.min_conversions ?? 0}
              </p>
            </div>

            <div className="button-row">
              <button onClick={handleGenerateCreatives} disabled={loading}>
                {loading ? "Working…" : "Generate creatives"}
              </button>
              <button
                className="secondary"
                onClick={() => setStep(1)}
                disabled={loading}
              >
                ← Back
              </button>
              {creatives.length > 0 && (
                <button
                  className="secondary"
                  onClick={() => setStep(3)}
                  disabled={loading}
                >
                  Skip to results
                </button>
              )}
            </div>

            {creatives.length > 0 && (
              <div className="section">
                <div className="section-title">Creative variants</div>
                <div className="section-subtitle">
                  Each card maps to a variant in the plan.
                </div>
                <div className="creative-grid">
                  {creatives.map((c) => {
                    const score = getScoreForVariant(c.variant_id);
                    return (
                      <div key={c.variant_id} className="creative-card">
                        <h3>Variant {c.variant_id}</h3>
                        <div className="creative-meta">
                          {plan.variants.find(
                            (v) => v.variant_id === c.variant_id
                          )?.description || ""}
                        </div>
                        {c.image_url && (
                          <div className="creative-image" style={{ marginTop: "0.5rem" }}>
                            <div className="status-badge-container">
                              {c.image_status === "fibo" ? (
                                <span className="status-badge live">Bria FIBO: LIVE ✅ (JSON-controlled)</span>
                              ) : (
                                <span className="status-badge mock">Mock ⚠️ (set FIBO_API_KEY to generate)</span>
                              )}
                            </div>

                            {c.previous_image_url ? (
                              <div className="thumbnails-row">
                                <div style={{ width: '50%' }}>
                                  <div className="thumb-title">Previous ({c.previous_timestamp})</div>
                                  <img
                                    src={c.previous_image_url}
                                    alt="Previous version"
                                    className="thumb-img"
                                  />
                                </div>
                                <div style={{ width: '50%' }}>
                                  <div className="thumb-title">Current ({c.timestamp || new Date().toLocaleTimeString()})</div>
                                  <img
                                    src={c.image_url}
                                    alt="Current version"
                                    className="thumb-img"
                                  />
                                </div>
                              </div>
                            ) : (
                              <img
                                src={c.image_url}
                                alt="Creative image"
                                style={{ width: "100%", borderRadius: "4px", marginTop: "0.5rem" }}
                              />
                            )}
                          </div>
                        )}

                        {/* Task #2 Feature B: Show what changed on regeneration */}
                        {c.changed_fields && c.changed_fields.length > 0 && (
                          <div style={{ marginTop: "0.75rem", padding: "0.5rem", background: "rgba(34, 197, 94, 0.1)", borderRadius: "6px", border: "1px solid rgba(74, 222, 128, 0.3)" }}>
                            <div style={{ fontSize: "0.75rem", color: "#86efac", fontWeight: "600", marginBottom: "0.25rem" }}>
                              🔄 Changed fields:
                            </div>
                            <div style={{ fontSize: "0.7rem", color: "#bbf7d0" }}>
                              {c.changed_fields.join(", ")}
                            </div>
                          </div>
                        )}

                        {/* Task #2 Feature A: Spec Inspector */}
                        {c.fibo_spec && (
                          <div style={{ marginTop: "0.75rem" }}>
                            <button
                              className="spec-inspector-toggle"
                              onClick={() => toggleSpecInspector(c.variant_id)}
                              style={{
                                fontSize: "0.75rem",
                                padding: "0.35rem 0.6rem",
                                background: "rgba(59, 130, 246, 0.15)",
                                border: "1px solid rgba(96, 165, 250, 0.4)",
                                color: "#93c5fd",
                                borderRadius: "4px",
                                cursor: "pointer",
                                width: "100%",
                                textAlign: "left",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center"
                              }}
                            >
                              <span>📋 Spec Inspector ({c.image_status})</span>
                              <span>{expandedSpecs[c.variant_id] ? "▼" : "▶"}</span>
                            </button>
                            {expandedSpecs[c.variant_id] && (
                              <div style={{ marginTop: "0.5rem", padding: "0.5rem", background: "rgba(15, 23, 42, 0.95)", borderRadius: "4px", border: "1px solid rgba(148, 163, 184, 0.3)" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                  <span style={{ fontSize: "0.7rem", color: "#94a3b8" }}>FIBO Spec JSON:</span>
                                  <button
                                    onClick={() => copySpecToClipboard(c.fibo_spec)}
                                    style={{
                                      fontSize: "0.7rem",
                                      padding: "0.25rem 0.5rem",
                                      background: "rgba(34, 197, 94, 0.2)",
                                      border: "1px solid rgba(74, 222, 128, 0.4)",
                                      color: "#86efac",
                                      borderRadius: "4px",
                                      cursor: "pointer"
                                    }}
                                  >
                                    📋 Copy JSON
                                  </button>
                                </div>
                                <pre style={{
                                  fontSize: "0.65rem",
                                  color: "#e2e8f0",
                                  background: "rgba(0, 0, 0, 0.3)",
                                  padding: "0.5rem",
                                  borderRadius: "4px",
                                  overflow: "auto",
                                  maxHeight: "200px",
                                  margin: 0
                                }}>
                                  {JSON.stringify(c.fibo_spec, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                        {/* Removed raw image status text in favor of badge */}


                        <div className="creative-body" style={{ marginTop: "1rem" }}>
                          <strong>Hook:</strong> {c.hook}
                          <br />
                          <strong>Primary text:</strong> {c.primary_text}
                          <br />
                          <strong>Headline:</strong> {c.headline}
                        </div>
                        <div className="cta-pill">
                          CTA: {c.call_to_action}
                        </div>
                        {score && (
                          <div>
                            <div className="score-chip">
                              Overall {score.overall_strength?.toFixed(1) ?? "—"}/10
                            </div>
                            <div className="feedback">
                              {score.feedback || "No feedback provided."}
                            </div>
                          </div>
                        )}
                        {c.image_url && (
                          <div style={{ marginTop: "0.5rem" }}>
                            <div className="preset-row">
                              <button className="preset-btn" onClick={() => handlePreset(c.variant_id, "product")}>Product Shot</button>
                              <button className="preset-btn" onClick={() => handlePreset(c.variant_id, "lifestyle")}>Lifestyle</button>
                              <button className="preset-btn" onClick={() => handlePreset(c.variant_id, "punchy")}>Punchy Ad</button>
                              <button
                                className="preset-btn"
                                onClick={() => handlePreset(c.variant_id, "lockLighting")}
                                style={{ background: "rgba(251, 191, 36, 0.15)", borderColor: "rgba(250, 204, 21, 0.5)", color: "#fde047" }}
                              >
                                🔒 Lock Lighting
                              </button>
                            </div>
                            <input
                              type="text"
                              placeholder="Optional prompt override"
                              value={patchPrompts[c.variant_id] || ""}
                              onChange={(e) => handlePatchChange(c.variant_id, e.target.value)}
                              style={{ width: "100%", marginBottom: "0.25rem" }}
                            />
                            <button
                              onClick={() => handleRegenerateImage(c.variant_id)}
                              disabled={loading}
                            >
                              Regenerate image
                            </button>

                            {/* Phase 3.1 Task B: Explore 8 Visual Variants Button */}
                            <button
                              onClick={() => handleExploreVariants(c.variant_id)}
                              disabled={loading}
                              style={{
                                marginTop: "0.5rem",
                                background: "rgba(139, 92, 246, 0.15)",
                                borderColor: "rgba(167, 139, 250, 0.5)",
                                color: "#c4b5fd"
                              }}
                            >
                              🔍 Explore 8 Visual Variants
                            </button>
                          </div>
                        )}

                      </div>
                    );
                  })}
                </div>

                <div className="button-row">
                  <button
                    onClick={handleScoreCreatives}
                    disabled={loading || !creatives.length}
                  >
                    {loading ? "Scoring…" : "Score creatives"}
                  </button>
                  {scores.length > 0 && (
                    <button
                      className="secondary"
                      onClick={() => setStep(3)}
                      disabled={loading}
                    >
                      Next: Results & next moves →
                    </button>
                  )}
                </div>
              </div>
            )}
          </section>
        )}

        {step === 3 && plan && (
          <section className="section">
            <div className="section-title">3. Results & next moves</div>
            <div className="section-subtitle">
              Plug in performance to see the winner and the next test the agent recommends.
            </div>

            <form onSubmit={handleResultsSubmit}>
              <label>
                Winning variant ID
                <select
                  value={winnerVariantId}
                  onChange={(e) => setWinnerVariantId(e.target.value)}
                >
                  {plan.variants.map((v) => (
                    <option key={v.variant_id} value={v.variant_id}>
                      {v.variant_id}
                    </option>
                  ))}
                </select>
              </label>

              <div className="section">
                <div className="section-title">Variant performance</div>
                <div className="section-subtitle">
                  Defaults are provided; tweak them to match your real test.
                </div>
                <div className="results-grid">
                  <table>
                    <thead>
                      <tr>
                        <th>Variant</th>
                        <th>Impr.</th>
                        <th>Clicks</th>
                        <th>Conv.</th>
                        <th>Spend</th>
                        <th>Revenue</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultRows.map((row, idx) => (
                        <tr key={row.variant_id}>
                          <td>{row.variant_id}</td>
                          <td>
                            <input
                              type="number"
                              value={row.impressions}
                              onChange={(e) =>
                                handleResultChange(
                                  idx,
                                  "impressions",
                                  e.target.value
                                )
                              }
                            />
                          </td>
                          <td>
                            <input
                              type="number"
                              value={row.clicks}
                              onChange={(e) =>
                                handleResultChange(
                                  idx,
                                  "clicks",
                                  e.target.value
                                )
                              }
                            />
                          </td>
                          <td>
                            <input
                              type="number"
                              value={row.conversions}
                              onChange={(e) =>
                                handleResultChange(
                                  idx,
                                  "conversions",
                                  e.target.value
                                )
                              }
                            />
                          </td>
                          <td>
                            <input
                              type="number"
                              value={row.spend}
                              onChange={(e) =>
                                handleResultChange(
                                  idx,
                                  "spend",
                                  e.target.value
                                )
                              }
                            />
                          </td>
                          <td>
                            <input
                              type="number"
                              value={row.revenue}
                              onChange={(e) =>
                                handleResultChange(
                                  idx,
                                  "revenue",
                                  e.target.value
                                )
                              }
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="button-row">
                <button type="submit" disabled={loading}>
                  {loading ? "Crunching…" : "Get recommendation"}
                </button>
                <button
                  className="secondary"
                  type="button"
                  onClick={() => setStep(2)}
                  disabled={loading}
                >
                  ← Back to plan
                </button>
              </div>
            </form>

            {recommendation && (
              <div className="section">
                <div className="section-title">Agent recommendation</div>

                {/* Winner Creative Card - Makes agentic loop judge-visible */}
                {(() => {
                  const winnerCreative = creatives.find((c) => c.variant_id === winnerVariantId);
                  const winnerScore = scores.find((s) => s.creative_id === winnerVariantId);

                  return winnerCreative ? (
                    <div style={{
                      background: "linear-gradient(135deg, #667eea10 0%, #764ba210 100%)",
                      border: "2px solid #667eea",
                      borderRadius: "8px",
                      padding: "1rem",
                      marginBottom: "1rem"
                    }}>
                      <h3 style={{ margin: "0 0 0.5rem 0", color: "#667eea" }}>
                        🏆 Winning Variant: {winnerCreative.variant_id}
                      </h3>

                      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "1rem" }}>
                        {/* Winner Image */}
                        <div>
                          {winnerCreative.image_url && (
                            <img
                              src={winnerCreative.image_url}
                              alt={`Winner: Variant ${winnerCreative.variant_id}`}
                              style={{ width: "100%", borderRadius: "4px", border: "2px solid #667eea50" }}
                            />
                          )}
                          <div style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
                            <strong>Copy:</strong> {winnerCreative.hook}
                          </div>
                        </div>

                        {/* FIBO Spec & Scores */}
                        <div>
                          <div style={{ marginBottom: "0.75rem" }}>
                            <strong style={{ color: "#667eea" }}>Key FIBO Parameters:</strong>
                            <ul style={{ marginTop: "0.25rem", paddingLeft: "1.5rem" }}>
                              {winnerCreative.fibo_spec?.shot_type && (
                                <li>Shot type: <code>{winnerCreative.fibo_spec.shot_type}</code></li>
                              )}
                              {winnerCreative.fibo_spec?.lighting_style && (
                                <li>Lighting: <code>{winnerCreative.fibo_spec.lighting_style}</code></li>
                              )}
                              {winnerCreative.fibo_spec?.color_palette && (
                                <li>Color palette: <code>{winnerCreative.fibo_spec.color_palette}</code></li>
                              )}
                              {winnerCreative.fibo_spec?.background_type && (
                                <li>Background: <code>{winnerCreative.fibo_spec.background_type}</code></li>
                              )}
                              {winnerCreative.fibo_spec?.camera_angle && (
                                <li>Camera angle: <code>{winnerCreative.fibo_spec.camera_angle}</code></li>
                              )}
                            </ul>
                          </div>

                          {winnerScore && (
                            <div style={{ marginTop: "0.75rem" }}>
                              <strong style={{ color: "#667eea" }}>Score Breakdown:</strong>
                              <div style={{
                                display: "grid",
                                gridTemplateColumns: "1fr 1fr",
                                gap: "0.5rem",
                                marginTop: "0.5rem",
                                fontSize: "0.9rem"
                              }}>
                                <div>Clarity: <strong>{winnerScore.clarity_of_promise?.toFixed(1)}</strong>/10</div>
                                <div>Emotional: <strong>{winnerScore.emotional_resonance?.toFixed(1)}</strong>/10</div>
                                <div>Credibility: <strong>{winnerScore.proof_and_credibility}</strong>/10</div>
                                <div>CTA Strength: <strong>{winnerScore.call_to_action_score}</strong>/10</div>
                                <div>Curiosity: <strong>{winnerScore.curiosity_hook_factor}</strong>/10</div>
                                <div>Overall: <strong style={{ color: "#667eea" }}>{winnerScore.overall_strength?.toFixed(1)}</strong>/10</div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : null;
                })()}

                <div className="result-summary">
                  <strong>Summary:</strong> {recommendation.summary}
                </div>
                {recommendation.recommended_variants &&
                  recommendation.recommended_variants.length > 0 && (
                    <>
                      <div className="section-subtitle" style={{ marginTop: "0.75rem" }}>
                        Next test variants:
                      </div>
                      <table>
                        <thead>
                          <tr>
                            <th>Variant</th>
                            <th>Role</th>
                            <th>Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {recommendation.recommended_variants.map((v) => (
                            <tr key={v.variant_id}>
                              <td>{v.variant_id}</td>
                              <td>{v.control ? <span className="pill">Control</span> : "Test"}</td>
                              <td>{v.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </>
                  )}

                <div className="button-row" style={{ marginTop: "1rem" }}>
                  <button
                    onClick={handleExport}
                    className="secondary"
                  >
                    📦 Export All Artifacts
                  </button>
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {/* Phase 3.1 Task B: Exploration Grid Popout Panel */}
      {activeExplorationGrid && (
        <div style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          maxHeight: "75vh",
          backgroundColor: "rgba(15, 23, 42, 0.98)",
          borderTop: "2px solid rgba(139, 92, 246, 0.5)",
          boxShadow: "0 -4px 20px rgba(0, 0, 0, 0.5)",
          zIndex: 1000,
          overflow: "auto",
          backdropFilter: "blur(10px)"
        }}>
          <div style={{
            maxWidth: "1600px",
            margin: "0 auto",
            padding: "1.5rem 2rem"
          }}>
            {/* Header with title and close button */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1.5rem",
              paddingBottom: "1rem",
              borderBottom: "1px solid rgba(148, 163, 184, 0.2)"
            }}>
              <div>
                <div style={{
                  fontSize: "1.25rem",
                  fontWeight: "700",
                  color: "#c4b5fd",
                  marginBottom: "0.25rem"
                }}>
                  🔍 Visual Exploration Grid
                </div>
                <div style={{
                  fontSize: "0.9rem",
                  color: "#94a3b8"
                }}>
                  Showing {activeExplorationGrid.variants.length} variants for <strong style={{ color: "#c4b5fd" }}>{activeExplorationGrid.variantName}</strong>
                </div>
              </div>
              <button
                onClick={() => setActiveExplorationGrid(null)}
                style={{
                  background: "rgba(239, 68, 68, 0.2)",
                  border: "1px solid rgba(239, 68, 68, 0.4)",
                  borderRadius: "6px",
                  padding: "0.5rem 1rem",
                  color: "#fca5a5",
                  fontSize: "1rem",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.3)";
                  e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.6)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.2)";
                  e.currentTarget.style.borderColor = "rgba(239, 68, 68, 0.4)";
                }}
              >
                ✕ Close
              </button>
            </div>

            {/* Grid - Always 2 rows x 4 columns */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
              gap: "1.5rem"
            }}>
              {activeExplorationGrid.variants.map((exploredVariant, idx) => (
                <div key={idx} style={{
                  background: "rgba(0, 0, 0, 0.4)",
                  borderRadius: "8px",
                  padding: "1rem",
                  border: "1px solid rgba(148, 163, 184, 0.2)",
                  display: "flex",
                  flexDirection: "column",
                  transition: "all 0.2s"
                }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = "rgba(139, 92, 246, 0.5)";
                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(139, 92, 246, 0.2)";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = "rgba(148, 163, 184, 0.2)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  {exploredVariant.image_url && (
                    <img
                      src={exploredVariant.image_url}
                      alt={`Explored variant ${idx + 1}`}
                      style={{
                        width: "100%",
                        height: "auto",
                        aspectRatio: "1 / 1",
                        objectFit: "cover",
                        borderRadius: "6px",
                        marginBottom: "0.75rem"
                      }}
                    />
                  )}
                  <div style={{
                    fontSize: "0.85rem",
                    color: "#94a3b8",
                    marginBottom: "0.5rem",
                    textAlign: "center",
                    fontWeight: "700"
                  }}>
                    Variant {idx + 1}
                  </div>
                  <div style={{
                    fontSize: "0.75rem",
                    color: "#cbd5e1",
                    lineHeight: "1.6",
                    flex: "1"
                  }}>
                    {exploredVariant.fibo_spec?.lighting_style && (
                      <div style={{ marginBottom: "0.25rem" }}>💡 <strong>Lighting:</strong> {exploredVariant.fibo_spec.lighting_style}</div>
                    )}
                    {exploredVariant.fibo_spec?.color_palette && (
                      <div style={{ marginBottom: "0.25rem" }}>🎨 <strong>Palette:</strong> {exploredVariant.fibo_spec.color_palette}</div>
                    )}
                    {exploredVariant.fibo_spec?.background_type && (
                      <div>🖼️ <strong>Background:</strong> {exploredVariant.fibo_spec.background_type}</div>
                    )}
                  </div>
                  {exploredVariant.fibo_spec && (
                    <details style={{ marginTop: "0.75rem" }}>
                      <summary style={{
                        fontSize: "0.7rem",
                        color: "#93c5fd",
                        cursor: "pointer",
                        textAlign: "center",
                        fontWeight: "600"
                      }}>
                        View Full JSON
                      </summary>
                      <pre style={{
                        fontSize: "0.65rem",
                        color: "#e2e8f0",
                        background: "rgba(0, 0, 0, 0.5)",
                        padding: "0.5rem",
                        borderRadius: "4px",
                        overflow: "auto",
                        maxHeight: "200px",
                        marginTop: "0.5rem",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word"
                      }}>
                        {JSON.stringify(exploredVariant.fibo_spec, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
