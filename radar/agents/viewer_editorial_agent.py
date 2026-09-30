"""
Viewer Editorial Agent (Long-Form Documentary Engine V4)
Responsible for ensuring long-form content achieves documentary quality:
- Identifies and evaluates Central Question & Viewer Promise
- Maps narrative arc, curiosity gaps, evidence points, payoff points, and detects filler
- Calculates ViewerValueScore (0–100) across 8 dimensions (Threshold >= 90.0)
- Enforces Explanation Quality >= 12/15 as critical editorial gate
- Enforces EditorialThesis grounding
- Determines editorial decision (PASS / REWRITE / REJECT)
- Enforces Gate LF-EDITORIAL-01
"""
import os
import re
from typing import Dict, Any, List, Tuple
from radar.models.schemas import (
    LongFormScriptArtifact, ViewerEditorialReport, QAReport, QAGateStatus
)


class ViewerEditorialAgent:
    """
    Evaluates technology documentary scripts against viewer retention and value principles.

    V4 Score components (Total: 100):
    1. Central Question (0–15): Clear, investigative, compelling question driving the entire video
    2. Novelty / Non-obviousness (0–15): Not just basic marketing facts, but deep architectural insight
    3. Evidence Grounding (0–15): Claims backed by code, benchmarks, real repos or official sources
    4. Explanation Quality (0–15): Clear mechanisms, progressive disclosure without jargon overload (Must be >= 12.0)
    5. Narrative Momentum & Curiosity (0–15): Transitions connect chapters, curiosity hooks sustained
    6. Visual Storytelling Readiness (0–10): Concrete visual cues, high proof levels, zero abstract walls
    7. Practical Engineering Value (0–10): Viewer learns practical takeaways, trade-offs, architecture
    8. Payoff & Ending Satisfaction (0–5): Conclusive answers given, zero unresolved promises
    """

    PASS_THRESHOLD = 90.0
    MIN_EXPLANATION_QUALITY = 12.0

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def review_script(self, script: LongFormScriptArtifact) -> ViewerEditorialReport:
        """
        Analyze script, evaluate narrative depth, calculate ViewerValueScore,
        and generate a comprehensive VIEWER_EDITORIAL_REPORT.
        """
        # 1. Identify Central Question & Viewer Promise
        central_q = script.central_question.strip()
        if not central_q:
            for seg in script.all_segments[:3]:
                if "?" in seg.spoken_text:
                    central_q = seg.spoken_text
                    break
            if not central_q:
                central_q = f"Làm thế nào {script.title} vận hành và thay đổi kỹ thuật phần mềm?"

        viewer_promise = script.viewer_promise.strip()
        if not viewer_promise:
            viewer_promise = script.description[:120] if script.description else "Hiểu rõ cơ chế kiến trúc nội tại."

        # 2. Extract Curiosity Gaps & Narrative Arc
        curiosity_gaps = []
        narrative_arc = []
        evidence_points = []
        payoff_points = []
        filler_sections = []

        for ch in script.chapters:
            narrative_arc.append(f"[{ch.chapter_label}] {ch.chapter_title}")
            if ch.question:
                curiosity_gaps.append(ch.question)
            elif ch.curiosity_hook:
                curiosity_gaps.append(ch.curiosity_hook)

            # Check evidence
            for seg in ch.segments:
                if seg.supporting_evidence:
                    evidence_points.extend(seg.supporting_evidence)
                if seg.segment_type in ("payoff", "benchmark", "tech_deep_dive"):
                    payoff_points.append(f"{ch.chapter_label}: {seg.headline_text}")

                # Filler detection
                text_lower = seg.spoken_text.lower()
                fluff_phrases = ["như các bạn đã biết", "vô cùng tuyệt vời", "rất là hay", "không thể tin được"]
                for fp in fluff_phrases:
                    if fp in text_lower:
                        filler_sections.append(f"{seg.beat_id}: '{fp}'")

        # 3. Calculate Scores across 8 dimensions
        scores = {}
        reasons = []

        # D1: Central Question & Thesis Grounding (15 pts)
        has_thesis = script.editorial_thesis is not None
        if len(central_q) >= 15 and "?" in central_q and has_thesis:
            scores["central_question"] = 15.0
            reasons.append("Câu hỏi cốt lõi sắc bén, mang tính điều tra kỹ thuật sâu và gắn kết chặt chẽ với Editorial Thesis.")
        elif len(central_q) >= 15 and "?" in central_q:
            scores["central_question"] = 13.5
            reasons.append("Câu hỏi cốt lõi rõ ràng, mang tính điều tra kỹ thuật sâu.")
        elif len(central_q) >= 10:
            scores["central_question"] = 10.0
            reasons.append("Câu hỏi cốt lõi chấp nhận được nhưng cần tăng độ tò mò.")
        else:
            scores["central_question"] = 5.0
            reasons.append("Thiếu câu hỏi cốt lõi sắc bén định hình toàn bộ video.")

        # D2: Novelty & Non-obviousness (15 pts)
        has_deep_dive = any(ch.chapter_number >= 4 for ch in script.chapters)
        has_limitations = any(
            "GIOI HAN" in ch.chapter_title.upper() or "LIMIT" in ch.chapter_title.upper() or "RAO CAN" in ch.chapter_title.upper() or "DANH DOI" in ch.chapter_title.upper()
            for ch in script.chapters
        )
        has_tension = any(bool(ch.tension.strip()) for ch in script.chapters if not ch.is_cta)
        if has_deep_dive and has_limitations and has_tension:
            scores["novelty"] = 15.0
            reasons.append("Nội dung phản biện sắc sảo; phân tích rào cản kỹ thuật, nghịch lý kiến trúc và giới hạn thực tế.")
        elif has_deep_dive and has_limitations:
            scores["novelty"] = 13.5
            reasons.append("Nội dung không hời hợt; phân tích rào cản kỹ thuật và giới hạn thực tế.")
        elif has_deep_dive:
            scores["novelty"] = 11.0
            reasons.append("Có phân tích kỹ thuật nhưng còn thiếu góc nhìn phản biện / giới hạn.")
        else:
            scores["novelty"] = 6.0
            reasons.append("Nội dung chỉ dừng ở mức giới thiệu tính năng bề mặt.")

        # D3: Evidence Grounding (15 pts)
        all_claims = []
        for ch in script.chapters:
            all_claims.extend(ch.key_claims)
        high_proof_count = sum(1 for c in all_claims if getattr(c, "proof_level", 3) <= 2)
        if len(script.repository_urls) > 0 and (len(evidence_points) >= 3 or high_proof_count >= 2):
            scores["evidence"] = 14.5
            reasons.append("Luận điểm kỹ thuật có dẫn chứng repo, mã nguồn và benchmark xác thực.")
        elif len(script.repository_urls) > 0:
            scores["evidence"] = 11.0
            reasons.append("Có liên kết mã nguồn nhưng cần thêm số liệu đo lường cụ thể.")
        else:
            scores["evidence"] = 5.0
            reasons.append("Thiếu cơ sở dữ liệu đối chiếu.")

        # D4: Explanation Quality (15 pts) - V4 Strict Threshold >= 12.0
        word_count = script.total_spoken_words
        has_explanations = sum(1 for ch in script.chapters if bool(ch.explanation.strip()))
        if word_count >= 750 and has_explanations >= 5:
            scores["explanation_quality"] = 15.0
            reasons.append(f"Chất lượng giải thích xuất sắc: {word_count} từ, {has_explanations} chương giải thích cơ chế nội tại.")
        elif word_count >= 600 or (word_count >= 500 and script.target_duration_sec >= 300):
            scores["explanation_quality"] = 13.5
            reasons.append(f"Giải thích mạch lạc, thời lượng và mật độ thông tin cân đối ({word_count} từ).")
        elif word_count >= 400:
            scores["explanation_quality"] = 10.0
            reasons.append("Giải thích súc tích nhưng còn thiếu chiều sâu phân tích kiến trúc.")
        else:
            scores["explanation_quality"] = 6.0
            reasons.append(f"Mật độ giải thích quá ngắn ({word_count} từ) so với chuẩn documentary V4.")

        # D5: Narrative Momentum & Curiosity (15 pts)
        transitions_count = sum(1 for ch in script.chapters if ch.transition_to_next.strip())
        if transitions_count >= len(script.chapters) - 2 and len(script.chapters) >= 7:
            scores["narrative_momentum"] = 15.0
            reasons.append(f"Mạch dẫn chuyển tiếp hoàn hảo: {transitions_count} móc nối mở loop liên tục giữa các chương.")
        elif transitions_count >= len(script.chapters) // 2:
            scores["narrative_momentum"] = 13.0
            reasons.append("Mạch dẫn chuyển tiếp chặt chẽ giữa các chương, giữ chân người xem liên tục.")
        else:
            scores["narrative_momentum"] = 8.0
            reasons.append("Mạch câu chuyện bị đứt quãng giữa các phần.")

        # D6: Visual Storytelling Readiness (10 pts)
        visual_types = set()
        for ch in script.chapters:
            visual_types.update(ch.visual_types)
        proof_targets = sum(1 for ch in script.chapters if bool(ch.visual_proof_target.strip()))
        if len(visual_types) >= 4 and proof_targets >= 5 and any(t in visual_types for t in ["ARCHITECTURE_DIAGRAM", "TECHNICAL_FLOW", "TERMINAL_DEMO", "BROWSER_DEMO"]):
            scores["visual_storytelling"] = 10.0
            reasons.append(f"Trực quan hóa đa dạng cao ({len(visual_types)} paradigm) và có {proof_targets} visual proof targets cụ thể.")
        elif len(visual_types) >= 4:
            scores["visual_storytelling"] = 8.5
            reasons.append("Đa dạng hình ảnh trực quan cao (architecture, terminal, code, flow).")
        else:
            scores["visual_storytelling"] = 5.0
            reasons.append("Hình ảnh trực quan còn đơn điệu, dễ rơi vào bẫy slideshow.")

        # D7: Practical Engineering Value (10 pts)
        has_code_or_demo = any("DEMO" in ch.chapter_title.upper() or "CO CHE" in ch.chapter_title.upper() or "THUC NGHIEM" in ch.chapter_title.upper() or "BENCHMARK" in ch.chapter_title.upper() for ch in script.chapters)
        has_tradeoffs = any(bool(ch.tension.strip()) for ch in script.chapters)
        if has_code_or_demo and has_tradeoffs:
            scores["practical_value"] = 10.0
            reasons.append("Cung cấp giá trị thực hành thực tế cao kèm phân tích đánh đổi kiến trúc.")
        elif has_code_or_demo:
            scores["practical_value"] = 8.0
            reasons.append("Cung cấp giá trị thực hành thực tế cho kỹ sư phần mềm.")
        else:
            scores["practical_value"] = 5.0
            reasons.append("Ít yếu tố thực nghiệm trực tiếp.")

        # D8: Payoff & Ending Satisfaction (5 pts)
        has_payoff = any("KET LUAN" in ch.chapter_title.upper() or "PAYOFF" in ch.chapter_title.upper() or "TUONG LAI" in ch.chapter_title.upper() for ch in script.chapters)
        payoff_resolved = any(bool(ch.payoff.strip()) for ch in script.chapters if "KET LUAN" in ch.chapter_title.upper() or "PAYOFF" in ch.chapter_title.upper())
        if has_payoff and payoff_resolved:
            scores["payoff"] = 5.0
            reasons.append("Phần kết giải quyết trọn vẹn câu hỏi mở đầu và mở ra bài học kiến trúc dài hạn.")
        elif has_payoff:
            scores["payoff"] = 4.0
            reasons.append("Phần kết có giải đáp câu hỏi mở đầu.")
        else:
            scores["payoff"] = 2.0
            reasons.append("Phần kết chưa thực sự giải tỏa hết các hứa hẹn với khán giả.")

        total_score = round(sum(scores.values()), 1)

        # Decision
        expl_qual = scores.get("explanation_quality", 0.0)
        if total_score >= self.PASS_THRESHOLD and expl_qual >= self.MIN_EXPLANATION_QUALITY:
            decision = "PASS"
            rewrite_instructions = None
        elif total_score >= 70.0:
            decision = "REWRITE"
            rewrite_instructions = "Cần tăng mật độ giải thích cơ chế kỹ thuật (>= 12/15) và đào sâu phân tích đánh đổi."
        else:
            decision = "REJECT"
            rewrite_instructions = "Kịch bản thiếu cấu trúc phim tài liệu chuyên sâu V4; cần viết lại hoàn toàn theo khung V4."

        return ViewerEditorialReport(
            story_id=script.story_id,
            central_question=central_q,
            viewer_promise=viewer_promise,
            viewer_value_score=total_score,
            score_breakdown=scores,
            curiosity_gaps=curiosity_gaps,
            narrative_arc=narrative_arc,
            evidence_points=list(set(evidence_points)),
            payoff_points=payoff_points,
            filler_sections=filler_sections,
            decision=decision,
            reasons=reasons,
            rewrite_instructions=rewrite_instructions
        )

    def evaluate_gate(self, report: ViewerEditorialReport) -> QAReport:
        """Evaluate LF-EDITORIAL-01 Gate enforcing V4 thresholds."""
        expl_qual = report.score_breakdown.get("explanation_quality", 0.0)
        passed = (report.viewer_value_score >= self.PASS_THRESHOLD and expl_qual >= self.MIN_EXPLANATION_QUALITY)

        if passed:
            return QAReport(
                gate_name="LF-EDITORIAL-01:VIEWER_EDITORIAL_GATE",
                status=QAGateStatus.PASS,
                score=round(report.viewer_value_score / 100.0, 3),
                reasons=[
                    f"Passed Viewer Editorial Gate V4: ViewerValueScore {report.viewer_value_score:.1f}/100 >= {self.PASS_THRESHOLD}.",
                    f"Explanation Quality: {expl_qual:.1f}/15 >= {self.MIN_EXPLANATION_QUALITY}.",
                    f"Central Question: '{report.central_question}'",
                    f"Viewer Promise: '{report.viewer_promise}'",
                    f"Score Breakdown: {report.score_breakdown}"
                ]
            )
        else:
            reasons = [
                f"Failed Viewer Editorial Gate V4: ViewerValueScore {report.viewer_value_score:.1f}/100 (Threshold {self.PASS_THRESHOLD}) or Explanation Quality {expl_qual:.1f}/15 (Min {self.MIN_EXPLANATION_QUALITY}).",
                f"Rewrite instructions: {report.rewrite_instructions}",
                f"Identified issues: {report.reasons}"
            ]
            return QAReport(
                gate_name="LF-EDITORIAL-01:VIEWER_EDITORIAL_GATE",
                status=QAGateStatus.FAIL,
                score=round(report.viewer_value_score / 100.0, 3),
                reasons=reasons,
                remediation_hint=report.rewrite_instructions
            )
