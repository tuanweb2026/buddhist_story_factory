# LONG-FORM VISUAL STYLE GUIDE (16:9 WIDESCREEN)
**Version:** 2.2  
**Date:** 2026-09-27  

---

## 1. Canvas Dimensions & Color Palette

- **Native Resolution:** 1920 x 1080 (16:9 widescreen) or 3840 x 2160 (4K UHD source).
- **Aspect Ratio:** 16:9 exclusively. (9:16 vertical assets are strictly prohibited).
- **Background Theme:** Deep space slate (`#0a0e17` / `rgb(10, 14, 23)`).
- **Accent Primaries:**
  - Electric Cyan (`#0ea5e9` / `rgb(14, 165, 233)`)
  - Tech Blue (`#2563eb` / `rgb(37, 99, 235)`)
  - Emerald Green (`#10b981` / `rgb(16, 185, 129)`)
  - Amber Gold (`#eab308` / `rgb(234, 179, 8)`)
  - Warning Red (`#ef4444` / `rgb(239, 68, 68)`)
- **Text & Foreground:**
  - Primary text: Bright Titanium (`#f8fafc` / `rgb(248, 250, 252)`)
  - Secondary labels: Muted Slate (`#94a3b8` / `rgb(148, 163, 184)`)

---

## 2. 16:9 Screen Division & Safe Margins

- **Top Navigation & Identity Bar:** `y: 40` to `y: 110` (Title, chapter badge, GitHub logo/URL).
- **Headline & Attention Zone:** `y: 130` to `y: 220` (Bold, max 6 words).
- **Main Technical Stage:** `x: 80` to `x: 1840`, `y: 250` to `y: 980` (1760px wide horizontal technical stage).
- **Bottom Status & Telemetry:** `y: 1000` to `y: 1050` (Evidence citations, timing telemetry).

---

## 3. 15 Native 16:9 Visual Layout Classes

1. **`REAL_REPOSITORY_UI`**: Left 40% repository identity, star metrics, topics; Right 60% live commit stream & language distribution breakdown.
2. **`CODE_WALKTHROUGH`**: Side-by-side view with line numbers (Left) and active execution state/variables (Right).
3. **`TERMINAL_DEMO`**: 16:9 Unix terminal window with syntax-highlighted commands, outputs, and status badges.
4. **`ARCHITECTURE_DIAGRAM`**: Horizontal node pipeline showing data transformations across services.
5. **`BROWSER_DEMO`**: Widescreen browser viewport with simulated DOM tree on the left and active interaction canvas on the right.
6. **`DATA_VISUALIZATION`**: Horizontal comparative benchmark bars (e.g. Memory, Latency, CPU).
7. **`BEFORE_AFTER`**: Horizontal split screen (Left: Legacy Approach / Right: Resilient AI Engine).
8. **`CHAPTER_OPENER`**: Minimalist cinematic title card with glowing chapter index and core investigative question (2.5s duration).
9. **`END_PAYOFF`**: Grand architectural summary card with actionable repository takeaways and primary documentation references.
