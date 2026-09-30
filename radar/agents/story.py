import uuid
from typing import List, Dict, Any, Optional
from radar.models.schemas import RepoAnalysis, StorySelectionArtifact, EvidenceType


class StorySelectionAgent:
    """Selects top repository story and determines format based on content strength."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_score = config.get("scoring", {}).get("min_story_threshold", 70.0)
        self.min_longform_score = config.get("scoring", {}).get("min_longform_threshold", 80.0)

    def evaluate_format_fit(self, analysis: RepoAnalysis) -> str:
        """Determines best format (shorts vs long_form) based on editorial substance:
        - Short: Single breakthrough, concise UI demo, fast punchy discovery.
        - Long-form: Deep architecture, competing mechanisms, benchmarks, trade-offs.
        """
        has_deep_architecture = (
            len(analysis.technical_novelty) > 60 or
            any(k in analysis.technical_novelty.lower() for k in ["kiến trúc", "architecture", "offload", "gpui", "compiler", "engine"])
        )
        has_investigative_value = analysis.composite_content_score >= self.min_longform_score
        has_rich_evidence = len(analysis.evidence) >= 4

        if has_deep_architecture and has_investigative_value and has_rich_evidence:
            return "long_form"
        return "shorts"

    def select_story(self, candidates: List[RepoAnalysis], format_type: str = "shorts") -> Optional[StorySelectionArtifact]:
        """NO-FILLER RULE:
        Filter strictly by minimum editorial score.
        If no candidates meet the threshold, return None immediately.
        Do NOT relax thresholds or pick weak filler candidates.
        """
        required_score = self.min_longform_score if format_type == "long_form" else self.min_score
        qualified = [c for c in candidates if c.composite_content_score >= required_score]

        if not qualified:
            # NO-FILLER: SKIP > LOW-QUALITY VIDEO
            return None

        # Sort descending by composite content score
        qualified.sort(key=lambda x: x.composite_content_score, reverse=True)
        top_repo = qualified[0]

        story_id = f"story_{uuid.uuid4().hex[:10]}"
        if format_type == "long_form" and len(qualified) >= 3:
            selected_repos = qualified[:min(6, len(qualified))]
            format_subtype = "multi_repo"
        else:
            selected_repos = [top_repo]
            format_subtype = "single_repo"

        repo_name = top_repo.repository.name
        stars_k = round(top_repo.repository.stars / 1000, 1)
        stars_display = f"{stars_k}k" if stars_k >= 1 else f"{top_repo.repository.stars}"

        # Natural Vietnamese hook formulation
        if top_repo.novelty_score >= 90.0:
            core_hook_angle = f"Tại sao cả cộng đồng lập trình đang phát sốt vì {repo_name}?"
            narrative_thesis = f"{repo_name} đại diện cho bước chuyển giao ngoạn mục: biến AI từ người trò chuyện thành người trực tiếp giải quyết vấn đề."
        else:
            core_hook_angle = f"Dự án mã nguồn mở cực kỳ đáng chú ý: {repo_name}"
            narrative_thesis = f"{repo_name} mang lại bước đột phá lớn về năng suất cho giới phát triển phần mềm."

        return StorySelectionArtifact(
            story_id=story_id,
            format=format_type,
            selected_repos=selected_repos,
            format_type=format_subtype,
            core_hook_angle=core_hook_angle,
            narrative_thesis=narrative_thesis
        )


class FactVerificationAgent:
    """Verifies factual claims against references and blocks unsupported hype."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def verify(self, story: StorySelectionArtifact) -> bool:
        """Ensures every critical claim has grounded evidence and no unresolvable conflicts."""
        for repo_analysis in story.selected_repos:
            if not repo_analysis.evidence:
                return False
            
            # Check verified fact ratio
            verified_count = sum(1 for e in repo_analysis.evidence if e.verified)
            if verified_count == 0:
                return False

            # Check for unresolved conflicts
            for ev in repo_analysis.evidence:
                if ev.conflict_notes and not ev.verified:
                    return False

        return True
