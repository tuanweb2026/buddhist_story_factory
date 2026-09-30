from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PipelineState(str, Enum):
    INITIALIZED = "INITIALIZED"
    DISCOVERY_RUNNING = "DISCOVERY_RUNNING"
    DISCOVERY_QA = "DISCOVERY_QA"
    CANDIDATE_POOL_READY = "CANDIDATE_POOL_READY"
    REPOSITORY_INTELLIGENCE = "REPOSITORY_INTELLIGENCE"
    CONTENT_SCORING = "CONTENT_SCORING"
    STORY_SELECTION = "STORY_SELECTION"
    FACT_VERIFICATION = "FACT_VERIFICATION"
    EDITORIAL_SCRIPT = "EDITORIAL_SCRIPT"
    SCRIPT_QA = "SCRIPT_QA"
    VISUAL_STORYBOARD = "VISUAL_STORYBOARD"
    ASSET_GENERATION = "ASSET_GENERATION"
    VISUAL_QA = "VISUAL_QA"
    VOICE_BENCHMARK = "VOICE_BENCHMARK"
    VOICE_GENERATION = "VOICE_GENERATION"
    AUDIO_QA = "AUDIO_QA"
    VIDEO_RENDER = "VIDEO_RENDER"
    RENDER_QA = "RENDER_QA"
    FINAL_RED_TEAM_QA = "FINAL_RED_TEAM_QA"
    READY_FOR_HUMAN_REVIEW = "READY_FOR_HUMAN_REVIEW"
    READY_FOR_PUBLISH = "READY_FOR_PUBLISH"
    PUBLISHING = "PUBLISHING"
    POST_PUBLISH_VERIFICATION = "POST_PUBLISH_VERIFICATION"
    PUBLISHED = "PUBLISHED"
    JOB_COMPLETE = "JOB_COMPLETE"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    FAILED = "FAILED"
    QUARANTINED = "QUARANTINED"


