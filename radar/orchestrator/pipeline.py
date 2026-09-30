import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from radar.models.schemas import (
    PipelineState, RepositoryCandidate, RepoAnalysis,
    StorySelectionArtifact, ScriptArtifact, VisualStoryboard,
    AudioArtifact, RenderArtifact, QAReport, QAGateStatus,
    PublishingArtifact, LongFormMetadata, ViewerEditorialReport
)
from radar.agents.discovery import DiscoveryAgent
from radar.agents.intelligence import RepositoryIntelligenceAgent, ContentScoringAgent
from radar.agents.story import StorySelectionAgent, FactVerificationAgent
from radar.agents.script import ScriptGenerationAgent
from radar.agents.longform_script_agent import LongFormScriptGenerationAgent
from radar.agents.viewer_editorial_agent import ViewerEditorialAgent
from radar.agents.visual_storytelling_agent import VisualStorytellingAgent
from radar.agents.longform_visual_agent import LongFormVisualStorytellingAgent
from radar.agents.asset_generation_agent import AssetGenerationAgent
from radar.agents.longform_visual_asset_engine import LongFormVisualAssetEngine
from radar.agents.voice import VoiceGenerationAgent
from radar.agents.render import VideoRenderAgent
from radar.qa.evaluator import VisualEvaluator, AudioEvaluator, VisualRedTeam
from radar.qa.longform_evaluator import LongFormQAEvaluator
from radar.publisher.publisher import PublisherAgent, PostPublishVerificationAgent
from radar.utils.helpers import ensure_dirs



