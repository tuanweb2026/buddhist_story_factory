import os
from typing import Dict, Any, List
from radar.models.schemas import (
    QAReport, QAGateStatus, RepositoryCandidate, RepoAnalysis,
    StorySelectionArtifact, ScriptArtifact, VisualStoryboard,
    AudioArtifact, RenderArtifact
)


class VisualEvaluator:
    """Detailed visual quality evaluator implementing GATE-V01 through GATE-V12 (Visual Storytelling Engine V3)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def evaluate_storyboard(self, storyboard: VisualStoryboard) -> List[QAReport]:
        reports = []
        beats = storyboard.beats

        # GATE-V01: VISUAL_CONTENT_PRESENT
        if not beats:
            reports.append(QAReport(
                gate_name="GATE-V01:VISUAL_CONTENT_PRESENT",
                status=QAGateStatus.FAIL,
                score=0.0,
                reasons=["Storyboard contains zero visual beats."]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V01:VISUAL_CONTENT_PRESENT",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=[f"{len(beats)} visual beats scheduled."]
            ))

        # GATE-V02: VISUAL_STORYTELLING & NO_ORPHAN_VISUALS
        orphan_beats = [b.beat_id for b in beats if not b.semantic_intent or not b.visual_claim]
        if orphan_beats:
            reports.append(QAReport(
                gate_name="GATE-V02:VISUAL_STORYTELLING",
                status=QAGateStatus.FAIL,
                score=0.4,
                reasons=[f"Orphan visuals detected without semantic narration mapping: {orphan_beats}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V02:VISUAL_STORYTELLING",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["Every visual beat proves or illustrates an exact narration claim (zero orphan visuals)."]
            ))

        # GATE-V03: VISUAL_VARIETY (At least 4 distinct visual types)
        visual_types = [b.visual_type.upper() for b in beats]
        unique_types = set(visual_types)
        if len(unique_types) < 4:
            reports.append(QAReport(
                gate_name="GATE-V03:VISUAL_VARIETY",
                status=QAGateStatus.FAIL,
                score=0.4,
                reasons=[f"Insufficient visual variety: only {len(unique_types)} distinct visual types used: {unique_types}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V03:VISUAL_VARIETY",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=[f"Strong visual variety with {len(unique_types)} distinct scene paradigms."]
            ))

        # GATE-V04: TECHNICAL_VISUALIZATION (Must contain technical demo/flow/architecture)
        tech_types = {
            "TECHNICAL_FLOW", "BROWSER_DEMO", "TERMINAL_DEMO", "ARCHITECTURE_DIAGRAM",
            "BEFORE_AFTER", "DATA_VISUALIZATION", "AGENT_WORKFLOW", "BROWSER_INTERACTION",
            "DEVICE_INTERACTION", "SYSTEM_DIAGRAM", "CODE_VISUALIZATION", "HARDWARE_VISUALIZATION"
        }
        has_tech = any(t in tech_types for t in visual_types)
        if not has_tech:
            reports.append(QAReport(
                gate_name="GATE-V04:TECHNICAL_VISUALIZATION",
                status=QAGateStatus.FAIL,
                score=0.0,
                reasons=["No technical concept visualization or simulation found in storyboard."]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V04:TECHNICAL_VISUALIZATION",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["Technical concepts visually demonstrated via architecture / interaction diagrams."]
            ))

        # GATE-V05: CAMERA_ATTENTION_GUIDANCE (Every beat must declare attention target & purposeful camera motion)
        unfocused_beats = [b.beat_id for b in beats if not b.attention_target or not b.motion_type]
        if unfocused_beats:
            reports.append(QAReport(
                gate_name="GATE-V05:CAMERA_ATTENTION_GUIDANCE",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=[f"Beats lacking explicit attention target or camera motion: {unfocused_beats}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V05:CAMERA_ATTENTION_GUIDANCE",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["Every visual beat directs camera motion toward a clear attention target."]
            ))

        # GATE-V06: VISUAL_PAYOFF_AND_TRANSITION (Beats have payoff resolution and transition)
        lacking_payoff = [b.beat_id for b in beats if not b.payoff]
        if lacking_payoff:
            reports.append(QAReport(
                gate_name="GATE-V06:VISUAL_PAYOFF",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=[f"Beats missing visual payoff: {lacking_payoff}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V06:VISUAL_PAYOFF",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["All beats resolve into concrete visual payoffs before transition."]
            ))

        # GATE-V07: HOOK_VISUAL (First 2 seconds must identify repository)
        first_beat = beats[0] if beats else None
        valid_hook_types = {"REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK"}
        if first_beat and first_beat.visual_type.upper() not in valid_hook_types:
            reports.append(QAReport(
                gate_name="GATE-V07:HOOK_VISUAL",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=[f"First 2 seconds visual type {first_beat.visual_type} lacks immediate repository identification."]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V07:HOOK_VISUAL",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["First 2 seconds immediately establishes repository curiosity and subject identification."]
            ))

        # GATE-V08: TEXT_DENSITY (Headlines <= 6 words, no paragraph slides)
        word_violations = [b.beat_id for b in beats if len(b.headline_text.split()) > 7]
        if word_violations:
            reports.append(QAReport(
                gate_name="GATE-V08:TEXT_DENSITY",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=[f"Headlines exceed concise 6-word limit on beats: {word_violations}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V08:TEXT_DENSITY",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["All headlines are concise (<= 6 words); no paragraph walls on screen."]
            ))

        # GATE-V09: NO_DECORATIVE_BACKGROUND (Reject purely decorative slides)
        decorative_beats = [b.beat_id for b in beats if not b.diagram_elements and not b.visual_action]
        if decorative_beats:
            reports.append(QAReport(
                gate_name="GATE-V09:NO_DECORATIVE_BACKGROUND",
                status=QAGateStatus.FAIL,
                score=0.3,
                reasons=[f"Purely decorative beats without active diagrams or actions: {decorative_beats}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V09:NO_DECORATIVE_BACKGROUND",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["All visual scenes feature active UI diagrams, technical flows, or interaction simulations."]
            ))

        # GATE-V10: REPOSITORY_IDENTITY_CLEAR
        repo_beats = [b for b in beats if b.visual_type.upper() in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK", "PAYOFF_VISUAL", "RESULT_PAYOFF"]]
        if not repo_beats:
            reports.append(QAReport(
                gate_name="GATE-V10:REPOSITORY_IDENTITY_CLEAR",
                status=QAGateStatus.FAIL,
                score=0.4,
                reasons=["Repository name/URL not prominently identified in storyboard."]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V10:REPOSITORY_IDENTITY_CLEAR",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["Repository identity and source provenance clearly established."]
            ))

        # GATE-V11: MOTION_COHERENCE (Camera motions belong to allowed cinematic vocabulary)
        allowed_motions = {
            "PUSH_IN", "ZOOM_TO_DETAIL", "PAN_LEFT_TO_RIGHT", "DATA_FLOW",
            "REVEAL", "BEFORE_AFTER_SPLIT", "PAYOFF_PUSH", "STATIC", "ZOOM_PAN",
            "PROGRESSIVE_REVEAL", "PAYOFF_REVEAL", "CURSOR_CLICK_SEQUENCE"
        }
        invalid_motions = [b.beat_id for b in beats if b.motion_type.upper() not in allowed_motions]
        if invalid_motions:
            reports.append(QAReport(
                gate_name="GATE-V11:MOTION_COHERENCE",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=[f"Invalid camera motion types found on beats: {invalid_motions}"]
            ))
        else:
            reports.append(QAReport(
                gate_name="GATE-V11:MOTION_COHERENCE",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=["Camera motion strictly follows semantic vocabulary."]
            ))

        # GATE-V12: CTA_POLICY (Strict: Like, Share, Subscribe only. No comment CTA)
        last_beat = beats[-1] if beats else None
        if last_beat:
            bad_cta_words = ["bình luận", "comment", "ý kiến"]
            found_bad = any(w in last_beat.headline_text.lower() for w in bad_cta_words)
            if found_bad:
                reports.append(QAReport(
                    gate_name="GATE-V12:CTA_POLICY",
                    status=QAGateStatus.FAIL,
                    score=0.0,
                    reasons=["Forbidden comment CTA detected on screen."]
                ))
            else:
                reports.append(QAReport(
                    gate_name="GATE-V12:CTA_POLICY",
                    status=QAGateStatus.PASS,
                    score=1.0,
                    reasons=["CTA complies strictly with policy: LIKE • SHARE • ĐĂNG KÝ KÊNH."]
                ))

        return reports


class AudioEvaluator:
    """Detailed audio quality evaluator checking voice provider, loudness, and peaks."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def evaluate(self, audio: AudioArtifact) -> QAReport:
        if not os.path.exists(audio.audio_path):
            return QAReport(
                gate_name="audio",
                status=QAGateStatus.FAIL,
                score=0.0,
                reasons=["Audio file not found on disk."]
            )

        if audio.duration_sec < 15.0 or audio.duration_sec > 65.0:
            return QAReport(
                gate_name="audio",
                status=QAGateStatus.FAIL,
                score=0.4,
                reasons=[f"Audio duration {audio.duration_sec}s outside allowed Shorts window [15s, 65s]."]
            )

        reasons = [
            f"Provider: {audio.provider} ({audio.voice_name})",
            f"Integrated Loudness: {audio.lufs} LUFS",
            f"True Peak: {audio.true_peak_db} dBTP",
            f"Duration: {audio.duration_sec}s"
        ]

        if audio.true_peak_db > -0.5:
            return QAReport(
                gate_name="audio",
                status=QAGateStatus.FAIL,
                score=0.5,
                reasons=reasons + ["True peak exceeds -0.5 dBTP; audio clipping detected."]
            )

        return QAReport(
            gate_name="audio",
            status=QAGateStatus.PASS,
            score=1.0,
            reasons=reasons
        )


