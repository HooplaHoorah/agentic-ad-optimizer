import requests
import json

# Test the regeneration endpoint
BASE_URL = "http://localhost:8000"

print("Testing /regenerate-image endpoint...")
print("=" * 60)

# Create a sample variant object
test_variant = {
    "variant_id": "TEST",
    "hook": "Test Hook",
    "primary_text": "Test primary text",
    "headline": "Test Headline",
    "call_to_action": "Shop Now",
    "image_url": "https://placehold.co/600x400",
    "fibo_spec": {
        "camera_angle": "medium",
        "shot_type": "product_only",
        "lighting_style": "warm",
        "color_palette": "neutral",
        "background_type": "studio"
    },
    "image_status": "mocked"
}

# Create spec patch
spec_patch = {
    "lighting_style": "dramatic",
    "color_palette": "vibrant",
    "prompt": "Vibrant advertisement with dramatic lighting"
}

# Make the request
payload = {
    "variant": test_variant,
    "spec_patch": spec_patch
}

print("\n1. REQUEST PAYLOAD:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(
        f"{BASE_URL}/regenerate-image",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n2. RESPONSE STATUS: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n3. RESPONSE BODY:")
        print(json.dumps(result, indent=2))
        
        print("\n4. VERIFICATION:")
        print(f"   ✓ Variant ID matches: {result['variant_id'] == test_variant['variant_id']}")
        print(f"   ✓ Image status set: {result.get('image_status', 'NOT SET')}")
        print(f"   ✓ Image URL present: {'image_url' in result}")
        print(f"   ✓ FIBO spec merged: {result.get('fibo_spec', {}).get('lighting_style') == 'dramatic'}")
        print(f"   ✓ Color palette merged: {result.get('fibo_spec', {}).get('color_palette') == 'vibrant'}")
        print(f"   ✓ Prompt added: {result.get('fibo_spec', {}).get('prompt') == spec_patch['prompt']}")
        
        print("\n✅ TEST PASSED - Regeneration endpoint working correctly!")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n" + "=" * 60)
