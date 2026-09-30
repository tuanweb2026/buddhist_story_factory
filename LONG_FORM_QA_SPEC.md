# LONG-FORM QA SPECIFICATION (LFV2-01 THROUGH LFV2-22)
**Version:** 2.2  
**Date:** 2026-09-27  

---

## 1. Specification Overview

Every long-form video produced by GitHub Project Radar Factory V2 must undergo automated, fail-closed verification against 22 rigorous QA gates before reaching `READY_FOR_HUMAN_REVIEW`.

---

## 2. Gate Definitions

| Gate ID | Name | Criteria | Failure Action |
|---|---|---|---|
| **LFV2-01** | Story Integrity | Script has complete chapters (min 5), zero placeholders, complete narration. | Fail Closed |
| **LFV2-02** | Narrative Continuity | Chapters progress logically: Hook $\to$ Problem $\to$ Discovery $\to$ Mechanism $\to$ Demo $\to$ Limitations $\to$ Payoff $\to$ CTA. | Fail Closed |
| **LFV2-03** | Fact Verification | 100% of factual statements grounded in verified evidence items. | Fail Closed |
| **LFV2-04** | Source Coverage | Official repository URL and primary documentation citations present. | Fail Closed |
| **LFV2-05** | Originality | No duplicate sentences or repetitive paragraphs across chapters. | Fail Closed |
| **LFV2-06** | Retention Structure | Every chapter introduces a new technical payoff. | Fail Closed |
| **LFV2-07** | Open Loop Integrity | Every chapter (except CTA) articulates an investigative question. | Fail Closed |
| **LFV2-08** | Visual-Narration Alignment | 100% of visual beats map to an exact narration claim (zero orphan visuals). | Fail Closed |
| **LFV2-09** | Visual Evidence Quality | Visual elements prove, demonstrate, or diagram the narrated mechanism. | Fail Closed |
| **LFV2-10** | Native 16:9 Asset Quality | Every visual asset is natively $\ge 1920 \times 1080$ with a 16:9 aspect ratio. Rejects any 9:16 Shorts asset. | Fail Closed |
| **LFV2-11** | Visual Variety | At least 5 distinct 16:9 scene paradigms utilized. | Fail Closed |
| **LFV2-12** | Visual Fatigue | No static visual holds longer than 15s without purposeful camera movement. | Fail Closed |
| **LFV2-13** | Camera Intent | Camera motions (`PUSH_IN`, `CODE_FOCUS`, `UI_FOCUS`, `DATA_FLOW`) track attention targets. | Fail Closed |
| **LFV2-14** | Demonstration Integrity | Demonstrations are grounded in real or documented workflows, never fabricated. | Fail Closed |
| **LFV2-15** | Audio Quality | Broadcast loudness: $-16.0 \pm 1.0$ LUFS integrated, True Peak $\le -1.5$ dBTP. | Fail Closed |
| **LFV2-16** | Voice Naturalness | Uses Microsoft Neural Voice (`vi-VN-HoaiMyNeural`), documentary pacing (145–160 WPM). | Fail Closed |
| **LFV2-17** | Chapter Timing | Chapter duration matches information density; opener title cards $\le 3$s. | Fail Closed |
| **LFV2-18** | Thumbnail Quality | Dedicated 16:9 ($1280 \times 720$), high contrast, 2–6 words, no paragraph text. | Fail Closed |
| **LFV2-19** | Metadata Integrity | `LONG_FORM_METADATA.json` includes formatted YouTube chapters (`00:00 Chapter`). | Fail Closed |
| **LFV2-20** | CTA Compliance | Strict CTA: Like, Share, and Subscribe only. Zero comment solicitations. | Fail Closed |
| **LFV2-21** | Documentary Quality | Narrative feels like an investigative documentary, not a README recitation. | Fail Closed |
| **LFV2-22** | Final Red Team | Adversarial evaluation verifies video is engaging, clear, high-resolution, and valuable. | Fail Closed |
