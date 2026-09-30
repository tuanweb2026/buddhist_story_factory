"""
Unit and integration tests for Long-Form Documentary Engine V4.
Verifies:
- EditorialIntelligenceAgent: Synthesizes complete 10-point EditorialThesis
- LongFormScriptGenerationAgent: 5–8 min (300–480s) narrative, 7–10 chapters, enriched chapters (tension, explanation, payoff, proof target)
- ViewerEditorialAgent V4: ViewerValueScore >= 90.0, Explanation Quality >= 12.0/15, LF-EDITORIAL-01 PASS
- LongFormVisualStorytellingAgent: Complete visual sequence (narration_claim, visual_intent, evidence_type, visual_asset, attention_target, camera_motion, visual_payoff, transition_reason)
- LongFormQAEvaluator: 15 Fail-Closed V4 QA Gates (LF-V4-01 through LF-V4-15)
"""
import pytest
from radar.models.schemas import (
    StorySelectionArtifact, RepoAnalysis, RepositoryCandidate,
    LongFormStoryType, ClaimClassification, QAGateStatus,
    AudioArtifact, RenderArtifact, LongFormMetadata
)
from radar.agents.editorial_intelligence_agent import EditorialIntelligenceAgent
from radar.agents.longform_script_agent import LongFormScriptGenerationAgent
from radar.agents.viewer_editorial_agent import ViewerEditorialAgent
from radar.agents.longform_visual_agent import LongFormVisualStorytellingAgent
from radar.qa.longform_evaluator import LongFormQAEvaluator
from radar.utils.helpers import load_config


@pytest.fixture
def config():
    return load_config("config/factory.yaml")


@pytest.fixture
def browser_use_story():
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
        takeaway="Pioneers the agentic web era without hardcoded rules.",
        composite_content_score=94.0
    )
    return StorySelectionArtifact(
        story_id="test_lf_v4_browser_use",
        format="long_form",
        selected_repos=[analysis],
        format_type="single_repo",
        core_hook_angle="AI tự mở trình duyệt web và thao tác như người",
        narrative_thesis="browser-use thay đổi web automation từ script cứng sang LLM reasoning."
    )


@pytest.fixture
def uv_story():
    repo = RepositoryCandidate(
        full_name="astral-sh/uv",
        owner="astral-sh",
        name="uv",
        html_url="https://github.com/astral-sh/uv",
        description="An extremely fast Python package and project manager, written in Rust.",
        stars=38500,
        forks=1200,
        open_issues=80,
        language="Rust",
        topics=["python", "rust", "package-manager", "pip"]
    )
    analysis = RepoAnalysis(
        repository=repo,
        what_it_is="Extremely fast Python package manager written in Rust.",
        unusual_capability="10-100x faster than pip via PubGrub and hardlinks.",
        technical_novelty="Rewrites Python core tooling infrastructure in Rust.",
        why_care="Massively reduces CI/CD times and Docker build overhead.",
        takeaway="Rust is the new runtime engine for Python developer infrastructure.",
        composite_content_score=95.0
    )
    return StorySelectionArtifact(
        story_id="test_lf_v4_uv",
        format="long_form",
        selected_repos=[analysis],
        format_type="single_repo",
        core_hook_angle="Trình quản lý gói Python nhanh gấp 100 lần pip",
        narrative_thesis="uv mang lại cuộc cách mạng tooling cho Python nhờ Rust."
    )


def test_editorial_intelligence_agent(browser_use_story, uv_story):
    agent = EditorialIntelligenceAgent()
    
    thesis_bu = agent.synthesize_thesis(browser_use_story)
    assert thesis_bu is not None
    assert "browser-use" in thesis_bu.editorial_thesis
    assert "?" in thesis_bu.central_question
    assert thesis_bu.viewer_promise != ""
    assert thesis_bu.key_tension != ""
    assert thesis_bu.technical_breakthrough != ""
    assert thesis_bu.real_world_implication != ""
    assert thesis_bu.trade_off != ""
    assert thesis_bu.limitation != ""
    assert thesis_bu.final_payoff != ""

    thesis_uv = agent.synthesize_thesis(uv_story)
    assert thesis_uv is not None
    assert "uv" in thesis_uv.editorial_thesis
    assert "?" in thesis_uv.central_question


