# FACTORY MASTER UPGRADE REPORT — LONG-FORM & MULTI-FORMAT AUTOPILOT
**Version 2.1 Upgrade Completion**
**Date:** 2026-09-27

---

## 1. Executive Summary

GitHub Project Radar Factory V2 has been extended to support production-grade **LONG_FORM mode** alongside the existing **Shorts pipeline**. Both modes operate under a unified autonomous architecture:
`Discovery → Intelligence → Scoring → Story Selection → Fact Verification → Script Generation → Visual Planning → Asset Generation → Voice Generation → Audio QA → Video Render → Render QA → Final Red Team QA → Publish → Post-Publish Verification`.

---

## 2. Deliverables & Modified Files

| File | Type | Description |
|---|---|---|
| [`radar/models/schemas.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/models/schemas.py) | Modified | Added `LongFormStoryType`, `LongFormChapter`, `LongFormScriptArtifact`, `LongFormVisualBeat`, `LongFormStoryboard`, `LongFormMetadata`, `ClaimClassification`, `PublicationHistoryEntry` |
| [`radar/agents/longform_script_agent.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/longform_script_agent.py) | New | Implemented 9-chapter retention documentary scripts supporting Type A (single deep dive) and Type B (multi-repo theme) with claim classifications |
| [`radar/agents/longform_visual_agent.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/longform_visual_agent.py) | New | Long-form visual storyboard planner with chapter opener cards and full V3 narration alignment |
| [`radar/agents/asset_generation_agent.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/asset_generation_agent.py) | Modified | Added `_draw_chapter_title_card`, `generate_thumbnail` (16:9 1280x720), and `generate_longform_assets` |
| [`radar/agents/render.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/render.py) | Modified | Multi-format rendering engine supporting 16:9 (1920x1080) and 9:16 (1080x1920) with clip caching and dynamic timeouts |
| [`radar/agents/voice.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/voice.py) | Modified | Extended to accept both `ScriptArtifact` and `LongFormScriptArtifact` |
| [`radar/agents/story.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/agents/story.py) | Modified | Extended `select_story` to support multi-repo bundling for long-form |
| [`radar/qa/longform_evaluator.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/qa/longform_evaluator.py) | New | Full LF-01 through LF-15 QA gate implementation with strict fail-closed evaluation |
| [`radar/publisher/publisher.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/publisher/publisher.py) | Modified | Added `publish_longform`, `LONG_FORM_METADATA.json` generation, and cross-day deduplication history |
| [`radar/scheduler/scheduler.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/scheduler/scheduler.py) | Modified | Upgraded to manage independent daily slots: 3 Shorts (`SHORT_01`, `SHORT_02`, `SHORT_03`) + 1 Long-form (`LONG_01`) with isolated failure handling |
| [`radar/orchestrator/pipeline.py`](file:///Users/abc/Documents/github_project_radar_factory/radar/orchestrator/pipeline.py) | Modified | Integrated long-form subagents and implemented `_run_longform_pipeline` |
| [`cli.py`](file:///Users/abc/Documents/github_project_radar_factory/cli.py) | Modified | Added `--format long_form` CLI routing, thumbnail, and metadata reporting |
| [`tests/test_longform_pipeline.py`](file:///Users/abc/Documents/github_project_radar_factory/tests/test_longform_pipeline.py) | New | 7 comprehensive unit and integration tests covering the complete long-form pipeline |

---

## 3. Test Suite Verification

Full test suite execution:
```
pytest tests/ -v
================== 23 passed, 1 warning in 132.73s ==================
```

- **Shorts regression tests:** 16 passed
- **Long-form tests:** 7 passed
- **Failures:** 0

---

## 4. Controlled Long-Form Production Dry Run

- **Command executed:** `python cli.py run --format long_form --repo browser-use/browser-use --human-review`
- **Output state:** `READY_FOR_HUMAN_REVIEW`
- **Rendered video path:** [`data/rendered/lf_648eac5d.mp4`](file:///Users/abc/Documents/github_project_radar_factory/data/rendered/lf_648eac5d.mp4)
- **Resolution:** 1920x1080 (16:9 cinematic widescreen, H.264 + AAC)
- **Duration:** 232.10s (8 complete documentary chapters)
- **Voice:** Microsoft Neural Voice `vi-VN-HoaiMyNeural`
- **Audio standard:** -16.0 LUFS integrated, True Peak <= -1.5 dBTP
- **Thumbnail path:** [`data/visuals/lf_648eac5d_thumbnail.png`](file:///Users/abc/Documents/github_project_radar_factory/data/visuals/lf_648eac5d_thumbnail.png) (1280x720 16:9)
- **Metadata artifact:** [`data/rendered/lf_648eac5d_metadata.json`](file:///Users/abc/Documents/github_project_radar_factory/data/rendered/lf_648eac5d_metadata.json)
- **QA Gates passed:** 17/17 PASS (All LF-01 through LF-15 gates verified)
