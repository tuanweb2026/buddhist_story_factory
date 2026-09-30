import os
import pytest
from radar.utils.helpers import load_config
from radar.models.schemas import (
    RepositoryCandidate, RepoAnalysis, StorySelectionArtifact,
    ScriptArtifact, ScriptSegment, VisualStoryboard, VisualBeatEvent,
    AudioArtifact, RenderArtifact, QAGateStatus
)
from radar.agents.intelligence import RepositoryIntelligenceAgent, ContentScoringAgent
from radar.agents.story import StorySelectionAgent
from radar.agents.script import ScriptGenerationAgent
from radar.agents.visual_storytelling_agent import VisualStorytellingAgent
from radar.agents.asset_generation_agent import AssetGenerationAgent
from radar.qa.evaluator import VisualEvaluator, VisualRedTeam


@pytest.fixture
def config():
    return load_config("config/factory.yaml")


@pytest.fixture
def browser_use_candidate():
    return RepositoryCandidate(
        full_name="browser-use/browser-use",
        owner="browser-use",
        name="browser-use",
        html_url="https://github.com/browser-use/browser-use",
        description="Make websites accessible to AI agents. Connect your AI to web interactions.",
        stars=32450,
        forks=3100,
        open_issues=45,
        language="Python",
        pushed_at="2026-09-26T10:00:00Z",
        stars_today=450,
        topics=["agent", "browser-automation", "ai"]
    )


def test_narration_first_visual_mapping(config, browser_use_candidate):
    """TEST 1: Visual beats prove exact narration claims (no orphan visuals)."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    for beat in storyboard.beats:
        assert beat.semantic_intent != "", f"Beat {beat.beat_id} has empty semantic_intent"
        assert beat.visual_claim != "", f"Beat {beat.beat_id} has empty visual_claim"
        assert beat.attention_target != "", f"Beat {beat.beat_id} has empty attention_target"


def test_visual_event_type_coverage(config, browser_use_candidate):
    """TEST 2: Diverse visual event types present (REAL_REPOSITORY_UI, BROWSER_DEMO, TERMINAL_DEMO, etc)."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")
    types = [b.visual_type for b in storyboard.beats]

    assert "REAL_REPOSITORY_UI" in types
    assert any(t in types for t in ["BROWSER_DEMO", "TECHNICAL_FLOW"])
    assert any(t in types for t in ["TERMINAL_DEMO", "DATA_VISUALIZATION", "BEFORE_AFTER"])
    assert "CTA" in types


def test_browser_use_action_demonstration(config, browser_use_candidate):
    """TEST 3: Browser-use storyboard contains concrete simulated browser interaction."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    browser_beats = [b for b in storyboard.beats if b.visual_type in ["BROWSER_DEMO", "TECHNICAL_FLOW"]]
    assert len(browser_beats) >= 1
    # Check that at least one beat mentions form/flight/click in diagram elements or narration
    combined = " ".join([str(b.diagram_elements) + " " + b.narration for b in browser_beats]).lower()
    assert any(w in combined for w in ["booking", "flight", "trình duyệt", "form", "click", "ai"])


def test_attention_target_and_camera_motion_alignment(config, browser_use_candidate):
    """TEST 4: Every beat pairs an attention target with purposeful camera motion."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    valid_motions = {
        "PUSH_IN", "ZOOM_TO_DETAIL", "PAN_LEFT_TO_RIGHT", "DATA_FLOW",
        "REVEAL", "BEFORE_AFTER_SPLIT", "PAYOFF_PUSH", "STATIC", "ZOOM_PAN",
        "PROGRESSIVE_REVEAL", "PAYOFF_REVEAL"
    }
    for beat in storyboard.beats:
        assert beat.attention_target is not None and len(beat.attention_target) > 0
        assert beat.motion_type in valid_motions


def test_visual_payoff_resolution(config, browser_use_candidate):
    """TEST 5: All beats declare visual payoff resolution before transition."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    for beat in storyboard.beats:
        assert beat.payoff != ""
        assert beat.transition != ""


def test_asset_generation_produces_real_ui_canvases(config, browser_use_candidate, tmp_path):
    """TEST 6: AssetGenerationAgent renders full visual files with high technical detail."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    asset_dir = str(tmp_path / "test_visuals")
    generator = AssetGenerationAgent(config, output_dir=asset_dir)
    rendered_sb = generator.generate_assets(storyboard)

    for beat in rendered_sb.beats:
        assert os.path.exists(beat.asset_path)
        assert os.path.getsize(beat.asset_path) > 10000  # Non-empty PNG file


def test_qa_evaluator_passes_v3_storyboard(config, browser_use_candidate):
    """TEST 7: VisualEvaluator passes all GATE-V01 through GATE-V12 on compliant storyboard."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    evaluator = VisualEvaluator(config)
    reports = evaluator.evaluate_storyboard(storyboard)
    assert all(r.status == QAGateStatus.PASS for r in reports), [f"{r.gate_name}: {r.reasons}" for r in reports if r.status != QAGateStatus.PASS]


def test_qa_evaluator_rejects_orphan_visuals(config, browser_use_candidate):
    """TEST 8: VisualEvaluator fails-closed when orphan visual (missing semantic intent) is introduced."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    # Corrupt beat 2 by wiping semantic mapping
    storyboard.beats[1].semantic_intent = ""
    storyboard.beats[1].visual_claim = ""

    evaluator = VisualEvaluator(config)
    reports = evaluator.evaluate_storyboard(storyboard)
    v02_report = next(r for r in reports if "GATE-V02" in r.gate_name)
    assert v02_report.status == QAGateStatus.FAIL
    assert "Orphan visuals detected" in str(v02_report.reasons)


def test_qa_evaluator_rejects_forbidden_comment_cta(config, browser_use_candidate):
    """TEST 9: VisualEvaluator strictly fails when forbidden comment CTA is present."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    # Corrupt CTA beat with comment request
    storyboard.beats[-1].headline_text = "HÃY ĐỂ LẠI BÌNH LUẬN NHÉ"

    evaluator = VisualEvaluator(config)
    reports = evaluator.evaluate_storyboard(storyboard)
    v12_report = next(r for r in reports if "GATE-V12" in r.gate_name)
    assert v12_report.status == QAGateStatus.FAIL
    assert "Forbidden comment CTA detected" in str(v12_report.reasons)


def test_red_team_rejects_slideshow_and_approves_v3(config, browser_use_candidate):
    """TEST 10: Red Team rejects decorative text slideshow and approves compliant V3 production."""
    intel = RepositoryIntelligenceAgent(config).analyze(browser_use_candidate)
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    dummy_render = RenderArtifact(
        story_id=story.story_id,
        video_path="dummy.mp4",
        width=1080,
        height=1920,
        fps=30,
        duration_sec=45.0,
        video_codec="h264",
        audio_codec="aac",
        file_size_bytes=50000
    )

    red_team = VisualRedTeam(config)
    pass_report = red_team.audit(storyboard, script, dummy_render)
    assert pass_report.status == QAGateStatus.PASS

    # Corrupt into decorative slideshow
    for b in storyboard.beats:
        b.visual_type = "REAL_REPOSITORY_UI"
    storyboard.beats[-1].visual_type = "CTA"
    fail_report = red_team.audit(storyboard, script, dummy_render)
    assert fail_report.status == QAGateStatus.FAIL
    assert "slideshow" in str(fail_report.reasons).lower()