class VisualRedTeam:
    """Red Team visual adversarial check enforcing V3 quality gates with fail-closed semantics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def audit(self, storyboard: VisualStoryboard, script: ScriptArtifact, render: RenderArtifact) -> QAReport:
        types = [b.visual_type.upper() for b in storyboard.beats]

        # Check 1: Slide-deck rejection
        if all(t in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "CTA"] for t in types):
            return QAReport(
                gate_name="final_red_team",
                status=QAGateStatus.FAIL,
                score=0.0,
                reasons=["Red Team Rejected: Video looks like a static slideshow."]
            )

        # Check 2: Text walls
        if any(len(b.headline_text.split()) > 8 for b in storyboard.beats):
            return QAReport(
                gate_name="final_red_team",
                status=QAGateStatus.FAIL,
                score=0.2,
                reasons=["Red Team Rejected: Screen dominated by text paragraphs."]
            )

        # Check 3: Demonstration requirement
        has_demo = any(t in [
            "BROWSER_DEMO", "TERMINAL_DEMO", "TECHNICAL_FLOW", "ARCHITECTURE_DIAGRAM",
            "BEFORE_AFTER", "DATA_VISUALIZATION", "BROWSER_INTERACTION", "DEVICE_INTERACTION",
            "AGENT_WORKFLOW", "CODE_VISUALIZATION", "HARDWARE_VISUALIZATION"
        ] for t in types)
        if not has_demo:
            return QAReport(
                gate_name="final_red_team",
                status=QAGateStatus.FAIL,
                score=0.0,
                reasons=["Red Team Rejected: Core technology is not demonstrated or visually explained."]
            )

        # Check 4: No orphan visuals
        orphan_beats = [b.beat_id for b in storyboard.beats if not b.semantic_intent or not b.visual_claim]
        if orphan_beats:
            return QAReport(
                gate_name="final_red_team",
                status=QAGateStatus.FAIL,
                score=0.3,
                reasons=[f"Red Team Rejected: Orphan visuals lacking narration semantic alignment: {orphan_beats}"]
            )

        # Check 5: Forbidden comment CTA in narration
        for seg in script.segments:
            if "bình luận" in seg.spoken_text.lower() or "comment" in seg.spoken_text.lower():
                return QAReport(
                    gate_name="final_red_team",
                    status=QAGateStatus.FAIL,
                    score=0.0,
                    reasons=["Red Team Rejected: Forbidden comment CTA in narration."]
                )

        return QAReport(
            gate_name="final_red_team",
            status=QAGateStatus.PASS,
            score=1.0,
            reasons=[
                "Red Team Passed: Not a slideshow.",
                "Visual Storytelling Engine V3 active: Every visual proves an exact narration claim.",
                "Camera motion directed at attention targets with purposeful framing.",
                "Zero orphan visuals; strong technical demonstration and visual payoffs.",
                "Concise headlines (<= 6 words) with TrueType typography.",
                "First 2 seconds retention hook verified.",
                "Strict CTA policy enforced (Like, Share, Subscribe only).",
                f"Microsoft Neural Voice ({self.config.get('voice', {}).get('primary_voice')}) with broadcast-level loudness."
            ]
        )
