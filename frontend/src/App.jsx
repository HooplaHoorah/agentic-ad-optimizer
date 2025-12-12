import React, { useState, useEffect } from "react";
import {
  createExperimentPlan,
  generateCreatives,
  scoreCreatives,
  regenerateImage,
  submitResults,
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
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to create experiment plan.");
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
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to generate creatives.");
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
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to score creatives.");
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
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to process results.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreForVariant = (variantId) => {
    if (!scores || !scores.length) return null;
    return scores.find((s) => s.creative_id === variantId);
  };

  const handleStartOver = () => {

    /**
 * Handle updates to the prompt override for a given creative.
 * @param {string} variantId - The variant ID for which to update the draft prompt.
 * @param {string} value - The new prompt value.
 */
    const handlePatchChange = (variantId, value) => {
      setPatchPrompts((prev) => ({ ...prev, [variantId]: value }));
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
        const specPatch = {};
        if (patchPrompts[variantId]) {
          specPatch.prompt = patchPrompts[variantId];
        }
        const body = {
          creative_id: variantId,
          spec_patch: specPatch,
        };
        const updatedCreative = await regenerateImage(body);
        setCreatives((prev) =>
          prev.map((c) =>
            c.variant_id === updatedCreative.variant_id ? updatedCreative : c
          )
        );
      } catch (err) {
        console.error(err);
        setError(err.message || "Failed to regenerate image.");
      } finally {
        setLoading(false);
      }
    };
    setStep(1);
    setSnapshot(null);
    setPlan(null);
    setCreatives([]);
    setScores([]);
    setRecommendation(null);
    setError("");
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

        {error && !loading && <div className="error-banner">⚠️ {error}</div>}
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
                            <img
                              src={c.image_url}
                              alt="Creative image"
                              style={{ width: "100%", borderRadius: "4px" }}
                            />
                          </div>
                        )}
                        {c.image_status && c.image_status !== "SUCCEEDED" && (
                          <div className="image-status" style={{ marginTop: "0.25rem", color: "#555" }}>
                            Image status: {c.image_status}
                          </div>
                        )}
                        <div className="creative-body">
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
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
