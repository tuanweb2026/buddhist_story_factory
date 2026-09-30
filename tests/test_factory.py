import os
import json
import pytest
from radar.utils.helpers import load_config
from radar.models.schemas import (
    RepositoryCandidate, RepoAnalysis, EvidenceItem, EvidenceType,
    StorySelectionArtifact, ScriptArtifact, ScriptSegment,
    VisualStoryboard, VisualBeatEvent, AudioArtifact, RenderArtifact,
    QAGateStatus, PipelineState
)
from radar.agents.discovery import DiscoveryAgent
from radar.agents.intelligence import RepositoryIntelligenceAgent, ContentScoringAgent
from radar.agents.story import StorySelectionAgent, FactVerificationAgent
from radar.agents.script import ScriptGenerationAgent
from radar.agents.visual_storytelling_agent import VisualStorytellingAgent
from radar.agents.asset_generation_agent import AssetGenerationAgent
from radar.agents.voice import VoiceGenerationAgent
from radar.agents.render import VideoRenderAgent
from radar.qa.evaluator import VisualEvaluator, AudioEvaluator, VisualRedTeam
from radar.publisher.publisher import PublisherAgent
from radar.orchestrator.pipeline import Orchestrator


@pytest.fixture
def config():
    return load_config("config/factory.yaml")


@pytest.fixture
def sample_candidates():
    return [
        RepositoryCandidate(
            full_name="browser-use/browser-use",
            owner="browser-use",
            name="browser-use",
            html_url="https://github.com/browser-use/browser-use",
            description="Make websites accessible to AI agents. Connect your AI to web interactions.",
            stars=116450,
            forks=11500,
            open_issues=45,
            language="Python",
            pushed_at="2026-09-26T10:00:00Z",
            stars_today=450,
            topics=["agent", "browser-automation", "ai"]
        )
    ]


def test_discovery_filtering_and_deduplication(config, sample_candidates, tmp_path):
    history_file = str(tmp_path / "published_history.json")
    with open(history_file, "w") as f:
        json.dump([{"full_name": "browser-use/browser-use", "publish_time": "2026-09-15T00:00:00"}], f)

    agent = DiscoveryAgent(config, history_file=history_file)
    results = agent.discover(mock_candidates=sample_candidates)
    assert len(results) == 0


def test_content_scoring_separate_from_stars(config, sample_candidates):
    repo = sample_candidates[0]
    intel_agent = RepositoryIntelligenceAgent(config)
    scoring_agent = ContentScoringAgent(config)

    analysis = intel_agent.analyze(repo)
    scored = scoring_agent.score(analysis)

    assert scored.novelty_score >= 80.0
    assert scored.composite_content_score >= 70.0
    assert len(scored.evidence) >= 3


def test_story_selection_and_format(config, sample_candidates):
    intel_agent = RepositoryIntelligenceAgent(config)
    scoring_agent = ContentScoringAgent(config)
    story_agent = StorySelectionAgent(config)

    analysis = intel_agent.analyze(sample_candidates[0])
    scored = scoring_agent.score(analysis)

    story = story_agent.select_story([scored], format_type="shorts")
    assert story is not None
    assert story.format_type == "single_repo"
    assert "browser-use" in story.core_hook_angle


def test_visual_storytelling_engine_v2(config, sample_candidates):
    intel = RepositoryIntelligenceAgent(config).analyze(sample_candidates[0])
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    visual_agent = VisualStorytellingAgent(config)
    storyboard = visual_agent.plan_storyboard(script)

    assert storyboard.beats[0].visual_type in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK"]
    
    # Check visual evaluator
    evaluator = VisualEvaluator(config)
    reports = evaluator.evaluate_storyboard(storyboard)
    assert all(r.status == QAGateStatus.PASS for r in reports)


def test_cta_policy_and_red_team_rejection(config, sample_candidates):
    intel = RepositoryIntelligenceAgent(config).analyze(sample_candidates[0])
    scored = ContentScoringAgent(config).score(intel)
    story = StorySelectionAgent(config).select_story([scored])
    script = ScriptGenerationAgent(config).generate(story)

    # Corrupt script with forbidden comment CTA
    script.segments[-1].spoken_text = "Hãy để lại bình luận để nhận đường dẫn repo nhé!"
    
    red_team = VisualRedTeam(config)
    storyboard = VisualStorytellingAgent(config).plan_storyboard(script)
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
    report = red_team.audit(storyboard, script, dummy_render)
    assert report.status == QAGateStatus.FAIL
    assert "Forbidden comment CTA" in str(report.reasons)


def test_end_to_end_v2_pipeline(config, sample_candidates, tmp_path):
    data_dir = str(tmp_path / "factory_data")
    orchestrator = Orchestrator(config, data_dir=data_dir)

    result = orchestrator.run_pipeline(
        format_type="shorts",
        mock_candidates=[sample_candidates[0]],
        stop_at_human_review=True
    )

    assert result["state"] == PipelineState.READY_FOR_HUMAN_REVIEW
    assert os.path.exists(result["render"].video_path)
    assert len(result["storyboard"].beats) >= 6
    assert result["audio"].voice_name in ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural", "Linh"]
    assert all(r.status == QAGateStatus.PASS for r in result["qa_reports"])
