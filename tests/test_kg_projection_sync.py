#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sync_kg_projection",
    ROOT / "scripts/sync_kg_projection.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def snapshot(commit: str = "a" * 40) -> dict:
    return {
        "schema_version": 1,
        "source": {
            "repository": "eduarddeboer/eduarddeboer-kg",
            "commit": commit,
            "production_base": "https://data.eduarddeboer.com/",
        },
        "entities": {
            "person/eduard_de_boer": {
                "id": "person/eduard_de_boer",
                "type": "Person",
                "name": {"nl": "Eduard de Boer", "en": "Eduard de Boer"},
                "relations": [],
            }
        },
        "relations": [],
        "media": {},
    }


def sections(commit: str = "a" * 40) -> dict:
    return {
        "schema_version": 1,
        "source_commit": commit,
        "sections": {
            "home": {
                "schema": {
                    "page_type": "ProfilePage",
                    "main_entity": "person/eduard_de_boer",
                },
                "groups": [
                    {
                        "entities": ["person/eduard_de_boer"],
                    }
                ],
            }
        },
    }


def manifest(commit: str) -> dict:
    return {
        "commit_sha": commit,
        "production_host": "data.eduarddeboer.com",
    }


class ProjectionSyncTests(unittest.TestCase):
    def test_commit_only_change_is_not_semantic_drift(self) -> None:
        current = snapshot("a" * 40)
        candidate = snapshot("b" * 40)

        result = MODULE.sync_projection(
            candidate=candidate,
            release_manifest=manifest("b" * 40),
            current=current,
            sections=sections("a" * 40),
            apply=False,
        )

        self.assertFalse(result["changed"])
        self.assertEqual(
            result["current_semantic_sha256"],
            result["candidate_semantic_sha256"],
        )

    def test_semantic_change_updates_snapshot_and_section_commit(self) -> None:
        current = snapshot("a" * 40)
        candidate = snapshot("b" * 40)
        candidate["entities"]["person/eduard_de_boer"]["description"] = {
            "nl": "Nieuwe beschrijving",
            "en": "New description",
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_path = root / "snapshot.json"
            sections_path = root / "sections.json"

            result = MODULE.sync_projection(
                candidate=candidate,
                release_manifest=manifest("b" * 40),
                current=current,
                sections=sections("a" * 40),
                apply=True,
                snapshot_path=snapshot_path,
                sections_path=sections_path,
            )

            self.assertTrue(result["changed"])
            written_snapshot = __import__("json").loads(
                snapshot_path.read_text(encoding="utf-8")
            )
            written_sections = __import__("json").loads(
                sections_path.read_text(encoding="utf-8")
            )
            self.assertEqual(written_snapshot["source"]["commit"], "b" * 40)
            self.assertEqual(written_sections["source_commit"], "b" * 40)

    def test_release_manifest_must_match_snapshot_commit(self) -> None:
        with self.assertRaisesRegex(
            MODULE.SnapshotSyncError,
            "do not pin the same KG commit",
        ):
            MODULE.sync_projection(
                candidate=snapshot("b" * 40),
                release_manifest=manifest("c" * 40),
                current=snapshot("a" * 40),
                sections=sections(),
                apply=False,
            )

    def test_projection_must_remain_closed(self) -> None:
        candidate = snapshot("b" * 40)
        candidate["entities"]["person/eduard_de_boer"]["relations"] = [
            {"predicate": "knowsAbout", "target": "organization/missing"}
        ]
        candidate["relations"] = [
            {
                "subject": "person/eduard_de_boer",
                "predicate": "knowsAbout",
                "target": "organization/missing",
            }
        ]
        with self.assertRaisesRegex(MODULE.SnapshotSyncError, "non-closed relation"):
            MODULE.validate_snapshot(candidate)

    def test_section_reference_cannot_disappear(self) -> None:
        current = snapshot("a" * 40)
        candidate = snapshot("b" * 40)
        candidate["entities"]["person/eduard_de_boer"]["description"] = {
            "nl": "Changed",
            "en": "Changed",
        }
        bad_sections = copy.deepcopy(sections())
        bad_sections["sections"]["home"]["groups"][0]["entities"].append(
            "organization/not_projected"
        )

        with self.assertRaisesRegex(
            MODULE.SnapshotSyncError,
            "break section references",
        ):
            MODULE.sync_projection(
                candidate=candidate,
                release_manifest=manifest("b" * 40),
                current=current,
                sections=bad_sections,
                apply=False,
            )


class LocalRunnerWorkflowTests(unittest.TestCase):
    def test_validate_workflow_avoids_setup_python_on_local_macos(self) -> None:
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("Reuse local Python 3.12", workflow)
        self.assertIn("/opt/homebrew/bin/python3.12", workflow)
        self.assertIn("needs.choose-runner.outputs.target != 'local'", workflow)
        self.assertIn("uses: actions/setup-python@v6", workflow)
        self.assertIn("Reuse local Hugo Extended 0.167.0", workflow)
        self.assertIn("/Users/kg-runner/actions_hugo/bin/hugo", workflow)
        self.assertIn("rm -rf /Users/kg-runner/actions_hugo/_temp/pkg", workflow)
        self.assertIn("Bootstrap Hugo Extended on local Mac", workflow)
        self.assertIn("Hugo Extended on GitHub-hosted fallback", workflow)

    def test_projection_sync_avoids_setup_python_on_local_macos(self) -> None:
        workflow = (ROOT / ".github/workflows/kg-projection-sync.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("Reuse local Python 3.12", workflow)
        self.assertIn("/opt/homebrew/bin/python3.12", workflow)
        self.assertIn("needs.choose-runner.outputs.target != 'local'", workflow)

if __name__ == "__main__":
    unittest.main()
