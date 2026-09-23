#!/usr/bin/env python3
"""
render_slides.py
Render slide HTML templates to high-resolution PNG images using Playwright.
Run: .venv/bin/python render_slides.py
"""

import asyncio
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
RENDERS_DIR = BASE_DIR / "slide_renders"
OUTPUT_DIR = BASE_DIR / "slide_renders" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Slide configurations
SLIDES = [
    # ── Full slides (for reference / fallback) ──────────────────────────────
    {
        "name": "slide5_airflow_task",
        "html": RENDERS_DIR / "slide5_airflow_task.html",
        "output": OUTPUT_DIR / "slide5_airflow.png",
        "viewport": {"width": 2560, "height": 1350},
        "wait_for": ".mermaid svg",
        "wait_ms": 2500,
        "has_mermaid": True,
    },
    {
        "name": "slide6_dagster_task",
        "html": RENDERS_DIR / "slide6_dagster_task.html",
        "output": OUTPUT_DIR / "slide6_dagster.png",
        "viewport": {"width": 2560, "height": 1350},
        "wait_for": ".mermaid svg",
        "wait_ms": 2500,
        "has_mermaid": True,
    },
    {
        "name": "slide7_infrastructure",
        "html": RENDERS_DIR / "slide7_infrastructure.html",
        "output": OUTPUT_DIR / "slide7_infra.png",
        "viewport": {"width": 2560, "height": 1440},
        "wait_for": "body",
        "wait_ms": 800,
        "has_mermaid": False,
    },
    # ── Mermaid-only crops (navy bg, for PPTX Hybrid embedding) ─────────────
    {
        "name": "slide5_mermaid_only",
        "html": RENDERS_DIR / "slide5_mermaid_only.html",
        "output": OUTPUT_DIR / "slide5_mermaid.png",
        "viewport": {"width": 1480, "height": 1120},
        "wait_for": ".mermaid svg",
        "wait_ms": 3000,                    # Extra wait for Mermaid to render completely
        "has_mermaid": True,
    },
    {
        "name": "slide6_mermaid_only",
        "html": RENDERS_DIR / "slide6_mermaid_only.html",
        "output": OUTPUT_DIR / "slide6_mermaid.png",
        "viewport": {"width": 1480, "height": 1120},
        "wait_for": ".mermaid svg",
        "wait_ms": 3000,
        "has_mermaid": True,
    },
]


async def render_slide(browser, slide: dict) -> None:
    """Render a single slide to PNG."""
    print(f"  ▶ Rendering {slide['name']}...", end="", flush=True)

    page = await browser.new_page(
        viewport=slide["viewport"],
        device_scale_factor=1,  # 1x since we're already at 2560px
    )

    # Navigate to local file
    file_url = slide["html"].as_uri()
    await page.goto(file_url, wait_until="networkidle", timeout=30000)

    # Wait for the key element (Mermaid SVG or body)
    try:
        await page.wait_for_selector(slide["wait_for"], timeout=15000)
    except Exception as e:
        print(f"\n  ⚠️  wait_for_selector timed out: {e}")

    # If has Mermaid, wait for ALL SVGs to be rendered
    if slide["has_mermaid"]:
        # Wait until Mermaid has finished processing all .mermaid divs
        try:
            await page.wait_for_function(
                """() => {
                    const divs = document.querySelectorAll('.mermaid');
                    if (divs.length === 0) return false;
                    for (const div of divs) {
                        if (!div.querySelector('svg')) return false;
                    }
                    return true;
                }""",
                timeout=15000,
            )
        except Exception as e:
            print(f"\n  ⚠️  Mermaid SVG check timed out: {e}")

    # Additional wait for fonts, transitions, etc.
    await asyncio.sleep(slide["wait_ms"] / 1000)

    # Take screenshot
    await page.screenshot(
        path=str(slide["output"]),
        type="png",
        full_page=False,
        clip={"x": 0, "y": 0, "width": slide["viewport"]["width"], "height": slide["viewport"]["height"]},
    )

    await page.close()
    size_kb = slide["output"].stat().st_size // 1024
    print(f" ✅ {slide['output'].name} ({size_kb} KB)")


async def main():
    print("=" * 60)
    print("  Slide Renderer (Playwright + Chromium)")
    print("=" * 60)

    # Check HTML files exist
    missing = [s["name"] for s in SLIDES if not s["html"].exists()]
    if missing:
        print(f"❌ Missing HTML files: {missing}")
        sys.exit(1)

    # Launch browser
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--force-device-scale-factor=1",
                "--high-dpi-support=1",
            ],
        )

        print(f"\n🚀 Rendering {len(SLIDES)} slides to: {OUTPUT_DIR}\n")

        for slide in SLIDES:
            try:
                await render_slide(browser, slide)
            except Exception as e:
                print(f"\n  ❌ Error rendering {slide['name']}: {e}")

        await browser.close()

    print(f"\n✅ Done! Output images in: {OUTPUT_DIR}")
    print("\nFiles created:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  📸 {f.name} ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    asyncio.run(main())
