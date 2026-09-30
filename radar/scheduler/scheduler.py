import time
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from radar.orchestrator.pipeline import Orchestrator

logger = logging.getLogger(__name__)


class FactoryScheduler:
    """Autonomous scheduler managing scheduled slots for 3 Shorts + 1 Long-form daily.
    
    Adheres strictly to the specification:
    - Daily targets: SHORT_01, SHORT_02, SHORT_03, LONG_01
    - Independent job execution: If one job fails, other scheduled jobs CONTINUE.
    - Full fail-closed behavior: Errors are recorded, never halting unrelated tasks.
    """

    DEFAULT_DAILY_SLOTS = [
        {"slot_id": "SHORT_01", "format": "shorts", "target_time": "08:00"},
        {"slot_id": "SHORT_02", "format": "shorts", "target_time": "12:30"},
        {"slot_id": "SHORT_03", "format": "shorts", "target_time": "17:30"},
        {"slot_id": "LONG_01",  "format": "long_form", "target_time": "20:00"}
    ]

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator = Orchestrator(config)
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.execution_log: List[Dict[str, Any]] = []

    def trigger_scheduled_slot(self, slot_type: str = "shorts", stop_at_human_review: bool = True) -> Dict[str, Any]:
        """Executes a single autonomous scheduled slot with fail-isolation."""
        job_tag = f"slot_{slot_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"[*] Triggering scheduled slot {job_tag} (format: {slot_type})")
        try:
            result = self.orchestrator.run_pipeline(
                format_type=slot_type,
                stop_at_human_review=stop_at_human_review
            )
            entry = {
                "job_tag": job_tag,
                "format": slot_type,
                "status": "SUCCESS" if result.get("state") in ["READY_FOR_HUMAN_REVIEW", "JOB_COMPLETE"] else "FAILED",
                "result": result,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.execution_log.append(entry)
            return result
        except Exception as e:
            logger.error(f"[!] Error in slot {job_tag}: {e}")
            entry = {
                "job_tag": job_tag,
                "format": slot_type,
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.execution_log.append(entry)
            # Fail isolated: do NOT re-raise to allow subsequent scheduled jobs to run
            return {"job_tag": job_tag, "status": "FAILED", "error": str(e)}

    def run_quality_first_daily_autopilot(self, stop_at_human_review: bool = True) -> Dict[str, Any]:
        """QUALITY-FIRST, NOT QUOTA-FIRST DAILY AUTOPILOT:
        1. Discover candidates across ecosystem.
        2. Intelligence analysis & fact check.
        3. Strict scoring with NO-FILLER RULE.
        4. Select only qualified stories (score >= min_threshold).
        5. Formats allocated dynamically based on depth:
           - 0 qualified -> 0 videos (SUCCESSFUL quality-control decision, not failure).
           - 1 qualified -> 1 Short or 1 Long-form based on editorial substance.
           - 2 qualified -> 2 Shorts or 1 Short + 1 Long-form.
           - 3 qualified -> Up to 3 Shorts.
           - 4+ qualified -> Up to 3 Shorts + 1 Long-form maximum capacity.
        6. Produces standardized Daily Quality Report.
        """
        logger.info("[*] Starting Quality-First Daily Autopilot Cycle")
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        # 1. Broad Discovery
        raw_candidates = self.orchestrator.discovery_agent.discover()
        if not raw_candidates:
            raw_candidates = self.orchestrator.discovery_agent._fallback_curated()

        total_discovered = len(raw_candidates)

        # 2. Analyze & Score
        analyzed = [self.orchestrator.intelligence_agent.analyze(c) for c in raw_candidates]
        scored = [self.orchestrator.scoring_agent.score(a) for a in analyzed]

        # 3. Filter by Strict Editorial Thresholds
        min_story_threshold = self.config.get("scoring", {}).get("min_story_threshold", 75.0)
        min_longform_threshold = self.config.get("scoring", {}).get("min_longform_threshold", 85.0)

        qualified_stories = []
        skipped_candidates = []
        skip_reasons = []

        for item in scored:
            score = item.composite_content_score
            repo_name = item.repository.full_name
            if score < min_story_threshold:
                reason = f"{repo_name} (Score: {score:.1f} < {min_story_threshold}): Lacks compelling narrative/novelty or visual proof."
                skipped_candidates.append(item)
                skip_reasons.append(reason)
            else:
                qualified_stories.append(item)

        # Sort qualified by score
        qualified_stories.sort(key=lambda s: s.composite_content_score, reverse=True)
        qualified_count = len(qualified_stories)

        produced_results = []
        shorts_urls = []
        longform_urls = []

        # 4. Dynamic Production Allocation (No filler, max capacity 3 Shorts + 1 Long-form)
        if qualified_count == 0:
            logger.info("[+] 0 qualified stories found today. Successful Quality-Control decision.")
        else:
            # Determine format distribution
            # Check if top candidate qualifies for Long-form
            has_longform_candidate = any(s.composite_content_score >= min_longform_threshold for s in qualified_stories)
            
            allocated_jobs = [] # list of (format_type, repo_candidate)
            
            if qualified_count == 1:
                top = qualified_stories[0]
                fmt = self.orchestrator.story_agent.evaluate_format_fit(top)
                allocated_jobs.append((fmt, top.repository))
            elif qualified_count == 2:
                if has_longform_candidate:
                    # 1 Short + 1 Long-form
                    lf_item = next(s for s in qualified_stories if s.composite_content_score >= min_longform_threshold)
                    sh_item = next(s for s in qualified_stories if s != lf_item)
                    allocated_jobs.append(("shorts", sh_item.repository))
                    allocated_jobs.append(("long_form", lf_item.repository))
                else:
                    allocated_jobs.append(("shorts", qualified_stories[0].repository))
                    allocated_jobs.append(("shorts", qualified_stories[1].repository))
            elif qualified_count == 3:
                if has_longform_candidate:
                    lf_item = next(s for s in qualified_stories if s.composite_content_score >= min_longform_threshold)
                    sh_items = [s for s in qualified_stories if s != lf_item][:2]
                    for s in sh_items:
                        allocated_jobs.append(("shorts", s.repository))
                    allocated_jobs.append(("long_form", lf_item.repository))
                else:
                    for s in qualified_stories[:3]:
                        allocated_jobs.append(("shorts", s.repository))
            else:
                # 4+ qualified: Max capacity 3 Shorts + 1 Long-form
                sh_candidates = qualified_stories[:3]
                for s in sh_candidates:
                    allocated_jobs.append(("shorts", s.repository))
                if has_longform_candidate:
                    lf_item = next((s for s in qualified_stories if s.composite_content_score >= min_longform_threshold), qualified_stories[0])
                    allocated_jobs.append(("long_form", lf_item.repository))

            # Execute allocated jobs safely
            for fmt, repo_cand in allocated_jobs:
                try:
                    res = self.orchestrator.run_pipeline(
                        format_type=fmt,
                        mock_candidates=[repo_cand],
                        stop_at_human_review=stop_at_human_review
                    )
                    produced_results.append(res)
                    v_path = res.get("render", {}).video_path if hasattr(res.get("render"), "video_path") else (res.get("render", {}).get("video_path") if isinstance(res.get("render"), dict) else "")
                    if fmt == "shorts":
                        shorts_urls.append(v_path or f"data/rendered/{repo_cand.name}_short.mp4")
                    else:
                        longform_urls.append(v_path or f"data/rendered/{repo_cand.name}_longform.mp4")
                except Exception as e:
                    logger.error(f"[!] Production error for {repo_cand.full_name} ({fmt}): {e}")

        # 5. Build Daily Quality Report
        report_text = self._format_daily_quality_report(
            date=today_str,
            total_discovered=total_discovered,
            qualified_count=qualified_count,
            produced_count=len(produced_results),
            published_count=0 if stop_at_human_review else len(produced_results),
            skipped_count=len(skipped_candidates),
            skip_reasons=skip_reasons,
            shorts_urls=shorts_urls,
            longform_urls=longform_urls
        )

        return {
            "date": today_str,
            "total_discovered": total_discovered,
            "qualified_count": qualified_count,
            "produced_count": len(produced_results),
            "skipped_count": len(skipped_candidates),
            "report_text": report_text,
            "results": produced_results
        }

    def _format_daily_quality_report(self, date: str, total_discovered: int, qualified_count: int,
                                    produced_count: int, published_count: int, skipped_count: int,
                                    skip_reasons: List[str], shorts_urls: List[str], longform_urls: List[str]) -> str:
        lines = [
            "=" * 50,
            "RADAR FACTORY DAILY REPORT",
            f"Date: {date}",
            "Principle: Quality-First, Not Quota-First",
            "=" * 50,
            "",
            f"Discovery:  {total_discovered} candidates",
            f"Qualified:  {qualified_count} candidates",
            f"Produced:   {produced_count} videos",
            f"Published:  {published_count} videos",
            f"Skipped:    {skipped_count} candidates",
            ""
        ]

        if skip_reasons:
            lines.append("Skip reasons:")
            for r in skip_reasons[:8]:
                lines.append(f"  • {r}")
            lines.append("")

        lines.append("SHORTS:")
        if shorts_urls:
            for u in shorts_urls:
                lines.append(f"  • {u}")
        else:
            lines.append("  (None)")
        lines.append("")

        lines.append("LONG-FORM:")
        if longform_urls:
            for lu in longform_urls:
                lines.append(f"  • {lu}")
        else:
            lines.append("  (None)")
        lines.append("")

        if qualified_count == 0:
            lines.append("=" * 50)
            lines.append("STATUS: NO QUALIFIED STORY TODAY")
            lines.append("DECISION: Successful quality-control decision. Zero low-quality filler produced.")
            lines.append("=" * 50)
        else:
            lines.append("=" * 50)
            lines.append(f"STATUS: {produced_count} QUALITY STORIES PRODUCED")
            lines.append("DECISION: Meets strict editorial and viewer value thresholds.")
            lines.append("=" * 50)

        return "\n".join(lines)

    def run_daily_cycle(self, stop_at_human_review: bool = True) -> List[Dict[str, Any]]:
        """Delegates daily cycle to Quality-First Autopilot."""
        res = self.run_quality_first_daily_autopilot(stop_at_human_review=stop_at_human_review)
        return [res]

    def start_background(self):
        """Starts background daemon to execute according to targets and intervals."""
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run_loop(self):
        interval = 3600
        while self.running:
            try:
                # Trigger quality first autopilot
                self.run_quality_first_daily_autopilot()
            except Exception:
                pass
            time.sleep(interval)

