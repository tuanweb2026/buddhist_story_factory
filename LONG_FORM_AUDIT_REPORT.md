# LONG-FORM DOCUMENTARY ENGINE V2 — ARCHITECTURAL AUDIT REPORT
**Author:** Principal Architect & Senior Video-Production Engineer  
**Date:** 2026-09-27  
**Status:** COMPLETE AUDIT & ROOT CAUSE ANALYSIS  

---

## A. Current Architecture Overview

GitHub Project Radar Factory V2 operates as a single orchestrated pipeline designed originally for 9:16 vertical Shorts, with a recently attached `_run_longform_pipeline()` routing path.

```
DISCOVERY (GitHub trending/search)
  ↓
INTELLIGENCE & SCORING (Content novelty, curiosity, stars)
  ↓
STORY SELECTION (StorySelectionAgent)
  ↓
FACT VERIFICATION (FactVerificationAgent)
  ↓
LONG-FORM SCRIPT (LongFormScriptGenerationAgent)
  ↓
VISUAL PLAN (LongFormVisualStorytellingAgent)
  ↓
ASSET GENERATION (AssetGenerationAgent - SHARED 1080x1920 CANVAS)
  ↓
VOICE GENERATION (VoiceGenerationAgent - edge_tts vi-VN-HoaiMyNeural)
  ↓
VIDEO RENDER (VideoRenderAgent - FFmpeg zoompan to 1920x1080)
  ↓
QA EVALUATION (LongFormQAEvaluator: LF-01 through LF-15)
  ↓
FINAL RED TEAM (audit_final_red_team)
  ↓
TERMINAL STATE (READY_FOR_HUMAN_REVIEW)
```

---

## B. Production Flow Analysis

When executing `python cli.py run --format long_form`:
1. `DiscoveryAgent` and `ContentScoringAgent` score candidates.
2. `Orchestrator` branches to `_run_longform_pipeline()`.
3. `LongFormScriptGenerationAgent` builds a script with 8–9 chapters.
4. `LongFormVisualStorytellingAgent` maps script segments to `LongFormVisualBeat` events.
5. **AssetGenerationAgent** receives each beat and executes `_render_beat_asset()`.
6. `VoiceGenerationAgent` synthesizes speech using `vi-VN-HoaiMyNeural` and normalizes audio to -16 LUFS.
7. **VideoRenderAgent** calls `ffmpeg` with `zoompan=...:s=1920x1080` targeting each asset image.
8. `LongFormQAEvaluator` checks programmatic gates and declares `PASS`.
9. The run stops at `READY_FOR_HUMAN_REVIEW`.

---

## C. Actual Weaknesses Discovered in Artifact Inspection

1. **Pixelated / Blurry 16:9 Video:**
   - As proven by inspection of `data/visuals/lf_648eac5d_LF_C01_B01.png`, every generated image asset is **1080 x 1920** (a vertical 9:16 canvas).
   - In `render.py`, FFmpeg applies `zoompan=...:s=1920x1080` to that 1080x1920 asset.
   - FFmpeg crops the center of the vertical 1080x1920 image and stretches it horizontally across a 1920x1080 frame.
   - Result: severe pixelation, distorted aspect ratios, clipped UI boxes, and illegible text.

2. **Short-Form Aesthetic Stretched to Minutes:**
   - The visual layouts (`_draw_repo_ui`, `_draw_technical_flow`, `_draw_browser_demo`) were designed with a 1080x1920 vertical layout with a top badge at y=120, center card at y=360..1540, and footer at y=1750.
   - None of the components exploit horizontal widescreen space (1920x1080 or 3840x2160 4K).
   - The video is literally a vertical Short stretched into a horizontal rectangle.

3. **Weak Narrative Progression & Missing Curiosity Loops:**
   - While chapters exist (`HOOK`, `VAN DE`, `KHAM PHA`, `CO CHE`), they do not build an escalating investigative narrative.
   - Each chapter states facts rather than posing an intriguing technical mystery (e.g., "How does an LLM see a web page without an API?").
   - There are no open loops connecting chapters; each chapter terminates with a declarative period.

4. **Superficial Evidence & Decorative Assets:**
   - The simulated browser (`_draw_browser_demo`) only shows a booking flight form, regardless of the nuanced mechanics of browser-use (e.g., coordinate clicks, DOM trees, action execution loops, vision grounding).
   - There is no code walkthrough, no architectural component dissection, and no inspectable terminal output.

