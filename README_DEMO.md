# Quick Start Guide - Agentic Ad Optimizer Demo

## Current Status: ✅ READY FOR DEMO

Both servers are running and properly configured:
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173

## What Was Fixed

### Port Alignment ✅
- Backend running on port **8000**
- Frontend configured to connect to **http://localhost:8000**
- No more misalignment issues

### Code Fixes ✅
1. **Backend (`main.py`):** Removed duplicate code (185 lines)
2. **Frontend (`App.jsx`):** Fixed function scoping and API payload structure

### API Contract ✅
The `/regenerate-image` endpoint now correctly:
- Receives full `variant` object + `spec_patch`
- Merges existing spec with patch
- Returns updated variant with merged `fibo_spec`
- Sets `image_status` to "fibo", "mocked", or "error"
- Logs concisely: `regenerate-image creative_id=X status=Y`

## Demo the Regeneration Flow

### Quick Test (5 minutes)

1. **Open the app:** http://localhost:5173

2. **Generate creatives:**
   - Leave default values in business snapshot
   - Click "Generate experiment plan"
   - Click "Generate creatives"
   - Wait for images to load

3. **Test regeneration:**
   - Scroll to Variant B
   - Click "Lifestyle" preset button
   - Click "Regenerate image"
   - **Observe:** Before/after thumbnails appear with timestamps

4. **Verify API call:**
   - Press F12 → Network tab
   - Regenerate again
   - Check `/regenerate-image` request/response payload

### Detailed Test (15 minutes)

Run the interactive guide:
```bash
python manual_test_guide.py
```

This will walk you through every step with verification checkpoints.

## Key Features to Demo

### 1. Status Badges
- **"Bria FIBO: LIVE ✅"** - Real FIBO API (when FIBO_API_KEY is set)
- **"Mock ⚠️"** - Mock mode (when FIBO_API_KEY is not set)

### 2. Preset Buttons
Quick-apply common image styles:
- **Product Shot:** Professional product photography
- **Lifestyle:** Warm natural lighting
- **Punchy Ad:** Vibrant, dramatic lighting

### 3. Regeneration History
After clicking "Regenerate image":
- Left thumbnail: Previous version with timestamp
- Right thumbnail: Current version with timestamp
- Both displayed side-by-side for easy comparison

### 4. Custom Prompts
Type any custom prompt to fine-tune image generation:
- "Studio photography, soft lighting"
- "Outdoor scene, natural sunlight"
- "Vibrant colors, high contrast"

## Network Tab Evidence

When you regenerate an image, check the Network tab for:

**Request Payload:**
```json
{
  "variant": {
    "variant_id": "B",
    "hook": "...",
    "primary_text": "...",
    "headline": "...",
    "fibo_spec": { ... },
    // ... all other fields
  },
  "spec_patch": {
    "prompt": "Lifestyle photography, warm natural lighting",
    "background_type": "lifestyle",
    "lighting_style": "warm"
  }
}
```

**Response:**
```json
{
  "variant_id": "B",
  "image_url": "https://...",
  "fibo_spec": {
    // Merged base spec + patch
    "lighting_style": "warm",
    "background_type": "lifestyle",
    // ... other fields
  },
  "image_status": "mocked"  // or "fibo" or "error"
}
```

## Backend Logs

Check the backend terminal for concise logs:
```
regenerate-image creative_id=B status=mocked
regenerate-image creative_id=C status=mocked
```

No secrets, just clean status logging.

## Verification Checklist

After testing, confirm:

- [ ] All creative variants load with images
- [ ] Status badges display correctly
- [ ] Preset buttons populate prompt field
- [ ] "Regenerate image" button works
- [ ] Before/after thumbnails appear
- [ ] Timestamps display correctly
- [ ] Network tab shows correct request/response
- [ ] Backend logs show concise regeneration lines
- [ ] No console errors
- [ ] Error handling works (try regenerating when backend is stopped)

## Files for Reference

| File | Description |
|------|-------------|
| `IMPLEMENTATION_SUMMARY.md` | Executive summary of all changes |
| `REGENERATION_DEMO_REPORT.md` | Detailed technical documentation |
| `test_regeneration.py` | Automated API test |
| `manual_test_guide.py` | Interactive testing script |
| `README_DEMO.md` | This file |

## Troubleshooting

### Backend not responding
```bash
# Restart backend
cd c:\dev\agentic-ad-optimizer
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend not loading
```bash
# Restart frontend
cd c:\dev\agentic-ad-optimizer\frontend
npm run dev
```

### Port conflict
Make sure nothing else is using port 8000 or 5173:
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

## Next Steps

Once you've verified the regeneration flow works:

1. **Capture screenshots** of before/after thumbnails
2. **Record network traffic** showing correct API contract
3. **Document backend logs** showing concise output
4. **Take browser console screenshot** showing no errors

This evidence pack proves the regeneration flow is working as specified! 🎉

---

**Last Updated:** December 12, 2025
**Status:** ✅ All systems operational
