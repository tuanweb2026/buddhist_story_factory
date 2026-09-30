"""
Long-Form Visual Storytelling Agent
Maps LongFormScriptArtifact chapters → LongFormStoryboard.

Each visual beat has:
  - visual_purpose: prove / demonstrate / explain / visualize / evidence / payoff
  - chapter context (chapter_number, chapter_label, is_chapter_opener)
  - full V3 narration alignment fields

Visual pacing: new meaningful visual event every 2–6 seconds.
Chapter openers use CHAPTER_TITLE_CARD visual type.
"""
import uuid
from typing import List
from radar.models.schemas import (
    LongFormScriptArtifact, LongFormStoryboard, LongFormVisualBeat,
    LongFormChapter, LongFormStoryType, ScriptSegment
)


_MOTION_MAP = {
    "REAL_REPOSITORY_UI": "ZOOM_TO_DETAIL",
    "TECHNICAL_FLOW": "DATA_FLOW",
    "BROWSER_DEMO": "ZOOM_TO_DETAIL",
    "TERMINAL_DEMO": "REVEAL",
    "ARCHITECTURE_DIAGRAM": "REVEAL",
    "BEFORE_AFTER": "BEFORE_AFTER_SPLIT",
    "DATA_VISUALIZATION": "PUSH_IN",
    "PAYOFF_VISUAL": "PAYOFF_PUSH",
    "CHAPTER_TITLE_CARD": "PUSH_IN",
    "CTA": "STATIC",
}

_PURPOSE_MAP = {
    "hook": "evidence",
    "problem": "prove",
    "discovery": "demonstrate",
    "how_it_works": "explain",
    "tech_deep_dive": "demonstrate",
    "ai_features": "demonstrate",
    "benchmark": "prove",
    "implications": "visualize",
    "limitations": "prove",
    "payoff": "payoff",
    "cta": "payoff",
    "repo_intro": "evidence",
    "repo_why": "explain",
}


_PROOF_LEVEL_MAP = {
    "REAL_REPOSITORY_UI": 1,
    "BROWSER_DEMO": 2,
    "TERMINAL_DEMO": 2,
    "DATA_VISUALIZATION": 3,
    "TECHNICAL_FLOW": 4,
    "ARCHITECTURE_DIAGRAM": 4,
    "BEFORE_AFTER": 3,
    "PAYOFF_VISUAL": 5,
    "CHAPTER_TITLE_CARD": 5,
    "CTA": 5,
}