5. **QA Metric Gaming vs. Viewer Retention:**
   - The QA evaluator checked `status == QAGateStatus.PASS` based on whether `diagram_elements` and `semantic_intent` were non-empty strings.
   - It did not inspect whether the rendered image was natively 16:9, whether source resolution was at least 1920x1080, or whether the narrative actually structured open curiosity loops.

---

## D. Root Causes

1. **Coupled Visual Engine Canvas:**
   - `AssetGenerationAgent.__init__` hardcodes `self.width = 1080` and `self.height = 1920` from `shorts_cfg`.
   - `generate_longform_assets()` simply called `self._render_beat_asset()`, which drew onto `(self.width, self.height) = (1080, 1920)`.
   - The long-form pipeline had no dedicated 16:9 canvas renderer.

2. **Script Pacing and Information Density:**
   - Narrative beats were written as bullet points of 8–15 seconds each, yielding ~230 seconds total (~3.8 minutes), below the 6–8 minute documentary target.
   - Pacing was too fast and lacked dramatic pauses, technical investigations, code walkthroughs, and case studies.

3. **Absence of Dedicated Documentary Visual Classes:**
   - Missing 16:9 native visual classes: `CODE_WALKTHROUGH`, `REAL_GITHUB_SCREEN`, `ARCHITECTURE_DIAGRAM`, `TERMINAL_DEMO`, `DATA_VISUALIZATION`, `BROWSER_DEMO`, `CHAPTER_OPENER`, `PAYOFF_VISUAL`.

4. **Inadequate QA Validation:**
   - No QA gate checked `image.width >= 1920 and image.height >= 1080`.
   - No QA gate checked for 9:16 asset rejection in 16:9 jobs.
   - Red team audit checked text length and duration, but not native aspect ratio or open curiosity loops.

---

## E. Proposed V2 Architecture: LONG-FORM DOCUMENTARY ENGINE V2

```
                       ┌──────────────────────────────┐
                       │   SHARED DISCOVERY & INTEL   │
                       └──────────────┬───────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
┌───────────────────────┐                           ┌───────────────────────────┐
│     SHORTS ENGINE     │                           │   DOCUMENTARY ENGINE V2   │
│  (1080x1920, 9:16)    │                           │    (1920x1080, 16:9)      │
│  - Fast hook (3s)     │                           │  - Multi-act investigation│
│  - 30-60s duration    │                           │  - 6-10 min documentary   │
│  - Shorts visual card │                           │  - Native 16:9 Canvas V2  │
│  - Rapid cut motion   │                           │  - 15 Native Visual Types │
└───────────────────────┘                           │  - Open Loop Retention    │
                                                    │  - LFV2-01 to LFV2-22 QA  │
                                                    └───────────────────────────┘
```

### Key Upgrades:
1. **`LongFormVisualAssetEngine` (Dedicated 16:9 Engine):**
   - Native 1920x1080 canvas (or 3840x2160 supersampled).
   - 15 purpose-built widescreen visual paradigms: Widescreen GitHub dashboard, 2-column split code & terminal, 3-tier node architecture flow, simulated Chromium browser with side-by-side DOM tree & agent thought stream, dynamic benchmark bars, and cinematic 16:9 chapter openers.
2. **`LongFormRetentionEngine` & Documentary Scripting:**
   - Multi-act investigative narrative with open loops in every chapter.
   - Natural documentary pacing (145–155 WPM) with information-dense explanations, reaching 6–8 minutes.
3. **Comprehensive QA Suite (`LFV2-01` through `LFV2-22`):**
   - Native 16:9 asset verification (rejects any asset < 1920x1080).
   - Open loop verification, visual-to-narration semantic verification, documentary red team.

---

## F. Migration Strategy & Regression Protection

1. **Zero Regression for Shorts:** Keep existing `AssetGenerationAgent` and `ScriptGenerationAgent` untouched for shorts.
2. **Isolated Long-Form Subsystem:** Implement `LongFormVisualAssetEngine` and update `LongFormScriptGenerationAgent` and `LongFormVisualStorytellingAgent`.
3. **Full Test Enforcement:** Run the complete pytest test suite before and after rendering to guarantee both Shorts and Long-Form pass all gates.