def test_longform_script_v4_architecture(config, browser_use_story, uv_story):
    agent = LongFormScriptGenerationAgent(config)

    # Test browser-use (9 chapters, ~375s, 900+ words)
    script_bu = agent.generate(browser_use_story)
    assert script_bu.editorial_thesis is not None
    assert script_bu.target_duration_sec >= 300.0  # 5–8 min
    assert script_bu.total_spoken_words >= 800
    assert 7 <= len(script_bu.chapters) <= 10
    
    for ch in script_bu.chapters:
        if not ch.is_cta:
            assert ch.tension != "", f"Chapter {ch.chapter_label} missing tension"
            assert ch.explanation != "", f"Chapter {ch.chapter_label} missing explanation"
            assert ch.visual_proof_target != "", f"Chapter {ch.chapter_label} missing visual_proof_target"
            assert ch.payoff != "", f"Chapter {ch.chapter_label} missing payoff"
            assert ch.transition_to_next != "", f"Chapter {ch.chapter_label} missing transition_to_next"

    # Test uv (10 chapters, ~390s, 900+ words)
    script_uv = agent.generate(uv_story)
    assert script_uv.editorial_thesis is not None
    assert script_uv.target_duration_sec >= 300.0
    assert script_uv.total_spoken_words >= 800
    assert len(script_uv.chapters) == 10


def test_viewer_editorial_agent_v4_thresholds(config, browser_use_story, uv_story):
    script_agent = LongFormScriptGenerationAgent(config)
    editorial_agent = ViewerEditorialAgent(config)

    for story in [browser_use_story, uv_story]:
        script = script_agent.generate(story)
        report = editorial_agent.review_script(script)

        # V4 strict thresholds: ViewerValueScore >= 90.0, Explanation Quality >= 12.0
        assert report.viewer_value_score >= 90.0, f"Score {report.viewer_value_score} < 90.0: {report.reasons}"
        assert report.score_breakdown["explanation_quality"] >= 12.0
        assert report.decision == "PASS"

        gate = editorial_agent.evaluate_gate(report)
        assert gate.status == QAGateStatus.PASS


def test_longform_visual_storytelling_v4_sequence(config, browser_use_story):
    script_agent = LongFormScriptGenerationAgent(config)
    visual_agent = LongFormVisualStorytellingAgent()

    script = script_agent.generate(browser_use_story)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    assert len(storyboard.beats) >= 20
    for beat in storyboard.beats:
        # Full visual sequence verification
        assert beat.narration_claim != ""
        assert beat.visual_intent != ""
        assert beat.evidence_type != ""
        assert beat.visual_asset != ""
        assert beat.attention_target != ""
        assert beat.camera_motion != ""
        assert beat.visual_payoff != ""
        assert beat.transition_reason != ""


def test_all_15_v4_qa_gates_pass(config, browser_use_story, tmp_path):
    script_agent = LongFormScriptGenerationAgent(config)
    visual_agent = LongFormVisualStorytellingAgent()
    qa_evaluator = LongFormQAEvaluator(config)

    script = script_agent.generate(browser_use_story)
    storyboard = visual_agent.plan_storyboard(script, repo_category="BROWSER_AGENT")

    # 1. Script evaluation gates (LF-V4-01, 02, 03, 04, 05, 06, 11, 12, 13, 14, LF-10)
    script_reports = qa_evaluator.evaluate_script(script)
    for r in script_reports:
        assert r.status == QAGateStatus.PASS, f"Script Gate {r.gate_name} failed: {r.reasons}"

    # 2. Storyboard evaluation gates (LF-V4-07, 08, 09, LF-07, 08, LF-VISUAL-01)
    storyboard_reports = qa_evaluator.evaluate_storyboard(storyboard)
    for r in storyboard_reports:
        assert r.status == QAGateStatus.PASS, f"Storyboard Gate {r.gate_name} failed: {r.reasons}"

    # 3. Media & Red Team evaluation gates (LF-09, LF-12, LF-13, LF-V4-15)
    thumb_path = str(tmp_path / "thumb.png")
    with open(thumb_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 10000)

    audio = AudioArtifact(
        story_id=script.story_id,
        audio_path=str(tmp_path / "audio.wav"),
        duration_sec=375.0,
        sample_rate=24000,
        channels=1,
        lufs=-16.1,
        true_peak_db=-1.2,
        voice_name="vi-VN-HoaiMyNeural",
        provider="edge_tts"
    )
    render = RenderArtifact(
        story_id=script.story_id,
        video_path=str(tmp_path / "video.mp4"),
        width=1920,
        height=1080,
        fps=30,
        duration_sec=375.0,
        video_codec="h264",
        audio_codec="aac",
        file_size_bytes=50000000
    )
    metadata = LongFormMetadata(
        story_id=script.story_id,
        title=script.title,
        description=script.description,
        chapters=script.youtube_chapters,
        repository_urls=script.repository_urls,
        sources=script.sources,
        hashtags=script.hashtags,
        thumbnail_text=script.thumbnail_text,
        duration_sec=375.0,
        voice="vi-VN-HoaiMyNeural"
    )

    media_reports = qa_evaluator.evaluate_media(audio, render, metadata, thumb_path)
    for r in media_reports:
        assert r.status == QAGateStatus.PASS, f"Media Gate {r.gate_name} failed: {r.reasons}"

    red_team = qa_evaluator.audit_final_red_team(script, storyboard, render, audio)
    assert red_team.status == QAGateStatus.PASS, f"Red Team failed: {red_team.reasons}"
