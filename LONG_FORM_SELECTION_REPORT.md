# LONG-FORM STORY SELECTION REPORT
## Production Test #2: Zed Industries — Zed Code Editor

**Date:** 2026-09-27  
**Production Mode:** `LONG_FORM` (16:9 Documentary Engine V2)  
**Target Duration:** 360–400s (6–7 minutes)  
**Story Type:** Type A — Single Deep-Dive Repository  
**State:** PENDING HUMAN REVIEW (Pre-production Gate)

---

### 1. Selected Repository Metrics & Verification

- **Repository:** `zed-industries/zed`
- **GitHub URL:** https://github.com/zed-industries/zed
- **GitHub Stars:** ~58,200+ (58.2k)
- **Primary Language:** 100% Rust
- **License:** GPL-3.0 / AGPL / Apache-2.0 (Dual/Triple component licensing)
- **Creators:** Nathan Sobo & the original creators of Atom and Tree-sitter

---

### 2. Editorial Rationale & Technical Novelty

#### The Core Problem
For over a decade, desktop code editing tools (VS Code, Atom, Slack, Discord) have been dominated by Electron. Electron bundles an entire Chromium browser and Node.js runtime per window, resulting in:
1. **Severe Memory Overhead:** 200MB–600MB idle RAM usage before opening complex projects or installing extensions.
2. **Keystroke & Frame Latency:** 20ms–50ms keystroke-to-display latency, micro-stutters, and dropped frames on 4K 120Hz/144Hz displays.
3. **High CPU/Battery Consumption:** Constant background garbage collection and DOM reflow cycles.

#### The Technical Breakthrough
Zed rejects the web-stack approach entirely:
1. **GPUI Framework:** Zed created a custom GPU-accelerated UI framework in pure Rust that sends draw calls directly to Metal (macOS) and Vulkan (Linux/Windows), bypassing DOM, CSS, and Chromium layout engines.
2. **Sub-2ms Keystroke Latency:** Renders keystrokes within one monitor refresh frame (under 2ms on high-refresh displays).
3. **Rope Data Structure:** Edits multi-million line files smoothly with asynchronous non-blocking memory allocation.
4. **Rust Concurrency & Zero-Cost Abstractions:** Multi-threaded architecture leveraging Rust's ownership model without data races or garbage collection pauses.

---

### 3. Documentary Narrative Arc (9 Chapters)

1. **Chapter 01: Hook — Editor Nhanh Nhat The Gioi (0.0s – 34.0s)**
   - *Core Message:* Can a code editor start in 0.35s and consume <40MB RAM? Intro to Zed.
2. **Chapter 02: Van De — Rào Cản Hiệu Năng Của Electron (34.0s – 74.0s)**
   - *Core Message:* The hidden costs of Chromium/Electron in VS Code; RAM inflation & jitter on 4K 120Hz.
3. **Chapter 03: Kham Pha — Rust + GPUI Render Truc Tiep (74.0s – 114.0s)**
   - *Core Message:* No HTML, no CSS, no JavaScript. Direct GPU rasterization via GPUI.
4. **Chapter 04: Co Che — Rope Buffer Va Da Luong Rust (114.0s – 168.0s)**
   - *Core Message:* 3 architectural pillars: GPUI, Rope text buffers, and native binary LSP integration.
5. **Chapter 05: Tinh Nang — AI Built-in Va Multi-buffer (168.0s – 222.0s)**
   - *Core Message:* First-class AI integration (local + cloud), multi-buffer unified editing, and CRDT real-time collaboration.
6. **Chapter 06: Benchmark — So Sanh Chi Tiet Voi VS Code (222.0s – 260.0s)**
   - *Core Message:* Real benchmark breakdown: 0.35s vs 3.2s startup, 42MB vs 400MB+ RAM, 2ms latency.
7. **Chapter 07: Gioi Han — He Sinh Thai Va Ho Tro He Dieu Hanh (260.0s – 308.0s)**
   - *Core Message:* Production reality check: Early extension ecosystem vs VS Code Marketplace, Windows support maturity.
8. **Chapter 08: Ket Luan — Khoi Dau Cua The He Editor Sieu Toc (308.0s – 343.0s)**
   - *Core Message:* Paradigm shift towards compiled native desktop software. Link in description.
9. **Chapter 09: CTA — Ket Thuc (343.0s – 360.0s)**
   - *Core Message:* Strictly: Like, share và đăng ký kênh. Zero comment solicitation.

---

### 4. Visual Storytelling Strategy (16:9 Native)

- **Resolution:** 1920x1080 Native.
- **Visual Styles:**
  - `REAL_REPOSITORY_UI`: Exact GitHub repo interface with verified stars and Rust language badges.
  - `ARCHITECTURE_DIAGRAM`: Custom dark-mode GPU rendering pipeline and Rope buffer diagrams.
  - `DATA_VISUALIZATION`: Side-by-side benchmark bars (RAM, latency, startup time).
  - `BEFORE_AFTER`: Electron vs GPUI structural contrast.
  - `TECHNICAL_FLOW`: Multi-buffer & LSP binary pipeline animations.
- **Voice:** Microsoft Neural Voice `vi-VN-HoaiMyNeural` with loudnorm $(-16 \pm 1$ LUFS, TP $\le -1.5$ dBTP).

---

### 5. Compliance & Safety Check

- [x] Vietnamese language only
- [x] Microsoft `vi-VN-HoaiMyNeural` voice
- [x] No macOS `say` fallback
- [x] No robotic voice fallback
- [x] No YouTube upload (Stops at `READY_FOR_HUMAN_REVIEW`)
- [x] CTA only: "Like, share và đăng ký kênh nhé." (No comment solicitation)
- [x] Duration target: 360s (6.0 minutes)
