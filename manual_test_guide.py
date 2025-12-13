#!/usr/bin/env python3
"""
Manual Testing Guide for Regeneration Flow
Run this script and follow the instructions to manually test the application.
"""

import webbrowser
import time

print("""
╔════════════════════════════════════════════════════════════════════╗
║     AGENTIC AD OPTIMIZER - MANUAL TESTING GUIDE                    ║
║                  Regeneration Flow Verification                    ║
╚════════════════════════════════════════════════════════════════════╝

PREREQUISITES:
✓ Backend running on http://localhost:8000
✓ Frontend running on http://localhost:5173

TESTING STEPS:

┌────────────────────────────────────────────────────────────────────┐
│ STEP 1: Open Application                                          │
└────────────────────────────────────────────────────────────────────┘
Opening http://localhost:5173 in your browser...
""")

time.sleep(2)
webbrowser.open('http://localhost:5173')

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 2: Business Snapshot                                         │
└────────────────────────────────────────────────────────────────────┘
1. Leave all default values in the form:
   - Product name: Math Wars Meta DIY Kit
   - Price: 49
   - Main benefit: Turns math practice into a co-op board game
   - Audience: Parents of 7-12 year olds
   - Pain point: Kids hate math homework

2. Click "Generate experiment plan"

3. VERIFY: You see the experiment plan with 3 variants (A, B, C)

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 3: Generate Creatives                                        │
└────────────────────────────────────────────────────────────────────┘
1. Click "Generate creatives" button

2. Wait for all 3 creative variants to load

3. VERIFY:
   ✓ All variants show an image
   ✓ Status badge shows either "Bria FIBO: LIVE ✅" or "Mock ⚠️"
   ✓ Each variant has preset buttons and "Regenerate image" button

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 4: Test Regeneration - Variant B                            │
└────────────────────────────────────────────────────────────────────┘
1. Scroll to Variant B

2. Click the "Lifestyle" preset button
   → VERIFY: The prompt input field now contains:
     "Lifestyle photography, warm natural lighting, candid moment"

3. Click "Regenerate image"

4. Wait for regeneration to complete

5. VERIFY THE FOLLOWING:
   ✓ UI shows "Working..." indicator during regeneration
   ✓ After completion, TWO thumbnails appear side-by-side:
     - Left: "Previous" with timestamp
     - Right: "Current" with timestamp
   ✓ Status badge still shows "Bria FIBO: LIVE ✅" or "Mock ⚠️"
   ✓ No error messages appear

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 5: Verify API Call (Network Tab)                            │
└────────────────────────────────────────────────────────────────────┘
1. Press F12 to open DevTools

2. Go to the "Network" tab

3. Clear the network log

4. Test regeneration again:
   - Change the prompt or click a different preset
   - Click "Regenerate image"

5. VERIFY IN NETWORK TAB:
   ✓ POST request to /regenerate-image appears
   ✓ Request Status: 200 OK
   ✓ Request Payload contains:
     • "variant": { full variant object with all fields }
     • "spec_patch": { prompt, lighting_style, etc. }
   ✓ Response contains:
     • Updated variant with merged fibo_spec
     • image_url
     • image_status: "fibo", "mocked", or "error"

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 6: Test Custom Prompt                                       │
└────────────────────────────────────────────────────────────────────┘
1. Scroll to Variant C

2. Type a custom prompt in the input field:
   "Vibrant advertisement, high contrast, dramatic lighting, close up"

3. Click "Regenerate image"

4. VERIFY:
   ✓ Regeneration completes successfully
   ✓ Before/after thumbnails appear
   ✓ Network tab shows the custom prompt in spec_patch

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 7: Score Creatives                                          │
└────────────────────────────────────────────────────────────────────┘
1. Click "Score creatives" button

2. VERIFY:
   ✓ Score chips appear under each variant
   ✓ Overall strength score (e.g., "7.3/10")
   ✓ Feedback text appears

Press Enter when ready to continue...
""")
input()

print("""
┌────────────────────────────────────────────────────────────────────┐
│ STEP 8: Complete the Loop                                        │
└────────────────────────────────────────────────────────────────────┘
1. Click "Next: Results & next moves →"

2. Leave default performance data or modify as desired

3. Click "Get recommendation"

4. VERIFY:
   ✓ Success banner appears
   ✓ Recommendation summary shows winning variant
   ✓ Next test variants are suggested

Press Enter when done...
""")
input()

print("""
╔════════════════════════════════════════════════════════════════════╗
║                    TESTING COMPLETE!                               ║
╚════════════════════════════════════════════════════════════════════╝

CHECKLIST - Confirm all items passed:

Frontend Functionality:
□ Business snapshot form submission works
□ Experiment plan generation works
□ Creative variants generation works
□ All images load correctly
□ Status badges display correctly

Regeneration Flow:
□ Preset buttons populate prompt field
□ Custom prompt input works
□ Regenerate button triggers API call
□ Before/after thumbnails appear after regeneration
□ Timestamps display correctly

API Contract:
□ /regenerate-image receives full variant object
□ spec_patch contains explicit fields
□ Response includes merged fibo_spec
□ image_status is set correctly ("fibo", "mocked", or "error")

Error Handling:
□ No console errors during normal operation
□ Error banner shows if something fails
□ Loading indicator appears during async operations

Backend Logging:
□ Check backend terminal for concise log lines:
  "regenerate-image creative_id=<id> status=<status>"

═══════════════════════════════════════════════════════════════════

If all items are checked, the regeneration flow is working correctly! 🎉

To check backend logs, look at the terminal running:
  uvicorn backend.app.main:app --reload --port 8000

You should see one log line per regeneration like:
  regenerate-image creative_id=B status=mocked

═══════════════════════════════════════════════════════════════════
""")
