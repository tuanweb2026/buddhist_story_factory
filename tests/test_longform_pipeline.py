import pytest
import os
import json
from radar.utils.helpers import load_config
from radar.models.schemas import (
    RepositoryCandidate, RepoAnalysis, StorySelectionArtifact,
    LongFormStoryType, QAGateStatus, AudioArtifact, RenderArtifact
)
from radar.agents.longform_script_agent import LongFormScriptGenerationAgent
from radar.agents.longform_visual_agent import LongFormVisualStorytellingAgent
from radar.agents.asset_generation_agent import AssetGenerationAgent
from radar.qa.longform_evaluator import LongFormQAEvaluator
from radar.publisher.publisher import PublisherAgent
from radar.scheduler.scheduler import FactoryScheduler


@pytest.fixture
def config():
    return load_config("config/factory.yaml")


@pytest.fixture
def mock_repo():
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


@pytest.fixture
def mock_story(mock_repo):
    analysis = RepoAnalysis(
        repository=mock_repo,
        what_it_is="AI browser agent controller",
        unusual_capability="Controls DOM directly",
        technical_novelty="Vision + Playwright loop",
        why_care="Automates web workflows without coding scrapers",
        takeaway="Web accessibility for LLMs",
        composite_content_score=92.0
    )
    return StorySelectionArtifact(
        story_id="test_lf_story_001",
        format="long_form",
        selected_repos=[analysis],
        format_type="single_repo",
        core_hook_angle="AI tu dieu khien trinh duyet",
        narrative_thesis="browser-use opens direct web automation for AI."
    )


def test_longform_script_generation(config, mock_story):
    agent = LongFormScriptGenerationAgent(config)
    script = agent.generate(mock_story)
    assert script is not None
    assert script.format == "long_form"
    assert len(script.chapters) >= 5
    assert len(script.youtube_chapters) >= 4
    assert script.thumbnail_text != ""
    assert all(ch.duration_sec > 0 for ch in script.chapters)


def test_longform_visual_storyboard_planning(config, mock_story):
    script_agent = LongFormScriptGenerationAgent(config)
    script = script_agent.generate(mock_story)

    visual_agent = LongFormVisualStorytellingAgent()
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    assert storyboard is not None
    assert len(storyboard.beats) > len(script.chapters)
    # Check that chapter opener title cards exist
    title_cards = [b for b in storyboard.beats if b.visual_type == "CHAPTER_TITLE_CARD"]
    assert len(title_cards) >= 4
    # Check all beats have semantic intent and visual claim (no orphan visuals)
    for beat in storyboard.beats:
        assert beat.semantic_intent != ""
        assert beat.visual_claim != ""


def test_longform_qa_script_evaluation(config, mock_story):
    script_agent = LongFormScriptGenerationAgent(config)
    script = script_agent.generate(mock_story)

    evaluator = LongFormQAEvaluator(config)
    reports = evaluator.evaluate_script(script)

    assert len(reports) >= 6
    # All script gates must PASS
    for r in reports:
        assert r.status == QAGateStatus.PASS, f"Gate {r.gate_name} failed: {r.reasons}"


def test_longform_qa_cta_policy_enforcement(config, mock_story):
    script_agent = LongFormScriptGenerationAgent(config)
    script = script_agent.generate(mock_story)

    evaluator = LongFormQAEvaluator(config)
    cta_report = next(r for r in evaluator.evaluate_script(script) if "CTA_COMPLIANCE" in r.gate_name)
    assert cta_report.status == QAGateStatus.PASS

    # Inject forbidden comment call to verify fail-closed detection
    script.chapters[0].segments[0].spoken_text += " Hãy comment bên dưới ý kiến của bạn nhé."
    script.all_segments[0].spoken_text += " Hãy comment bên dưới ý kiến của bạn nhé."
    fail_reports = evaluator.evaluate_script(script)
    cta_fail = next(r for r in fail_reports if "CTA_COMPLIANCE" in r.gate_name)
    assert cta_fail.status == QAGateStatus.FAIL


