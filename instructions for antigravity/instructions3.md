P0 Patch Instructions for Antigravity (Instructions 3)

This guide explains how to update the agentic‑ad‑optimizer project to resolve the outstanding “P0” issues. Follow these steps to clean up the backend, align the API contract, fix documentation, and update the frontend.

1. Clean up backend/app/main.py

Remove the duplicated code blocks at the top of the file. Each endpoint and data class should appear only once.

Fix the process_experiment_results function to fully render the summary string. The summary should read: “Variant <winner.variant_id> was the clear winner with $<winner.profit> profit.  We recommend iterating on its successful elements.”

Consolidate the /regenerate-image endpoint implementation: keep a single function and ensure it returns a CreativeVariant with an image_url, merged fibo_spec, and image_status (one of "fibo", "mocked", or "error").

2. Align the /regenerate-image API contract

The request body should include a full variant (type CreativeVariant), not just a creative_id. This allows the backend to merge the existing fibo_spec with your patch.

A spec_patch (partial FiboImageSpec) may be provided. Only fields present in this patch override the existing spec fields.

Update the endpoint’s docstring accordingly and log a concise message indicating which variant was regenerated and the resulting status.

3. Update the API documentation

In docs/api-contracts.md, replace references to creative_id with variant in the RegenerateRequest. Clarify that spec_patch only contains fields to override (e.g. camera_angle, shot_type, lighting_style, color_palette, background_type, prompt).

Correct the enumeration for image_status to "fibo", "mocked", or "error", and explain what each value means.

4. Fix the README

Under API reference, update the description of the POST /regenerate-image endpoint to match the new request and response. It should indicate that the input takes a variant and a spec_patch, and that the output includes a CreativeVariant with updated image_url, merged fibo_spec, and image_status ("fibo", "mocked", or "error").

5. Update the frontend

In frontend/src/App.jsx, modify the handleRegenerateImage function to send the full CreativeVariant in the variant field. Previously it sent creative_id; this must be replaced with the entire object from your creatives list.

In frontend/src/api.js, update the comment above the regenerateImage helper to document the new request shape: a variant and an optional spec_patch.

6. Applying the patch

A pre‑made patch file (p0_patch.diff) accompanies this guide. To apply it locally, follow these steps inside your project directory:

git checkout main
git pull origin main
git apply /path/to/p0_patch.diff


Alternatively, you can manually edit the files according to the instructions above. After making the changes, commit and push them to your GitHub repository:

git add backend/app/main.py docs/api-contracts.md README.md frontend/src/App.jsx frontend/src/api.js
git commit -m "Fix P0 issues: unify regenerate-image contract, update docs, and cleanup backend"
git push origin main

7. Verify your changes

Run the existing tests (e.g. with pytest) to ensure the backend still imports correctly. Then launch the backend and frontend, and verify that the Regenerate button sends the new request and updates the creative cards as expected.

These instructions should help Google Antigravity (or any collaborator) understand what needs to be done to complete the P0 fixes. The accompanying patch automates most of the changes, but the summary here provides context and manual steps for verification.