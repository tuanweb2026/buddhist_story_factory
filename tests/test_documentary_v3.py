"""
Unit and integration tests for Long-Form Documentary Engine V3.
Verifies:
- ViewerEditorialAgent: Central Question, Viewer Promise, ViewerValueScore, Curiosity Gaps, LF-EDITORIAL-01
- LongFormScriptGenerationAgent: V3 metadata, claims, proof levels, transitions
- LongFormVisualStorytellingAgent: proof_level mapping, dynamic camera motion
- LongFormQAEvaluator: LF-VISUAL-01 visual hierarchy, LF-15 documentary red team
"""
import pytest
from radar.models.schemas import (
    StorySelectionArtifact, RepoAnalysis, RepositoryCandidate,
    LongFormStoryType, ClaimClassification, QAGateStatus
)
from radar.agents.longform_script_agent import LongFormScriptGenerationAgent
from radar.agents.viewer_editorial_agent import ViewerEditorialAgent
from radar.agents.longform_visual_agent import LongFormVisualStorytellingAgent
from radar.qa.longform_evaluator import LongFormQAEvaluator
from radar.utils.helpers import load_config


@pytest.fixture
def sample_story():
    repo = RepositoryCandidate(
        full_name="browser-use/browser-use",
        owner="browser-use",
        name="browser-use",
        html_url="https://github.com/browser-use/browser-use",
        description="Make websites accessible to AI agents. Connect LLMs to web interactions.",
        stars=32450,
        forks=3100,
        open_issues=45,
        language="Python",
        topics=["ai", "agent", "browser-automation"]
    )
    analysis = RepoAnalysis(
        repository=repo,
        what_it_is="Open-source Python library to connect LLMs with Chromium web browser.",
        unusual_capability="Vision-based DOM indexing and multi-layer agent control.",
        technical_novelty="Eliminates fragile CSS selectors via multimodal reasoning.",
        why_care="Enables fully autonomous end-to-end web workflows and QA automation.",
        takeaway="Pioneers the agentic web era without hardcoded rules."
    )
    return StorySelectionArtifact(
        story_id="test_lf_doc_v3",
        format="long_form",
        selected_repos=[analysis],
        format_type="single_repo",
        core_hook_angle="AI tự mở trình duyệt web và thao tác như người",
        narrative_thesis="browser-use thay đổi web automation từ script cứng sang LLM reasoning."
    )


def test_longform_script_v3_enrichment(sample_story):
    config = load_config("config/factory.yaml")
    agent = LongFormScriptGenerationAgent(config)
    script = agent.generate(sample_story)

    # 1. Central Question & Viewer Promise
    assert script.central_question != ""
    assert "?" in script.central_question
    assert script.viewer_promise != ""

    # 2. Chapters enriched with transitions and questions
    assert len(script.chapters) >= 8
    for ch in script.chapters:
        if not ch.is_cta:
            assert ch.question != ""
            assert ch.curiosity_hook != ""
            assert ch.transition_to_next != ""

    # 3. Claims classified with proof levels
    all_claims = []
    for ch in script.chapters:
        all_claims.extend(ch.key_claims)
    assert len(all_claims) >= 3
    assert any(c.proof_level <= 2 for c in all_claims)


def test_viewer_editorial_agent_evaluation(sample_story):
    config = load_config("config/factory.yaml")
    script_agent = LongFormScriptGenerationAgent(config)
    editorial_agent = ViewerEditorialAgent(config)

    script = script_agent.generate(sample_story)
    report = editorial_agent.review_script(script)

    assert report.viewer_value_score >= 80.0
    assert report.decision == "PASS"
    assert report.central_question == script.central_question
    assert len(report.curiosity_gaps) >= 4
    assert len(report.narrative_arc) >= 8

    # Evaluate gate
    gate = editorial_agent.evaluate_gate(report)
    assert gate.status == QAGateStatus.PASS
    assert gate.gate_name == "LF-EDITORIAL-01:VIEWER_EDITORIAL_GATE"


def test_longform_visual_storyboard_proof_hierarchy(sample_story):
    config = load_config("config/factory.yaml")
    script_agent = LongFormScriptGenerationAgent(config)
    visual_agent = LongFormVisualStorytellingAgent()
    qa_evaluator = LongFormQAEvaluator(config)

    script = script_agent.generate(sample_story)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    # Check proof levels assigned
    levels = [b.proof_level for b in storyboard.beats]
    assert 1 in levels or 2 in levels  # Level 1 (Code/Repo) or Level 2 (Live Demo)
    assert 4 in levels or 3 in levels  # Level 3/4 (Benchmark, Architecture)

    # Check storyboard QA including LF-VISUAL-01
    reports = qa_evaluator.evaluate_storyboard(storyboard)
    visual_gate = next(r for r in reports if r.gate_name == "LF-VISUAL-01:DOCUMENTARY_VISUAL_HIERARCHY")
    assert visual_gate.status == QAGateStatus.PASS
