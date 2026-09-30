"""
Unit and integration tests for ChatCommandRouter (Antigravity Chat Command Mode).
Verifies:
- Intent detection across all natural language phrases:
    "tạo Shorts", "tạo video dài", "tạo daily batch", "tạo video tiếp theo",
    "review video", "publish video", etc.
- Parameter extraction (batch counts, repo names).
- Execution to READY_FOR_HUMAN_REVIEW without auto-publishing.
- Multi-dimension Video Review inspection.
- Explicit human authorization for publishing (PUBLISH_APPROVED).
- Fail-closed enforcement on publication.
"""
import os
import pytest
from radar.chat.chat_command_router import ChatCommandRouter, ChatIntent
from radar.utils.helpers import load_config
from radar.orchestrator.pipeline import Orchestrator, PipelineState
from radar.models.schemas import (
    RepositoryCandidate, RepoAnalysis, StorySelectionArtifact,
    ScriptArtifact, RenderArtifact, AudioArtifact, QAReport, QAGateStatus
)


@pytest.fixture
def config():
    return load_config("config/factory.yaml")


@pytest.fixture
def router(config, tmp_path):
    r = ChatCommandRouter(config=config)
    r.orchestrator.publisher.history_file = str(tmp_path / "published_history.json")
    return r


@pytest.fixture(autouse=True)
def mock_voice_synth(monkeypatch):
    """Mocks voice generation with broadcast-normalized wave to prevent rate limits during test suite."""
    import subprocess
    from radar.agents.voice import VoiceGenerationAgent

    def fake_synth(self, text: str, voice_name: str, output_wav: str) -> bool:
        os.makedirs(os.path.dirname(output_wav), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=45",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar", "44100", "-ac", "2",
            output_wav
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0

    monkeypatch.setattr(VoiceGenerationAgent, "_synthesize_neural", fake_synth)


# ──────────────────────────────────────────────────────────────────────────────
# 1. INTENT DETECTION TESTS
# ──────────────────────────────────────────────────────────────────────────────

def test_intent_detection_shorts(router):
    cases = [
        ("Tạo Shorts #2", ChatIntent.CREATE_SHORT, 2),
        ("tạo short video", ChatIntent.CREATE_SHORT, None),
        ("Tạo video ngắn về repo browser-use", ChatIntent.CREATE_SHORT, None),
        ("Chạy shorts hôm nay", ChatIntent.CREATE_SHORT, None),
    ]
    for text, expected_intent, expected_num in cases:
        intent, params = router.detect_intent(text)
        assert intent == expected_intent, f"Failed for: {text}"
        if expected_num is not None:
            assert params.get("job_number") == expected_num


def test_intent_detection_longform(router):
    cases = [
        ("Tạo video dài hôm nay", ChatIntent.CREATE_LONGFORM),
        ("Tạo long-form documentary về astral-sh/uv", ChatIntent.CREATE_LONGFORM),
        ("tạo video tài liệu 16:9", ChatIntent.CREATE_LONGFORM),
        ("Chạy longform mới", ChatIntent.CREATE_LONGFORM),
    ]
    for text, expected_intent in cases:
        intent, params = router.detect_intent(text)
        assert intent == expected_intent, f"Failed for: {text}"


def test_intent_detection_daily_batch(router):
    cases = [
        ("Tạo daily batch", ChatIntent.CREATE_DAILY_BATCH, 3, 1),
        ("Tạo 2 Shorts + 1 Long-form", ChatIntent.CREATE_DAILY_BATCH, 2, 1),
        ("Chạy daily production", ChatIntent.CREATE_DAILY_BATCH, 3, 1),
        ("Tạo 3 Shorts hôm nay", ChatIntent.CREATE_DAILY_BATCH, 3, 1),
    ]
    for text, expected_intent, exp_s, exp_l in cases:
        intent, params = router.detect_intent(text)
        assert intent == expected_intent, f"Failed for: {text}"
        assert params.get("shorts_count") == exp_s
        assert params.get("longform_count") == exp_l


def test_intent_detection_next_video(router):
    cases = [
        ("Tạo video tiếp theo", ChatIntent.CREATE_NEXT),
        ("Tạo một video về repo đang hot nhất hôm nay", ChatIntent.CREATE_NEXT),
        ("next video", ChatIntent.CREATE_NEXT),
        ("chọn repo hot nhất làm video", ChatIntent.CREATE_NEXT),
    ]
    for text, expected_intent in cases:
        intent, params = router.detect_intent(text)
        assert intent == expected_intent, f"Failed for: {text}"


def test_intent_detection_review_and_repair(router):
    # Review
    intent, _ = router.detect_intent("Review video này")
    assert intent == ChatIntent.REVIEW_VIDEO

    intent, _ = router.detect_intent("Kiểm tra video vừa render")
    assert intent == ChatIntent.REVIEW_VIDEO

    # Repair
    intent, _ = router.detect_intent("Review và sửa video vừa render")
    assert intent == ChatIntent.REPAIR_VIDEO

    intent, _ = router.detect_intent("Tự sửa lỗi video")
    assert intent == ChatIntent.REPAIR_VIDEO


def test_intent_detection_publish(router):
    cases = [
        "Publish video này",
        "Approve và publish",
        "Publish tất cả video đã approved",
        "OK, publish",
        "Đồng ý publish video"
    ]
    for text in cases:
        intent, _ = router.detect_intent(text)
        assert intent == ChatIntent.PUBLISH_APPROVED, f"Failed for: {text}"


def test_intent_detection_status_and_result(router):
    intent, _ = router.detect_intent("Xem trạng thái hệ thống")
    assert intent == ChatIntent.SHOW_STATUS

    intent, _ = router.detect_intent("Xem kết quả gần nhất")
    assert intent == ChatIntent.SHOW_LAST_RESULT


# ──────────────────────────────────────────────────────────────────────────────
# 2. EXECUTION & SAFETY TESTS
# ──────────────────────────────────────────────────────────────────────────────

def test_chat_create_short_stops_at_human_review(router):
    """Verifies that 'Tạo Shorts' runs to READY_FOR_HUMAN_REVIEW and does not auto-publish."""
    res = router.handle_command("Tạo Shorts #1 về repo browser-use/browser-use")
    assert res["success"] is True
    assert res["intent"] == ChatIntent.CREATE_SHORT.value
    assert "READY_FOR_HUMAN_REVIEW" in res["response_text"]
    assert "GITHUB PROJECT RADAR FACTORY" in res["response_text"]
    assert "PRODUCTION COMPLETE" in res["response_text"]
    assert "Human Action:\nREVIEW VIDEO" in res["response_text"]
    assert len(router.pending_reviews) == 1


def test_chat_review_video(router):
    """Verifies multi-dimension video inspection."""
    # Ensure there is a pending review job
    router.handle_command("Tạo Shorts #1 về repo browser-use/browser-use")
    
    review_res = router.handle_command("Review video này")
    assert review_res["success"] is True
    assert review_res["intent"] == ChatIntent.REVIEW_VIDEO.value
    
    text = review_res["response_text"]
    assert "VIDEO REVIEW" in text
    assert "Visual:" in text
    assert "Narration:" in text
    assert "Voice:" in text
    assert "Story:" in text
    assert "Retention:" in text
    assert "Technical:" in text
    assert "Overall:" in text


def test_chat_publish_only_after_approval(router):
    """Verifies that publishing only happens upon explicit PUBLISH_APPROVED command."""
    # Step 1: Produce video (stops at READY_FOR_HUMAN_REVIEW)
    create_res = router.handle_command("Tạo Shorts #2 về repo browser-use/browser-use")
    assert create_res["result"]["state"] == PipelineState.READY_FOR_HUMAN_REVIEW

    # Step 2: Approve and publish
    pub_res = router.handle_command("Approve và publish video này")
    assert pub_res["success"] is True
    assert pub_res["intent"] == ChatIntent.PUBLISH_APPROVED.value
    assert "PUBLICATION COMPLETE" in pub_res["response_text"]
    assert "Video URL:" in pub_res["response_text"]
    assert "PUBLISHED" in pub_res["response_text"]


def test_chat_publish_fails_without_pending_job(router):
    """Verifies fail-closed behavior when no video is in review."""
    router.pending_reviews = []
    router.last_result = None
    pub_res = router.handle_command("Publish video này")
    assert pub_res["success"] is False
    assert "Không có video nào" in pub_res["response_text"]


def test_chat_create_next_auto_selection(router):
    """Verifies 'Tạo video tiếp theo' auto-discovers and picks candidate without prompt."""
    res = router.handle_command("Tạo video tiếp theo")
    assert res["success"] is True
    assert res["intent"] == ChatIntent.CREATE_NEXT.value
    assert "READY_FOR_HUMAN_REVIEW" in res["response_text"]
    assert "NEXT VIDEO" in res["response_text"]
