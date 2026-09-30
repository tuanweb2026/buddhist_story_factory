# LONG-FORM DOCUMENTARY ENGINE V2 — ARCHITECTURE SPECIFICATION
**Version:** 2.2  
**Date:** 2026-09-27  

---

## 1. System Overview

`LONG-FORM DOCUMENTARY ENGINE V2` is an autonomous documentary generation engine built inside GitHub Project Radar Factory V2. It transforms high-signal GitHub repositories into 6–10 minute, 16:9 widescreen technology investigations.

---

## 2. Core Modules

### 2.1 Narrative & Retention Engine (`LongFormScriptGenerationAgent`)
- Implements 4 documentary structures:
  - **Type A:** Single Project Investigation (10–11 narrative beats)
  - **Type B:** Technology Breakdown
  - **Type C:** Multi-Repo Investigation
  - **Type D:** Trend Documentary
- Enforces the **Open Loop Principle**: Every chapter poses an intriguing technical question, delivers concrete factual answers, and opens the next curiosity thread.
- Target duration: 360–600 seconds (6–10 minutes) with natural documentary speech pacing (145–155 WPM).

### 2.2 Native 16:9 Visual Asset Engine (`LongFormVisualAssetEngine`)
- Natively draws in **1920x1080** (or supersampled 3840x2160) widescreen resolution.
- Zero reuse or stretching of 9:16 Shorts assets.
- Provides 15 native visual types:
  1. `REAL_REPOSITORY_UI`
  2. `REAL_GITHUB_SCREEN`
  3. `CODE_WALKTHROUGH`
  4. `TERMINAL_DEMO`
  5. `ARCHITECTURE_DIAGRAM`
  6. `DATA_VISUALIZATION`
  7. `PRODUCT_WORKFLOW`
  8. `BROWSER_DEMO`
  9. `SCREEN_RECORDING`
  10. `TECHNICAL_ILLUSTRATION`
  11. `CONCEPTUAL_CINEMATIC`
  12. `COMPARISON`
  13. `TIMELINE`
  14. `CHAPTER_OPENER`
  15. `END_PAYOFF`

### 2.3 Audio & Camera Timing
- Voice: Microsoft Neural Voice (`vi-VN-HoaiMyNeural` primary, `vi-VN-NamMinhNeural` secondary). Fail-closed on errors.
- Audio loudness: -16.0 LUFS integrated, True Peak <= -1.5 dBTP.
- Camera movements tailored to information target: `PUSH_IN`, `PULL_OUT`, `PAN_LEFT`, `PAN_RIGHT`, `CODE_FOCUS`, `UI_FOCUS`, `DATA_FLOW`.

### 2.4 QA System (LFV2-01 through LFV2-22)
Comprehensive quality gates ensuring strict documentary standards:
- `LFV2-01` Story Integrity
- `LFV2-02` Narrative Continuity
- `LFV2-03` Fact Verification
- `LFV2-04` Source Coverage
- `LFV2-05` Originality
- `LFV2-06` Retention Structure
- `LFV2-07` Open Loop Integrity
- `LFV2-08` Visual-Narration Alignment
- `LFV2-09` Visual Evidence Quality
- `LFV2-10` Native 16:9 Asset Quality (Strict aspect ratio & resolution enforcement)
- `LFV2-11` Visual Variety
- `LFV2-12` Visual Fatigue
- `LFV2-13` Camera Intent
- `LFV2-14` Demonstration Integrity
- `LFV2-15` Audio Quality
- `LFV2-16` Voice Naturalness
- `LFV2-17` Chapter Timing
- `LFV2-18` Thumbnail Quality
- `LFV2-19` Metadata Integrity
- `LFV2-20` CTA Compliance
- `LFV2-21` Documentary Quality
- `LFV2-22` Final Red Team
