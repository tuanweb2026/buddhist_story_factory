# ARCHITECTURE

Central Orchestrator + specialized agents.

Logical layers:
Discovery → Intelligence → Editorial → Production → QA → Publishing.

State:
DISCOVERY_RUNNING → DISCOVERY_QA → CANDIDATE_POOL_READY → RESEARCH → SCORING → STORY_SELECTION → FACT_VERIFICATION → SCRIPT → SCRIPT_QA → VISUALS → VISUAL_QA → VOICE → AUDIO_QA → RENDER → RENDER_QA → FINAL_RED_TEAM → READY_FOR_PUBLISH → PUBLISHING → POST_PUBLISH_VERIFICATION → PUBLISHED.

Failure states:
HUMAN_REVIEW_REQUIRED / FAILED / QUARANTINED.

Rules:
- no chat state as pipeline state
- every transition has an artifact
- resumable
- modular
- independently testable