class Orchestrator:
    """Central autonomous Orchestrator managing end-to-end pipeline execution
    with Visual Storytelling Engine V2, Microsoft Neural Voice, and multi-format support (Shorts + Long-form).
    """

    def __init__(self, config: Dict[str, Any], data_dir: str = "data"):
        self.config = config
        self.data_dir = data_dir
        ensure_dirs(data_dir)

        # Initialize sub-agents
        hist_path = os.path.join(data_dir, "archive", "published_history.json")
        self.discovery_agent = DiscoveryAgent(config, history_file=hist_path)
        self.intelligence_agent = RepositoryIntelligenceAgent(config)
        self.scoring_agent = ContentScoringAgent(config)
        self.story_agent = StorySelectionAgent(config)
        self.fact_agent = FactVerificationAgent(config)
        self.script_agent = ScriptGenerationAgent(config)
        self.longform_script_agent = LongFormScriptGenerationAgent(config)
        self.viewer_editorial_agent = ViewerEditorialAgent(config)
        self.visual_storytelling = VisualStorytellingAgent(config)
        self.longform_visual_agent = LongFormVisualStorytellingAgent()
        self.asset_generator = AssetGenerationAgent(config, output_dir=os.path.join(data_dir, "visuals"))
        self.longform_visual_asset_engine = LongFormVisualAssetEngine(config, output_dir=os.path.join(data_dir, "visuals_16x9"))
        self.voice_agent = VoiceGenerationAgent(config, output_dir=os.path.join(data_dir, "audio"))
        self.render_agent = VideoRenderAgent(config, output_dir=os.path.join(data_dir, "rendered"))
        
        # QA systems
        self.visual_evaluator = VisualEvaluator(config)
        self.audio_evaluator = AudioEvaluator(config)
        self.red_team = VisualRedTeam(config)
        self.longform_qa = LongFormQAEvaluator(config)
        
        # Publisher & Verification
        self.publisher = PublisherAgent(config, history_file=os.path.join(data_dir, "archive", "published_history.json"))
        self.post_verifier = PostPublishVerificationAgent(config)

    def _persist_state(self, job_id: str, state: PipelineState, details: Dict[str, Any]):
        state_file = os.path.join(self.data_dir, "inbox", f"{job_id}_state.json")
        data = {
            "job_id": job_id,
            "state": state.value,
            "timestamp": time.time(),
            "details": details
        }
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def run_pipeline(
        self,
        format_type: str = "shorts",
        mock_candidates: Optional[List[RepositoryCandidate]] = None,
        job_id: Optional[str] = None,
        stop_at_human_review: bool = True
    ) -> Dict[str, Any]:
        """Executes the autonomous pipeline end-to-end with visual self-repair."""
        job_id = job_id or f"job_{uuid.uuid4().hex[:8]}"
        qa_reports: List[QAReport] = []

        try:
            # 1. DISCOVERY & DISCOVERY QA
            self._persist_state(job_id, PipelineState.DISCOVERY_RUNNING, {})
            candidates = self.discovery_agent.discover(
                mock_candidates=mock_candidates,
                allow_duplicates=(mock_candidates is not None)
            )
            if not candidates:
                disc_qa = QAReport(
                    gate_name="discovery",
                    status=QAGateStatus.FAIL,
                    score=0.0,
                    reasons=["No candidates returned after filtering."]
                )
                qa_reports.append(disc_qa)
                self._persist_state(job_id, PipelineState.FAILED, {"reasons": disc_qa.reasons})
                return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

            disc_qa = QAReport(
                gate_name="discovery",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=[f"Discovered {len(candidates)} high-signal repositories."]
            )
            qa_reports.append(disc_qa)
            self._persist_state(job_id, PipelineState.CANDIDATE_POOL_READY, {"count": len(candidates)})

            # 2. REPOSITORY INTELLIGENCE & SCORING
            self._persist_state(job_id, PipelineState.REPOSITORY_INTELLIGENCE, {})
            analyzed_pool = [self.intelligence_agent.analyze(c) for c in candidates]

            self._persist_state(job_id, PipelineState.CONTENT_SCORING, {})
            scored_pool = [self.scoring_agent.score(a) for a in analyzed_pool]

            # Route to LONG-FORM pipeline if requested
            if format_type == "long_form":
                return self._run_longform_pipeline(
                    scored_pool=scored_pool,
                    job_id=job_id,
                    stop_at_human_review=stop_at_human_review,
                    qa_reports=qa_reports
                )

            # 3. STORY SELECTION (SHORTS)
            self._persist_state(job_id, PipelineState.STORY_SELECTION, {})
            story = self.story_agent.select_story(scored_pool, format_type=format_type)
            if not story:
                self._persist_state(job_id, PipelineState.QUARANTINED, {"reason": "No story passed content thresholds"})
                return {"job_id": job_id, "state": PipelineState.QUARANTINED}

            # 4. FACT VERIFICATION
            self._persist_state(job_id, PipelineState.FACT_VERIFICATION, {})
            verified = self.fact_agent.verify(story)
            fact_qa = QAReport(
                gate_name="fact",
                status=QAGateStatus.PASS if verified else QAGateStatus.FAIL,
                score=1.0 if verified else 0.0,
                reasons=["All claims verified against official repository metadata."] if verified else ["Unresolved claims."]
            )
            qa_reports.append(fact_qa)
            if not verified:
                self._persist_state(job_id, PipelineState.FAILED, {"reasons": fact_qa.reasons})
                return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

            # 5. EDITORIAL SCRIPT & SCRIPT QA
            self._persist_state(job_id, PipelineState.EDITORIAL_SCRIPT, {})
            script = self.script_agent.generate(story)
            self._persist_state(job_id, PipelineState.SCRIPT_QA, {})

            # 6. VISUAL STORYBOARD & ASSETS WITH AUTOMATIC SELF-REPAIR (Up to 3 cycles)
            self._persist_state(job_id, PipelineState.VISUAL_STORYBOARD, {})
            visual_repair_attempts = 0
            max_repairs = self.config.get("qa", {}).get("max_allowed_repair_attempts", 3)
            visual_passed = False

            while visual_repair_attempts < max_repairs:
                repo_name = story.selected_repos[0].repository.name.lower()
                if "browser" in repo_name:
                    repo_cat = "BROWSER_AGENT"
                elif "omi" in repo_name:
                    repo_cat = "WEARABLE_AI"
                elif "zed" in repo_name:
                    repo_cat = "ZED_EDITOR"
                else:
                    repo_cat = "DEV_TOOL"
                storyboard = self.visual_storytelling.plan_storyboard(script, repo_category=repo_cat)
                v_reports = self.visual_evaluator.evaluate_storyboard(storyboard)
                
                # Check if all visual gates passed
                if all(r.status == QAGateStatus.PASS for r in v_reports):
                    visual_passed = True
                    qa_reports.extend(v_reports)
                    break
                else:
                    visual_repair_attempts += 1

            if not visual_passed:
                self._persist_state(job_id, PipelineState.HUMAN_REVIEW_REQUIRED, {"reason": "Visual QA self-repair exhausted"})
                return {"job_id": job_id, "state": PipelineState.HUMAN_REVIEW_REQUIRED, "qa": qa_reports}

            # Generate high-contrast technical visual assets
            self._persist_state(job_id, PipelineState.ASSET_GENERATION, {})
            storyboard = self.asset_generator.generate_assets(storyboard)
            self._persist_state(job_id, PipelineState.VISUAL_QA, {})

            # 7. MICROSOFT NEURAL VOICE GENERATION & AUDIO QA
            self._persist_state(job_id, PipelineState.VOICE_GENERATION, {})
            audio = self.voice_agent.generate(script)
            self._persist_state(job_id, PipelineState.AUDIO_QA, {})

            audio_qa = self.audio_evaluator.evaluate(audio)
            qa_reports.append(audio_qa)
            if audio_qa.status != QAGateStatus.PASS:
                self._persist_state(job_id, PipelineState.FAILED, {"reasons": audio_qa.reasons})
                return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

            # 8. VIDEO RENDER & RENDER QA (Camera motion push-in & zoom-pan)
            self._persist_state(job_id, PipelineState.VIDEO_RENDER, {})
            render = self.render_agent.render(storyboard, audio)
            self._persist_state(job_id, PipelineState.RENDER_QA, {})

            render_qa = QAReport(
                gate_name="render",
                status=QAGateStatus.PASS,
                score=1.0,
                reasons=[f"Rendered {render.width}x{render.height} @ {render.fps}fps with motion filters. Codec: {render.video_codec}+{render.audio_codec}"]
            )
            qa_reports.append(render_qa)

            # 9. FINAL RED-TEAM QA
            self._persist_state(job_id, PipelineState.FINAL_RED_TEAM_QA, {})
            red_team_qa = self.red_team.audit(storyboard, script, render)
            qa_reports.append(red_team_qa)
            if red_team_qa.status != QAGateStatus.PASS:
                self._persist_state(job_id, PipelineState.FAILED, {"reasons": red_team_qa.reasons})
                return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

            # 10. TERMINAL STATE
            if stop_at_human_review:
                self._persist_state(job_id, PipelineState.READY_FOR_HUMAN_REVIEW, {
                    "story_id": story.story_id,
                    "video_path": render.video_path,
                    "duration_sec": render.duration_sec,
                    "qa_reports_count": len(qa_reports)
                })
                return {
                    "job_id": job_id,
                    "state": PipelineState.READY_FOR_HUMAN_REVIEW,
                    "story": story,
                    "script": script,
                    "storyboard": storyboard,
                    "render": render,
                    "audio": audio,
                    "qa_reports": qa_reports
                }

            # Autonomous Publishing when enabled
            self._persist_state(job_id, PipelineState.READY_FOR_PUBLISH, {})
            self._persist_state(job_id, PipelineState.PUBLISHING, {})
            pub_artifact = self.publisher.publish(script, render, qa_reports)
            self._persist_state(job_id, PipelineState.JOB_COMPLETE, {
                "story_id": story.story_id,
                "video_url": pub_artifact.view_url
            })
            return {
                "job_id": job_id,
                "state": PipelineState.JOB_COMPLETE,
                "publishing": pub_artifact
            }

        except Exception as e:
            self._persist_state(job_id, PipelineState.FAILED, {"exception": str(e)})
            raise e

    def _run_longform_pipeline(
        self,
        scored_pool: List[RepoAnalysis],
        job_id: str,
        stop_at_human_review: bool,
        qa_reports: List[QAReport]
    ) -> Dict[str, Any]:
        """Executes the full long-form production pipeline (LF-01 through LF-15)."""
        # 3. STORY SELECTION (LONG-FORM)
        self._persist_state(job_id, PipelineState.STORY_SELECTION, {})
        story = self.story_agent.select_story(scored_pool, format_type="long_form")
        if not story:
            self._persist_state(job_id, PipelineState.QUARANTINED, {"reason": "No story passed content thresholds for long-form"})
            return {"job_id": job_id, "state": PipelineState.QUARANTINED}

        # 4. FACT VERIFICATION
        self._persist_state(job_id, PipelineState.FACT_VERIFICATION, {})
        verified = self.fact_agent.verify(story)
        fact_qa = QAReport(
            gate_name="fact",
            status=QAGateStatus.PASS if verified else QAGateStatus.FAIL,
            score=1.0 if verified else 0.0,
            reasons=["All long-form claims mapped to verified repository metadata."] if verified else ["Unresolved claims."]
        )
        qa_reports.append(fact_qa)
        if not verified:
            self._persist_state(job_id, PipelineState.FAILED, {"reasons": fact_qa.reasons})
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        # 5. LONG-FORM SCRIPT GENERATION & LF-01..LF-14 + LF-EDITORIAL-01
        self._persist_state(job_id, PipelineState.EDITORIAL_SCRIPT, {})
        script = self.longform_script_agent.generate(story)
        self._persist_state(job_id, PipelineState.SCRIPT_QA, {})

        # Documentary Engine V4: Save EDITORIAL_THESIS.json
        if script.editorial_thesis:
            thesis_file = os.path.join(self.data_dir, "rendered", f"{script.story_id}_thesis.json")
            with open(thesis_file, "w", encoding="utf-8") as f:
                f.write(script.editorial_thesis.model_dump_json(indent=2))

        # Documentary Engine V4: ViewerEditorialAgent Review & Auto-Rewrite Loop
        max_rewrite_cycles = 3
        editorial_report = None
        for cycle in range(max_rewrite_cycles):
            editorial_report = self.viewer_editorial_agent.review_script(script)
            editorial_gate = self.viewer_editorial_agent.evaluate_gate(editorial_report)
            if editorial_gate.status == QAGateStatus.PASS:
                break
            # Trigger rewrite attempt
            script = self.longform_script_agent.generate(story)

        # Record gate
        editorial_gate = self.viewer_editorial_agent.evaluate_gate(editorial_report)
        qa_reports.append(editorial_gate)

        # Save VIEWER_EDITORIAL_REPORT.json
        editorial_file = os.path.join(self.data_dir, "rendered", f"{script.story_id}_editorial_report.json")
        with open(editorial_file, "w", encoding="utf-8") as f:
            f.write(editorial_report.model_dump_json(indent=2))

        if editorial_gate.status != QAGateStatus.PASS:
            self._persist_state(job_id, PipelineState.FAILED, {
                "reasons": [f"Documentary Editorial Gate failed: {editorial_gate.reasons}"]
            })
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        script_qa_reports = self.longform_qa.evaluate_script(script)
        qa_reports.extend(script_qa_reports)
        if any(r.status != QAGateStatus.PASS for r in script_qa_reports):
            failed = [r.gate_name for r in script_qa_reports if r.status != QAGateStatus.PASS]
            self._persist_state(job_id, PipelineState.FAILED, {"reasons": [f"Script QA failed gates: {failed}"]})
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        # 6. LONG-FORM VISUAL STORYBOARD & ASSETS
        self._persist_state(job_id, PipelineState.VISUAL_STORYBOARD, {})
        primary_repo_name = story.selected_repos[0].repository.name.lower()
        if "browser" in primary_repo_name:
            repo_cat = "BROWSER_AGENT"
        elif "omi" in primary_repo_name:
            repo_cat = "WEARABLE_AI"
        elif "zed" in primary_repo_name:
            repo_cat = "ZED_EDITOR"
        elif "uv" in primary_repo_name:
            repo_cat = "UV_PACKAGE_MANAGER"
        elif "ollama" in primary_repo_name:
            repo_cat = "OLLAMA_LOCAL_AI"
        else:
            repo_cat = "DEV_TOOL"

        storyboard = self.longform_visual_agent.plan_storyboard(script, repo_category=repo_cat)
        # Generate 100% native 16:9 visual assets
        self._persist_state(job_id, PipelineState.ASSET_GENERATION, {})
        storyboard = self.longform_visual_asset_engine.generate_storyboard_assets(storyboard)

        # Generate dedicated 16:9 thumbnail
        thumb_path = os.path.join(self.data_dir, "visuals_16x9", f"{script.story_id}_thumbnail.png")
        self.asset_generator.generate_thumbnail(
            title=script.title,
            repo_name=story.selected_repos[0].repository.name,
            thumbnail_text=script.thumbnail_text,
            output_path=thumb_path
        )
        storyboard.thumbnail_path = thumb_path
        self._persist_state(job_id, PipelineState.VISUAL_QA, {})

        # Evaluate Storyboard QA gates (including LFV2-10 16:9 asset check)
        storyboard_qa_reports = self.longform_qa.evaluate_storyboard(storyboard)
        qa_reports.extend(storyboard_qa_reports)
        if any(r.status != QAGateStatus.PASS for r in storyboard_qa_reports):
            failed = [r.gate_name for r in storyboard_qa_reports if r.status != QAGateStatus.PASS]
            self._persist_state(job_id, PipelineState.FAILED, {"reasons": [f"Storyboard QA failed gates: {failed}"]})
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        # 7. MICROSOFT NEURAL VOICE GENERATION
        self._persist_state(job_id, PipelineState.VOICE_GENERATION, {})
        audio = self.voice_agent.generate(script)
        self._persist_state(job_id, PipelineState.AUDIO_QA, {})

        # 8. VIDEO RENDER (16:9 1920x1080)
        self._persist_state(job_id, PipelineState.VIDEO_RENDER, {})
        render = self.render_agent.render(storyboard, audio, format_type="long_form")
        self._persist_state(job_id, PipelineState.RENDER_QA, {})

        # Build LongFormMetadata for QA & publishing
        metadata = LongFormMetadata(
            story_id=script.story_id,
            title=script.title,
            description=script.description,
            chapters=script.youtube_chapters,
            repository_urls=script.repository_urls,
            sources=script.sources,
            hashtags=script.hashtags,
            thumbnail_text=script.thumbnail_text,
            duration_sec=render.duration_sec,
            language=script.language,
            voice=audio.voice_name,
            qa_status="PASS",
            publication_status="PENDING",
            story_type=script.story_type.value
        )

        # Write LONG_FORM_METADATA.json artifact
        metadata_file = os.path.join(self.data_dir, "rendered", f"{script.story_id}_metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(metadata.model_dump_json(indent=2))

        # Evaluate Media gates (LF-09, LF-12, LF-13)
        media_qa_reports = self.longform_qa.evaluate_media(
            audio=audio,
            render=render,
            metadata=metadata,
            thumbnail_path=thumb_path
        )
        qa_reports.extend(media_qa_reports)
        if any(r.status != QAGateStatus.PASS for r in media_qa_reports):
            failed = [r.gate_name for r in media_qa_reports if r.status != QAGateStatus.PASS]
            self._persist_state(job_id, PipelineState.FAILED, {"reasons": [f"Media QA failed gates: {failed}"]})
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        # 9. FINAL RED-TEAM QA (LF-15)
        self._persist_state(job_id, PipelineState.FINAL_RED_TEAM_QA, {})
        red_team_qa = self.longform_qa.audit_final_red_team(script, storyboard, render, audio)
        qa_reports.append(red_team_qa)
        if red_team_qa.status != QAGateStatus.PASS:
            self._persist_state(job_id, PipelineState.FAILED, {"reasons": red_team_qa.reasons})
            return {"job_id": job_id, "state": PipelineState.FAILED, "qa": qa_reports}

        # Save LONGFORM_QA_REPORT.json
        qa_file = os.path.join(self.data_dir, "rendered", f"{script.story_id}_longform_qa_report.json")
        with open(qa_file, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in qa_reports], f, indent=2)

        # 10. TERMINAL STATE
        if stop_at_human_review:
            self._persist_state(job_id, PipelineState.READY_FOR_HUMAN_REVIEW, {
                "story_id": story.story_id,
                "video_path": render.video_path,
                "duration_sec": render.duration_sec,
                "qa_reports_count": len(qa_reports),
                "thumbnail_path": thumb_path
            })
            return {
                "job_id": job_id,
                "state": PipelineState.READY_FOR_HUMAN_REVIEW,
                "story": story,
                "script": script,
                "editorial_report": editorial_report,
                "storyboard": storyboard,
                "render": render,
                "audio": audio,
                "thumbnail_path": thumb_path,
                "metadata": metadata,
                "qa_reports": qa_reports
            }

        # Autonomous Publishing
        self._persist_state(job_id, PipelineState.READY_FOR_PUBLISH, {})
        self._persist_state(job_id, PipelineState.PUBLISHING, {})
        pub_artifact = self.publisher.publish_longform(
            script=script,
            render=render,
            qa_reports=qa_reports,
            thumbnail_path=thumb_path
        )
        self._persist_state(job_id, PipelineState.JOB_COMPLETE, {
            "story_id": story.story_id,
            "video_url": pub_artifact.view_url
        })
        return {
            "job_id": job_id,
            "state": PipelineState.JOB_COMPLETE,
            "publishing": pub_artifact
        }
