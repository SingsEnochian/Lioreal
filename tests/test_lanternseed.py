from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from lanternseed import SCHEMA, build_svg, normalise_wonder, wonder_fingerprint  # noqa: E402


class LanternseedTests(unittest.TestCase):
    def test_same_wonder_has_same_constellation(self) -> None:
        wonder = "What becomes possible when curiosity has a room?"
        self.assertEqual(build_svg(wonder), build_svg(wonder))
        self.assertEqual(wonder_fingerprint(wonder), wonder_fingerprint(f"  {wonder}  "))

    def test_different_wonders_have_different_constellations(self) -> None:
        first = build_svg("What does the lantern remember?")
        second = build_svg("What does the river remember?")
        self.assertNotEqual(first, second)

    def test_visual_keeps_the_four_stations_and_evidence_boundary(self) -> None:
        svg = build_svg("Can rigour and wonder walk home together?")
        self.assertIn(SCHEMA, svg)
        for station in ("DREAM", "INSTRUMENT", "OBSERVE", "RETURN"):
            self.assertIn(f">{station}</text>", svg)
        self.assertIn("geometry is not evidence, divination, or canon", svg)
        self.assertIn("prefers-reduced-motion:reduce", svg)

    def test_question_is_xml_escaped(self) -> None:
        svg = build_svg("Could <script>alert('brocrow')</script> become a lantern?")
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)

    def test_empty_wonder_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "needs a wonder"):
            normalise_wonder("   \n ")


if __name__ == "__main__":
    unittest.main()
