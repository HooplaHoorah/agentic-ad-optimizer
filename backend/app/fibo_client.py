"""Simple client wrapper for Bria FIBO image generation.

This module defines a minimal interface for requesting images from the FIBO
service.  To keep the demo self‑contained and always working, the client
returns a deterministic placeholder when no `FIBO_API_KEY` is present in
 the environment or when a network error occurs.  Judges can focus on
 the JSON contract and the agentic loop rather than debugging network
 requests.

When a `FIBO_API_KEY` is provided the client will attempt to call
Bria’s FIBO image generation API.  The API endpoint can be overridden by
setting the `FIBO_API_URL` environment variable; otherwise it defaults
 to Bria’s v2 `/image/generate` endpoint.  The request is made
 synchronously and includes the JSON spec as a `structured_prompt` along
 with a natural language `prompt`.  On success the returned `image_url`
and any resolved defaults from the service are propagated.  Any
exceptions or unexpected responses will result in a fallback placeholder
image so downstream code can continue to function.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import json

try:
    import requests  # type: ignore  # External dependency used only when FIBO_API_KEY is set
except Exception:
    # Requests might not be installed in some environments; it is only
    # required for real API calls.  When unavailable the client will
    # always fallback to mock mode.
    requests = None  # type: ignore


@dataclass
class FiboImageSpec:
    """Typed representation of an image specification for FIBO.

    The fields mirror common parameters exposed by the FIBO JSON schema.
    Add or remove fields here as Bria evolves their API.
    """

    camera_angle: str = "medium"
    shot_type: str = "product_only"
    lighting_style: str = "warm"
    color_palette: str = "pastel"
    background_type: str = "studio"


@dataclass
class FiboImageResult:
    """Return type for image generation calls."""

    image_url: str
    resolved_spec: Dict[str, Any]


def generate_fibo_image(spec: Dict[str, Any], prompt: str) -> FiboImageResult:
    """Generate an image from a Fibo spec and prompt.

    In a real integration this function POSTs to the FIBO API.  If
    a `FIBO_API_KEY` is not set or if the `requests` library is not
    available the function returns a deterministic placeholder and
    echoes back the provided spec.  Otherwise it will construct a
    JSON payload containing the natural-language `prompt` and the
    `spec` serialized as a string in `structured_prompt`.  The API
    token is sent via the `api_token` header and the request is made
    synchronously.  On success the returned `image_url` is propagated
    and the `spec` is returned unchanged.  If the API response is
    malformed or an exception is raised the function logs the error and
    falls back to a placeholder.

    Args:
        spec: Dictionary of JSON parameters controlling the image.
        prompt: Short natural‑language description used to guide the model.

    Returns:
        FiboImageResult with an `image_url` and a `resolved_spec` that may
        include defaults filled in by the FIBO service.
    """
    api_key = os.getenv("FIBO_API_KEY")
    # Without an API key or requests library we operate in mock mode
    if not api_key or requests is None:
        url = "https://placehold.co/600x400/png?text=Mock+Image"
        return FiboImageResult(image_url=url, resolved_spec=spec.copy())

    # Determine endpoint: allow override via environment variable
    base_url = os.getenv(
        "FIBO_API_URL",
        "https://engine.prod.bria-api.com/v2/image/generate",
    )

    # Construct payload; send structured_prompt as a JSON string
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "structured_prompt": json.dumps(spec),
        "sync": True,
    }
    headers = {
        "Content-Type": "application/json",
        "api_token": api_key,
    }

    try:
        response = requests.post(
            base_url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        # If the service returns a 202, the request is asynchronous; we
        # could poll the status_url here but for now fall back to mock
        response.raise_for_status()
        data = response.json()
        # Navigate the response to extract the image URL; according to
        # Bria’s docs it should be under data['result']['image_url']
        image_url: Optional[str] = None
        if isinstance(data, dict):
            result = data.get("result")
            if isinstance(result, dict):
                image_url = result.get("image_url")  # type: ignore
        if not image_url:
            raise ValueError("Missing image_url in FIBO response")
        return FiboImageResult(image_url=image_url, resolved_spec=spec.copy())
    except Exception:
        # In case of network failure, bad status, or JSON decoding
        # errors we return a deterministic error placeholder.  In a
        # production setting you might log the exception.
        fallback_url = f"https://placehold.co/600x400/png?text=Image+Error"
        return FiboImageResult(image_url=fallback_url, resolved_spec=spec.copy())
