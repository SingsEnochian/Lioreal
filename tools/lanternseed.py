#!/usr/bin/env python3
"""Render a wonder as a deterministic, local-first lantern constellation.

Lanternseed does not answer the wonder or assign meaning to the generated
geometry. It gives a question a stable visual address and keeps the four
stations of necessary dreaming visible: Dream, Instrument, Observe, Return.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import random
import textwrap
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "lioreal.lanternseed/v1"
WIDTH = 1200
HEIGHT = 800


@dataclass(frozen=True)
class Station:
    label: str
    invitation: str
    x: int
    y: int
    colour: str


STATIONS = (
    Station("DREAM", "permit the possibility", 180, 185, "#d9b46f"),
    Station("INSTRUMENT", "build one way to look", 1000, 205, "#8dd8c0"),
    Station("OBSERVE", "keep the honest receipt", 985, 645, "#9ea7ff"),
    Station("RETURN", "let evidence change the map", 205, 650, "#df85b4"),
)


def normalise_wonder(wonder: str) -> str:
    """Return a stable human question or reject an empty seed."""
    value = " ".join(str(wonder or "").split())
    if not value:
        raise ValueError("Lanternseed needs a wonder to map.")
    return value


def wonder_fingerprint(wonder: str) -> str:
    """Return the stable SHA-256 identity of a normalised wonder."""
    return hashlib.sha256(normalise_wonder(wonder).encode("utf-8")).hexdigest()


def _question_lines(wonder: str) -> list[str]:
    lines = textwrap.wrap(wonder, width=62, break_long_words=False, break_on_hyphens=False)
    if len(lines) <= 3:
        return lines
    return [*lines[:2], textwrap.shorten(" ".join(lines[2:]), width=62, placeholder="…")]


def _star_field(rng: random.Random, count: int = 58) -> str:
    stars: list[str] = []
    for index in range(count):
        x = rng.uniform(28, WIDTH - 28)
        y = rng.uniform(32, HEIGHT - 32)
        radius = rng.uniform(0.7, 2.2)
        opacity = rng.uniform(0.24, 0.84)
        duration = rng.uniform(4.2, 9.5)
        delay = -rng.uniform(0, duration)
        stars.append(
            f'<circle class="star" cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" '
            f'opacity="{opacity:.2f}" style="--twinkle:{duration:.2f}s;--delay:{delay:.2f}s" '
            f'data-star="{index + 1}" />'
        )
    return "\n    ".join(stars)


def _lantern_constellation(rng: random.Random) -> tuple[str, str]:
    centre_x, centre_y = WIDTH / 2, HEIGHT / 2 + 12
    points: list[tuple[float, float, float]] = []
    phase = rng.uniform(0, math.tau)
    for index in range(9):
        angle = phase + (math.tau * index / 9) + rng.uniform(-0.16, 0.16)
        radius_x = rng.uniform(145, 300)
        radius_y = rng.uniform(90, 215)
        points.append(
            (
                centre_x + math.cos(angle) * radius_x,
                centre_y + math.sin(angle) * radius_y,
                angle,
            )
        )
    points.sort(key=lambda item: item[2])
    route = " ".join(
        [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
        + [f"L {x:.2f} {y:.2f}" for x, y, _ in points[1:]]
        + ["Z"]
    )
    nodes = []
    for index, (x, y, _) in enumerate(points, start=1):
        size = rng.uniform(5.5, 9.5)
        nodes.append(
            f'<g class="lantern-node" transform="translate({x:.2f} {y:.2f})" data-lantern="{index}">'
            f'<path d="M 0 {-size:.2f} L {size * .72:.2f} 0 L 0 {size:.2f} '
            f'L {-size * .72:.2f} 0 Z" /></g>'
        )
    return route, "\n    ".join(nodes)


def build_svg(wonder: str) -> str:
    """Build a deterministic, self-contained SVG for *wonder*."""
    question = normalise_wonder(wonder)
    fingerprint = wonder_fingerprint(question)
    rng = random.Random(int(fingerprint, 16))
    route, lanterns = _lantern_constellation(rng)
    stars = _star_field(rng)
    escaped_question = html.escape(question)
    metadata = html.escape(
        json.dumps(
            {
                "schema": SCHEMA,
                "wonder": question,
                "fingerprint": fingerprint,
                "claim": "Deterministic visual invitation; geometry is not evidence, divination, or canon.",
                "stations": [station.label.lower() for station in STATIONS],
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        quote=False,
    )
    question_markup = "".join(
        f'<tspan x="600" dy="{0 if index == 0 else 31}">{html.escape(line)}</tspan>'
        for index, line in enumerate(_question_lines(question))
    )
    station_markup = "\n    ".join(
        f'''<g class="station" transform="translate({station.x} {station.y})">
      <circle r="42" fill="{station.colour}" fill-opacity=".08" stroke="{station.colour}" />
      <circle r="7" fill="{station.colour}" />
      <text class="station-label" y="67" fill="{station.colour}">{station.label}</text>
      <text class="station-invitation" y="90">{html.escape(station.invitation)}</text>
    </g>'''
        for station in STATIONS
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
     role="img" aria-labelledby="lanternseed-title lanternseed-description">
  <title id="lanternseed-title">Lanternseed constellation for: {escaped_question}</title>
  <desc id="lanternseed-description">A deterministic visual invitation connecting Dream, Instrument, Observe, and Return. The geometry makes no evidentiary claim.</desc>
  <metadata>{metadata}</metadata>
  <defs>
    <radialGradient id="night" cx="50%" cy="45%" r="72%">
      <stop offset="0" stop-color="#251f43" />
      <stop offset=".52" stop-color="#101426" />
      <stop offset="1" stop-color="#070a12" />
    </radialGradient>
    <radialGradient id="lantern-glow">
      <stop offset="0" stop-color="#fff1b8" stop-opacity=".92" />
      <stop offset=".35" stop-color="#d9b46f" stop-opacity=".44" />
      <stop offset="1" stop-color="#d9b46f" stop-opacity="0" />
    </radialGradient>
    <filter id="soft-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
    </filter>
    <style>
      .star{{fill:#f5f0ff;transform-box:fill-box;transform-origin:center;animation:twinkle var(--twinkle) ease-in-out var(--delay) infinite}}
      .constellation-route{{fill:none;stroke:#8dd8c0;stroke-width:1.2;stroke-opacity:.28;stroke-dasharray:3 9}}
      .lantern-node path{{fill:#d9b46f;stroke:#fff1b8;stroke-width:.8;filter:url(#soft-glow)}}
      .station circle:first-child{{stroke-width:1.2;stroke-dasharray:2 7}}
      .station-label{{font:600 15px ui-sans-serif,system-ui,sans-serif;text-anchor:middle;letter-spacing:.2em}}
      .station-invitation{{fill:#c9c9d8;font:13px ui-serif,Georgia,serif;text-anchor:middle}}
      .wonder-label{{fill:#8dd8c0;font:600 12px ui-sans-serif,system-ui,sans-serif;text-anchor:middle;letter-spacing:.28em}}
      .wonder{{fill:#fff8df;font:25px ui-serif,Georgia,serif;text-anchor:middle}}
      .fingerprint{{fill:#8b8ca5;font:11px ui-monospace,SFMono-Regular,monospace;text-anchor:middle}}
      @keyframes twinkle{{0%,100%{{transform:scale(.72);opacity:.28}}50%{{transform:scale(1.18);opacity:.9}}}}
      @media (prefers-reduced-motion:reduce){{.star{{animation:none}}}}
    </style>
  </defs>
  <rect width="1200" height="800" fill="url(#night)" />
  <g aria-hidden="true">
    {stars}
    <path class="constellation-route" d="{route}" />
    <circle cx="600" cy="412" r="78" fill="url(#lantern-glow)" opacity=".72" />
    {lanterns}
  </g>
  <g>
    {station_markup}
  </g>
  <g transform="translate(0 350)">
    <text class="wonder-label" x="600" y="0">LANTERNSEED</text>
    <text class="wonder" x="600" y="39">{question_markup}</text>
    <text class="fingerprint" x="600" y="143">wonder sha256 · {fingerprint[:16]}</text>
  </g>
</svg>
'''


def write_svg(wonder: str, output: Path) -> tuple[Path, str]:
    """Write a Lanternseed SVG and return its path and wonder fingerprint."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_svg(wonder), encoding="utf-8")
    return output, wonder_fingerprint(wonder)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wonder", help="The question or possibility to give a stable visual address.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lanternseed/latest.svg"),
        help="SVG destination (default: artifacts/lanternseed/latest.svg).",
    )
    args = parser.parse_args()
    try:
        output, fingerprint = write_svg(args.wonder, args.output)
    except ValueError as error:
        parser.error(str(error))
    print(f"Lanternseed {fingerprint[:16]} written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
