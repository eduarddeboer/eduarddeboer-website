#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.entity_review import build_public_payload, render_markdown, sanitize_document


class EntityReviewTests(unittest.TestCase):
    def test_sanitized_review_omits_private_resolver_ids(self) -> None:
        raw = {
            "source_id": "website/content/nl/insights/example/index.md",
            "known_mentions": [
                {
                    "entity_id": "organization/private_internal_node",
                    "entity_type": "Organization",
                    "aliases": ["Example Timber"],
                    "occurrences": 2,
                    "already_linked": False,
                    "suggested_predicate": "mentions",
                }
            ],
            "unlinked_known_mentions": [
                {
                    "entity_id": "organization/private_internal_node",
                    "entity_type": "Organization",
                    "aliases": ["Example Timber"],
                    "occurrences": 2,
                    "already_linked": False,
                    "suggested_predicate": "mentions",
                }
            ],
            "unknown_candidates": ["Another Candidate"],
            "declared_entity_links": ["legislation/eudr_2023_1115"],
            "unknown_declared_entity_links": [],
        }

        public = sanitize_document(raw)
        encoded = json.dumps(public, ensure_ascii=False)

        self.assertNotIn("private_internal_node", encoded)
        self.assertNotIn("entity_id", encoded)
        self.assertIn("Example Timber", encoded)
        self.assertIn("Another Candidate", encoded)
        self.assertIn("legislation/eudr_2023_1115", encoded)

    def test_summary_contains_only_public_safe_review_material(self) -> None:
        document = {
            "source_id": "website/content/nl/insights/example/index.md",
            "known_mentions": 1,
            "already_linked_known_mentions": 0,
            "unlinked_known_mentions": [
                {
                    "aliases": ["EUDR"],
                    "occurrences": 3,
                    "suggested_predicate": "mentions",
                }
            ],
            "unknown_candidates": ["Example Company"],
            "declared_entity_links": [],
            "unknown_declared_entity_links": [],
        }
        payload = build_public_payload(
            [document],
            website_commit="a" * 40,
            kg_commit="b" * 40,
        )
        markdown = render_markdown(payload)

        self.assertIn("EUDR", markdown)
        self.assertIn("Example Company", markdown)
        self.assertEqual(payload["summary"]["unlinked_known_mentions"], 1)
        self.assertEqual(payload["summary"]["unknown_candidates"], 1)

    def test_entity_review_workflow_enforces_private_kg_boundary(self) -> None:
        workflow = (ROOT / ".github/workflows/entity-review.yml").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("pull_request_target", workflow)
        self.assertIn(
            "github.event.pull_request.head.repo.full_name != github.repository",
            workflow,
        )
        self.assertIn(
            "github.event.pull_request.head.repo.full_name == github.repository",
            workflow,
        )
        self.assertIn("repository: eduarddeboer/eduarddeboer-kg", workflow)
        self.assertIn("Detect private KG credential", workflow)
        self.assertIn("token: ${{ secrets.KG_READ_TOKEN }}", workflow)
        self.assertNotIn("secrets.KG_READ_TOKEN || secrets.RUNNER_ROUTER_TOKEN", workflow)
        self.assertGreaterEqual(workflow.count("persist-credentials: false"), 2)
        self.assertIn("website-entity-review-", workflow)
        self.assertNotIn("entity-review-raw", workflow)
        self.assertIn("Choose preferred runner", workflow)
        self.assertIn("fromJSON(needs.choose-runner.outputs.runs_on)", workflow)
        self.assertIn("Reuse persistent Python 3.12 environment on local Mac", workflow)
        self.assertIn("/opt/homebrew/bin/python3.12", workflow)
        self.assertIn("/Users/kg-runner/.cache/eduard-website-ci", workflow)
        self.assertIn("needs.choose-runner.outputs.target != 'local'", workflow)


if __name__ == "__main__":
    unittest.main()