class EvidenceType(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"
    DOCUMENTATION_CLAIM = "DOCUMENTATION_CLAIM"
    COMMUNITY_SIGNAL = "COMMUNITY_SIGNAL"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    EDITORIAL_INTERPRETATION = "EDITORIAL_INTERPRETATION"


class QAGateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    MISSING = "MISSING"
    UNRESOLVED = "UNRESOLVED"
    EXPIRED = "EXPIRED"
    CONFLICT = "CONFLICT"


class EvidenceItem(BaseModel):
    statement: str
    evidence_type: EvidenceType
    source_url: Optional[str] = None
    source_ref: str
    verified: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    conflict_notes: Optional[str] = None


class RepositoryCandidate(BaseModel):
    full_name: str
    owner: str
    name: str
    html_url: str
    description: Optional[str] = ""
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    language: Optional[str] = "Unknown"
    created_at: Optional[str] = None
    pushed_at: Optional[str] = None
    stars_today: Optional[int] = 0
    topics: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    readme_sample: Optional[str] = None
    recent_commits_count: int = 0


class RepoAnalysis(BaseModel):
    repository: RepositoryCandidate
    what_it_is: str
    unusual_capability: str
    technical_novelty: str
    why_care: str
    takeaway: str
    star_momentum_score: float = 0.0
    novelty_score: float = 0.0
    visual_potential_score: float = 0.0
    curiosity_score: float = 0.0
    explanation_simplicity_score: float = 0.0
    composite_content_score: float = 0.0
    evidence: List[EvidenceItem] = Field(default_factory=list)


class StorySelectionArtifact(BaseModel):
    story_id: str
    format: str  # "shorts" or "long_form"
    selected_repos: List[RepoAnalysis]
    format_type: str  # single_repo, comparison, list, trend
    core_hook_angle: str
    narrative_thesis: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ScriptSegment(BaseModel):
    order: int
    beat_id: str
    segment_type: str  # hook, what_is_it, how_it_works, browser_interaction, tech_closeup, why_care, payoff, cta
    spoken_text: str
    estimated_duration_sec: float
    visual_type: str  # STAR_COUNT_HOOK, REPOSITORY_HOOK, BROWSER_INTERACTION, AGENT_WORKFLOW, CODE_VISUALIZATION, SYSTEM_DIAGRAM, RESULT_PAYOFF, CTA
    motion_type: str  # PUSH_IN, CURSOR_CLICK_SEQUENCE, DATA_FLOW, PROGRESSIVE_REVEAL, ZOOM_PAN, PAYOFF_REVEAL
    visual_cue: str
    headline_text: str  # Maximum <= 6 words
    supporting_evidence: List[str] = Field(default_factory=list)


class ScriptArtifact(BaseModel):
    story_id: str
    format: str
    language: str = "vi"
    title: str
    description: str
    tags: List[str]
    hook: str
    target_duration_sec: float
    total_spoken_words: int
    segments: List[ScriptSegment]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class VisualBeatEvent(BaseModel):
    beat_id: str
    order: int
    start_time: float
    end_time: float
    duration_sec: float
    narration: str
    visual_type: str  # REAL_REPOSITORY_UI, TECHNICAL_FLOW, BROWSER_DEMO, TERMINAL_DEMO, ARCHITECTURE_DIAGRAM, BEFORE_AFTER, DATA_VISUALIZATION, CONCEPTUAL_AI_VISUAL, PAYOFF_VISUAL, CTA
    headline_text: str  # <= 6 words
    sub_label: str
    diagram_elements: List[str] = Field(default_factory=list)
    motion_type: str  # PUSH_IN, ZOOM_TO_DETAIL, PAN_LEFT_TO_RIGHT, DATA_FLOW, REVEAL, BEFORE_AFTER_SPLIT, PAYOFF_PUSH, STATIC
    semantic_intent: str = ""
    visual_claim: str = ""
    attention_target: str = ""
    visual_action: str = ""
    payoff: str = ""
    transition: str = ""
    evidence_required: bool = True
    asset_path: Optional[str] = None
    is_synthetic: bool = True
    synthetic_notice: str = "MINH HỌA KHÁI NIỆM • GITHUB PROJECT RADAR"
    source_attribution: Optional[str] = None


class VisualStoryboard(BaseModel):
    story_id: str
    beats: List[VisualBeatEvent]
    total_duration_sec: float
    repo_category: str
    rendered_assets: List[str] = Field(default_factory=list)


class AudioArtifact(BaseModel):
    story_id: str
    audio_path: str
    duration_sec: float
    sample_rate: int
    channels: int
    lufs: float
    true_peak_db: float
    voice_name: str
    provider: str
    is_clipping: bool = False


class RenderArtifact(BaseModel):
    story_id: str
    video_path: str
    width: int
    height: int
    fps: int
    duration_sec: float
    video_codec: str
    audio_codec: str
    file_size_bytes: int


class QAReport(BaseModel):
    gate_name: str
    status: QAGateStatus
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    remediation_hint: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PublishingArtifact(BaseModel):
    story_id: str
    video_id: str
    platform: str = "youtube"
    publish_time: str
    privacy_status: str
    title: str
    view_url: str
    status: str
    channel_name: str = "@lido AI LAB"
    channel_id: str = "@lido_ai_lab"
    scheduled_publish_time: Optional[str] = None
    studio_edit_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ─── LONG-FORM MODE SCHEMAS ────────────────────────────────────────────────────

class LongFormStoryType(str, Enum):
    TYPE_A_SINGLE_REPO = "TYPE_A_SINGLE_REPO"          # Deep dive: one repository
    TYPE_B_MULTI_REPO = "TYPE_B_MULTI_REPO"            # Theme: multiple repositories
    TYPE_C_TECH_EXPLAINER = "TYPE_C_TECH_EXPLAINER"    # Technology topic, repos as evidence
    TYPE_D_TREND_REPORT = "TYPE_D_TREND_REPORT"        # Ecosystem / trend analysis


class ClaimClassification(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    INTERPRETATION = "INTERPRETATION"
    OPINION = "OPINION"
    OFFICIAL_SOURCE = "OFFICIAL_SOURCE"
    DIRECT_MEASUREMENT = "DIRECT_MEASUREMENT"
    FACTORY_MEASUREMENT = "FACTORY_MEASUREMENT"
    THIRD_PARTY_BENCHMARK = "THIRD_PARTY_BENCHMARK"
    DOCUMENTED_CLAIM = "DOCUMENTED_CLAIM"
    UNVERIFIED = "UNVERIFIED"


class LongFormClaim(BaseModel):
    """A classified factual claim within long-form content."""
    claim_text: str
    classification: ClaimClassification
    source_url: Optional[str] = None
    source_ref: str = ""
    verified: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    proof_level: int = Field(default=3, ge=1, le=5)  # 1: Code/Repo, 2: Terminal/Live, 3: Benchmark, 4: Architecture, 5: Concept


class EditorialThesis(BaseModel):
    """Deep editorial reasoning artifact created before script generation."""
    story_id: str
    editorial_thesis: str
    central_question: str
    viewer_promise: str
    why_this_matters: str
    key_tension: str
    surprising_insight: str
    technical_breakthrough: str
    real_world_implication: str
    trade_off: str
    limitation: str
    final_payoff: str
    target_audience: str = "Software Engineers, Tech Leads, AI Researchers"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LongFormChapter(BaseModel):
    """One chapter in a long-form video script."""
    chapter_number: int
    chapter_title: str                        # e.g. "THE PROBLEM"
    chapter_label: str                        # e.g. "CHAPTER 02"
    start_time_sec: float
    end_time_sec: float
    duration_sec: float
    spoken_text: str
    question: str = ""                        # Chapter-level inquiry
    curiosity_hook: str = ""                  # Curiosity gap for this chapter
    tension: str = ""                         # Conflict, tension, or paradox explored
    explanation: str = ""                     # Core mechanism or technical explanation delivered
    visual_proof_target: str = ""             # The concrete visual proof shown in this chapter
    payoff: str = ""                          # The takeaway or resolution for the viewer
    transition_to_next: str = ""              # Forward narrative momentum / open loop to chapter N+1
    segments: List[ScriptSegment] = Field(default_factory=list)
    key_claims: List[LongFormClaim] = Field(default_factory=list)
    visual_types: List[str] = Field(default_factory=list)
    retention_event: str = ""                 # New information introduced in this chapter
    is_cta: bool = False


class ViewerEditorialReport(BaseModel):
    """Report from ViewerEditorialAgent assessing documentary value."""
    story_id: str
    central_question: str
    viewer_promise: str
    viewer_value_score: float = Field(ge=0.0, le=100.0)
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    curiosity_gaps: List[str] = Field(default_factory=list)
    narrative_arc: List[str] = Field(default_factory=list)
    evidence_points: List[str] = Field(default_factory=list)
    payoff_points: List[str] = Field(default_factory=list)
    filler_sections: List[str] = Field(default_factory=list)
    decision: str = "PASS"                    # PASS, REWRITE, REJECT
    reasons: List[str] = Field(default_factory=list)
    rewrite_instructions: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LongFormScriptArtifact(BaseModel):
    """Full long-form video script artifact."""
    story_id: str
    format: str = "long_form"
    story_type: LongFormStoryType
    language: str = "vi"
    title: str
    description: str
    central_question: str = ""                # Core investigative question driving documentary
    viewer_promise: str = ""                  # Clear knowledge payoff guaranteed to the viewer
    editorial_thesis: Optional[EditorialThesis] = None
    tags: List[str] = Field(default_factory=list)
    hook: str
    target_duration_sec: float               # 300–480 (5–8 min)
    total_spoken_words: int
    chapters: List[LongFormChapter]
    all_segments: List[ScriptSegment] = Field(default_factory=list)
    repository_urls: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    thumbnail_text: str = ""                 # 2–6 words for thumbnail
    youtube_chapters: List[str] = Field(default_factory=list)  # ["00:00 Hook", ...]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LongFormVisualBeat(VisualBeatEvent):
    """Extended visual beat for long-form: adds chapter context."""
    chapter_number: int = 0
    chapter_label: str = ""
    visual_purpose: str = ""                 # prove / demonstrate / explain / visualize / evidence / payoff
    proof_level: int = 3                     # Level 1 (Code/UI), 2 (Live Demo), 3 (Benchmark), 4 (Arch), 5 (Concept)
    narration_claim: str = ""                # The exact major claim made in narration
    visual_intent: str = ""                  # The specific goal of this visual (prove, demonstrate, contrast)
    evidence_type: str = ""                  # REAL_REPO_UI, SOURCE_CODE, BENCHMARK_RESULT, etc.
    visual_asset: str = ""                   # Identifier or path of the asset
    attention_target: str = ""               # Specific coordinate / element where viewer looks
    camera_motion: str = ""                  # Purposeful camera movement
    visual_payoff: str = ""                  # What the viewer visually verifies
    transition_reason: str = ""              # Why the camera/scene cuts or shifts
    narration_reference: str = ""
    evidence_reference: str = ""
    is_chapter_opener: bool = False



class LongFormStoryboard(BaseModel):
    """Full storyboard for a long-form video."""
    story_id: str
    beats: List[LongFormVisualBeat]
    chapters: List[LongFormChapter]
    total_duration_sec: float
    repo_category: str
    story_type: LongFormStoryType
    rendered_assets: List[str] = Field(default_factory=list)
    thumbnail_path: Optional[str] = None


class LongFormMetadata(BaseModel):
    """Complete metadata package for long-form publication."""
    story_id: str
    title: str
    description: str
    chapters: List[str]                      # YouTube chapter format: ["00:00 Hook", ...]
    repository_urls: List[str]
    sources: List[str]
    hashtags: List[str]
    thumbnail_text: str
    duration_sec: float
    language: str = "vi"
    voice: str = "vi-VN-HoaiMyNeural"
    qa_status: str = "PASS"
    publication_status: str = "PENDING"
    story_type: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PublicationHistoryEntry(BaseModel):
    """Cross-day deduplication record."""
    story_id: str
    repository_full_name: str
    story_angle: str
    publication_date: str
    format: str                              # "shorts" or "long_form"
    title: str
    content_hash: str
    video_id: Optional[str] = None
    view_url: Optional[str] = None


class DailyQualityReport(BaseModel):
    """Quality-First Daily Autopilot Report Schema."""
    date: str
    total_discovered: int
    qualified_count: int
    produced_count: int
    published_count: int
    skipped_count: int
    skip_reasons: List[str] = Field(default_factory=list)
    shorts_urls: List[str] = Field(default_factory=list)
    longform_urls: List[str] = Field(default_factory=list)
    editorial_summary: str = ""
    is_success: bool = True