def test_longform_thumbnail_generation(config, tmp_path):
    agent = AssetGenerationAgent(config, output_dir=str(tmp_path))
    thumb_path = str(tmp_path / "test_thumb.png")
    out = agent.generate_thumbnail(
        title="Test Long-form Video",
        repo_name="browser-use",
        thumbnail_text="AI Tu Dieu Khien Trinh Duyet",
        output_path=thumb_path
    )
    assert os.path.exists(out)
    assert os.path.getsize(out) > 5000


def test_longform_metadata_generation_and_publishing(config, mock_story, tmp_path):
    script_agent = LongFormScriptGenerationAgent(config)
    script = script_agent.generate(mock_story)

    history_file = str(tmp_path / "published_history.json")
    pub = PublisherAgent(config, history_file=history_file)

    render = RenderArtifact(
        story_id=script.story_id,
        video_path=str(tmp_path / f"{script.story_id}.mp4"),
        width=1920,
        height=1080,
        fps=30,
        duration_sec=320.0,
        video_codec="h264",
        audio_codec="aac",
        file_size_bytes=1024000
    )

    qa_evaluator = LongFormQAEvaluator(config)
    script_reports = qa_evaluator.evaluate_script(script)

    artifact = pub.publish_longform(
        script=script,
        render=render,
        qa_reports=script_reports,
        thumbnail_path=str(tmp_path / "thumb.png")
    )

    assert artifact is not None
    assert artifact.status in ["published_simulated", "published_live"]
    # Check that metadata file was written
    meta_path = str(tmp_path / f"{script.story_id}_metadata.json")
    assert os.path.exists(meta_path)
    with open(meta_path) as f:
        meta_data = json.load(f)
    assert meta_data["title"] == script.title
    assert meta_data["format"] == "long_form"
    assert len(meta_data["chapters"]) >= 4

    # Check deduplication: attempting to publish duplicate title must raise ValueError
    with pytest.raises(ValueError, match="Duplicate publication detected"):
        pub.publish_longform(script=script, render=render, qa_reports=script_reports)


def test_scheduler_independent_jobs(config):
    scheduler = FactoryScheduler(config)
    assert len(scheduler.DEFAULT_DAILY_SLOTS) == 4
    slot_formats = [s["format"] for s in scheduler.DEFAULT_DAILY_SLOTS]
    assert slot_formats.count("shorts") == 3
    assert slot_formats.count("long_form") == 1


def test_longform_native_16x9_asset_quality_gate(config, mock_story, tmp_path):
    from radar.agents.longform_visual_asset_engine import LongFormVisualAssetEngine
    from PIL import Image

    script_agent = LongFormScriptGenerationAgent(config)
    script = script_agent.generate(mock_story)

    visual_agent = LongFormVisualStorytellingAgent()
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    # Generate native 16:9 assets
    engine = LongFormVisualAssetEngine(config, output_dir=str(tmp_path / "visuals_16x9"))
    storyboard = engine.generate_storyboard_assets(storyboard)

    qa_evaluator = LongFormQAEvaluator(config)
    reports = qa_evaluator.evaluate_storyboard(storyboard)

    gate_10 = next(r for r in reports if "NATIVE_16X9_ASSET_QUALITY" in r.gate_name)
    assert gate_10.status == QAGateStatus.PASS

    # Test rejection of vertical 9:16 Shorts asset (fail-closed check)
    bad_asset = str(tmp_path / "bad_vertical.png")
    im_bad = Image.new("RGB", (1080, 1920), color=(0, 0, 0))
    im_bad.save(bad_asset)
    storyboard.beats[0].asset_path = bad_asset

    fail_reports = qa_evaluator.evaluate_storyboard(storyboard)
    fail_gate_10 = next(r for r in fail_reports if "NATIVE_16X9_ASSET_QUALITY" in r.gate_name)
    assert fail_gate_10.status == QAGateStatus.FAIL

