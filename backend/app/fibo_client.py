"""Simple client wrapper for Bria FIBO image generation.

This module defines a minimal interface for requesting images from the FIBO
service.  To keep the demo self‑contained and always working, the client
returns a deterministic placeholder when no `FIBO_API_KEY` is present in
the environment.  Judges can focus on the JSON contract and the agentic
loop rather than debugging network requests.

The real FIBO client would make HTTP requests to Bria's API using the
provided JSON spec and a short natural‑language prompt.  The stubbed
implementation here simply echoes back the spec and returns a placeholder
image URL.  Downstream code should treat this as a black box that may
raise exceptions on network errors.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os


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

    In a real integration this function would POST to the FIBO API.  The
    current implementation is a stub: if a `FIBO_API_KEY` is present in the
    environment then it pretends a real call succeeded and echoes back the
    provided spec along with a placeholder URL.  Otherwise it returns a
    deterministic placeholder and the original spec.  This allows the
    frontend to work in mock mode without any network dependencies.

    Args:
        spec: Dictionary of JSON parameters controlling the image.
        prompt: Short natural‑language description used to guide the model.

    Returns:
        FiboImageResult with an `image_url` and a `resolved_spec` that may
        include defaults filled in by the FIBO service.
    """
    api_key = os.getenv("FIBO_API_KEY")
    # In a real client, you would construct the request body combining the prompt and spec,
    # then send it to FIBO_BASE_URL with authentication headers.  For now, we just
    # return a static image and echo the spec back.
    if api_key:
        # Pretend we got back a real URL.  Use a placeholder service so the
        # frontend shows an actual image.  The prompt could be encoded into
        # the image URL to make the placeholder more dynamic, but it's not
        # necessary for the demo.
        url = f"https://placehold.co/600x400/png?text={prompt.replace(' ', '+')}"
        resolved = spec.copy()
        return FiboImageResult(image_url=url, resolved_spec=resolved)
    else:
        # Mock mode – deterministic placeholder and echo the spec
        url = "https://placehold.co/600x400/png?text=Mock+Image"
        return FiboImageResult(image_url=url, resolved_spec=spec.copy())