class LongFormVisualStorytellingAgent:
    """
    Plans the visual storyboard for a long-form video.

    For each chapter: emits a CHAPTER_TITLE_CARD beat, then one beat
    per script segment. Each beat carries narration alignment metadata.
    """

    def plan_storyboard(
        self,
        script: LongFormScriptArtifact,
        repo_category: str = "DEV_TOOL"
    ) -> LongFormStoryboard:
        beats: List[LongFormVisualBeat] = []
        beat_order = 0
        current_time = 0.0

        for chapter in script.chapters:
            # ── Chapter opener title card ─────────────────────────────────
            if not chapter.is_cta:
                beat_order += 1
                title_card = LongFormVisualBeat(
                    beat_id=f"{script.story_id}_ch{chapter.chapter_number:02d}_TITLE",
                    order=beat_order,
                    start_time=current_time,
                    end_time=current_time + 2.5,
                    duration_sec=2.5,
                    narration="",
                    visual_type="CHAPTER_TITLE_CARD",
                    headline_text=" ".join(chapter.chapter_title.split()[:8]),
                    sub_label=chapter.chapter_label,
                    diagram_elements=[chapter.chapter_title, chapter.chapter_label,
                                      chapter.retention_event[:60] if chapter.retention_event else ""],
                    motion_type="PUSH_IN",
                    semantic_intent=f"Chapter opener: {chapter.chapter_title}",
                    visual_claim=f"Introducing: {chapter.chapter_label}",
                    attention_target="chapter_title",
                    visual_action="reveal_chapter_label",
                    payoff=f"Viewer knows next topic: {chapter.chapter_title}",
                    transition="FADE",
                    evidence_required=False,
                    # LongFormVisualBeat extras
                    chapter_number=chapter.chapter_number,
                    chapter_label=chapter.chapter_label,
                    visual_purpose="explain",
                    proof_level=5,
                    narration_reference="",
                    evidence_reference="",
                    is_chapter_opener=True,
                    narration_claim=f"Chương {chapter.chapter_number}: {chapter.chapter_title}",
                    visual_intent="Introduce chapter inquiry and orient viewer attention",
                    evidence_type="CHAPTER_TITLE_CARD",
                    visual_asset=f"title_card_{chapter.chapter_number:02d}",
                    camera_motion="PUSH_IN",
                    visual_payoff=f"Viewer clearly registers narrative transition to {chapter.chapter_label}",
                    transition_reason="Chapter boundary progression",
                )
                beats.append(title_card)
                current_time += 2.5

            # ── One beat per segment ──────────────────────────────────────
            for seg in chapter.segments:
                beat_order += 1
                v_type = seg.visual_type or "TECHNICAL_FLOW"
                motion = _MOTION_MAP.get(v_type, "PUSH_IN")
                purpose = _PURPOSE_MAP.get(seg.segment_type, "explain")
                proof_lvl = _PROOF_LEVEL_MAP.get(v_type, 3)

                ev_type = (
                    "REAL_REPO_UI" if v_type == "REAL_REPOSITORY_UI"
                    else "BENCHMARK_RESULT" if v_type == "DATA_VISUALIZATION"
                    else "SOURCE_CODE" if v_type == "TERMINAL_DEMO"
                    else "ARCHITECTURE_SCHEMATIC" if v_type == "ARCHITECTURE_DIAGRAM"
                    else "SYSTEM_EXECUTION"
                )

                beat = LongFormVisualBeat(
                    beat_id=f"{script.story_id}_{seg.beat_id}",
                    order=beat_order,
                    start_time=current_time,
                    end_time=current_time + seg.estimated_duration_sec,
                    duration_sec=seg.estimated_duration_sec,
                    narration=seg.spoken_text,
                    visual_type=v_type,
                    headline_text=seg.headline_text,
                    sub_label=seg.visual_cue.replace("_", " ").upper(),
                    diagram_elements=self._derive_elements(seg, script, repo_category),
                    motion_type=motion,
                    semantic_intent=f"{seg.segment_type}: {seg.spoken_text[:80]}",
                    visual_claim=f"Visual proves: {seg.spoken_text[:80]}",
                    attention_target=seg.visual_cue.replace("_", " "),
                    visual_action=f"{motion.lower()}_to_{seg.visual_cue}",
                    payoff=f"Viewer understands: {seg.spoken_text[:60]}",
                    transition="CUT" if seg.segment_type != "cta" else "FADE",
                    evidence_required=(seg.segment_type not in ["cta", "hook"]),
                    # LongFormVisualBeat extras
                    chapter_number=chapter.chapter_number,
                    chapter_label=chapter.chapter_label,
                    visual_purpose=purpose,
                    proof_level=proof_lvl,
                    narration_reference=seg.spoken_text[:100],
                    evidence_reference="; ".join(seg.supporting_evidence[:2]),
                    is_chapter_opener=False,
                    narration_claim=seg.spoken_text,
                    visual_intent=f"Demonstrate and prove: {seg.headline_text}",
                    evidence_type=ev_type,
                    visual_asset=seg.visual_cue,
                    camera_motion=motion,
                    visual_payoff=f"Direct visual evidence confirming: {seg.headline_text}",
                    transition_reason=f"Advancing visual focus to {seg.visual_cue} for narrative continuity",
                )
                beats.append(beat)
                current_time += seg.estimated_duration_sec

        total_dur = current_time

        return LongFormStoryboard(
            story_id=script.story_id,
            beats=beats,
            chapters=script.chapters,
            total_duration_sec=total_dur,
            repo_category=repo_category,
            story_type=script.story_type,
        )

    def _derive_elements(self, seg: ScriptSegment, script: LongFormScriptArtifact,
                         repo_category: str) -> List[str]:
        """Generate diagram_elements from segment context for asset renderer."""
        vt = seg.visual_type.upper() if seg.visual_type else ""
        name = repo_category.lower()

        if vt == "CHAPTER_TITLE_CARD":
            return [seg.headline_text]

        # Pass structured hints based on visual type + repo
        if vt in ("DATA_VISUALIZATION",):
            if "zed" in name or "zed" in seg.beat_id.lower():
                return ["zed", "KHOI DONG", "BENCHMARK", "58K"]
            elif "ollama" in name or "ollama" in seg.beat_id.lower():
                return ["ollama", "TOKEN SPEED", "VRAM COMPRESSION", "181K"]
            return [seg.headline_text]

        if vt == "TECHNICAL_FLOW":
            if "zed" in name:
                return ["ELECTRON APPROACH", "ZED RUST+GPUI", "GPU FRAME BUFFER"]
            elif "ollama" in name:
                return ["GO DAEMON", "LLAMA.CPP C++", "GPU LAYER OFFLOAD"]
            return [seg.headline_text, seg.visual_cue]

        if vt == "BROWSER_DEMO":
            if "zed" in name or "inline" in seg.visual_cue.lower():
                return ["zed", "AI inline", seg.headline_text]
            elif "ollama" in name:
                return ["ollama", "REST API", seg.headline_text]
            return [seg.headline_text]

        if vt == "TERMINAL_DEMO":
            if "zed" in name or "buffer" in seg.visual_cue.lower():
                return ["zed", "buffer", seg.headline_text]
            elif "ollama" in name:
                return ["ollama", "RUN CLI", seg.headline_text]
            return [seg.headline_text]

        if vt == "PAYOFF_VISUAL":
            if "zed" in name:
                return ["zed", "RUST WIN", seg.headline_text]
            elif "browser" in name:
                return ["browser-use", "AI AGENT", seg.headline_text]
            elif "ollama" in name:
                return ["ollama", "LOCAL AI VICTORY", seg.headline_text]
            return [seg.headline_text]

        if vt == "REAL_REPOSITORY_UI":
            if "zed" in name:
                return ["zed", "58K", seg.headline_text]
            elif "browser" in name:
                return ["browser-use", "32K", seg.headline_text]
            elif "ollama" in name:
                return ["ollama", "181K", seg.headline_text]
            return [seg.headline_text]

        return [seg.headline_text, seg.visual_cue, repo_category]
