# LONG-FORM RETENTION SPECIFICATION
**Version:** 2.2  
**Date:** 2026-09-27  

---

## 1. Core Retention Philosophy

Viewers remain engaged during long-form technology documentaries when there is a continuous chain of **curiosity loops**:

$$\text{Open Loop (The Question)} \longrightarrow \text{Investigation (Evidence)} \longrightarrow \text{Information Delivery (The Answer)} \longrightarrow \text{Visual Payoff} \longrightarrow \text{Next Loop (The Higher-Order Problem)}$$

Empty clickbait, generic suspense ("và điều bất ngờ sắp xuất hiện..."), or repetitive praise are strictly prohibited. Every retention event must be anchored in real technical dilemmas.

---

## 2. Chapter Loop Architecture (Example: Zed Editor Investigation)

1. **Chapter 01: Cold Open & The Benchmark Anomaly**
   - *Open Loop:* Why does a modern text editor take 3 seconds to launch and consume 500MB of RAM?
   - *Information:* Show VS Code Electron startup profiler.
   - *Payoff:* Zed launches in 0.3s with 40MB RAM.
   - *Next Loop:* But how can an editor render rich text and syntax trees in under 2ms without Chromium?

2. **Chapter 02: Electron vs Native GPU Rendering**
   - *Open Loop:* How did desktop software become dependent on a web browser engine?
   - *Information:* Breakdown of Electron DOM/CSS overhead.
   - *Payoff:* Contrast with GPUI engine rendering direct GPU draw calls.
   - *Next Loop:* If GPUI bypasses the DOM, how does it handle complex multi-file buffers?

3. **Chapter 03: The Rope Data Structure & Buffer Engine**
   - *Open Loop:* What happens when you open a 2GB log file?
   - *Information:* Flat string arrays crash; Rope binary tree splits chunks in $O(\log n)$.
   - *Payoff:* Smooth scrolling in million-line files.
   - *Next Loop:* Speed is solved, but what about the developer workflow—how does AI fit into a native Rust editor?

4. **Chapter 04: AI-Native Inline Synthesis**
   - *Open Loop:* Can AI assist developers without cloud latency and third-party extensions?
   - *Information:* Inline transformation directly communicating with LLM via background channels.
   - *Payoff:* Code transforms inline inside the editor canvas.
   - *Next Loop:* But what are the real limitations before a team migrates from VS Code?

5. **Chapter 05: The Limitations & Ecosystem Reality Check**
   - *Open Loop:* Is Zed ready to replace VS Code today?
   - *Information:* Extension ecosystem maturity, Windows platform support timeline.
   - *Payoff:* Objective evaluation of current production trade-offs.
   - *Next Loop:* What does Zed signal for the future of desktop tooling?

6. **Chapter 06: Final Takeaway & Architectural Payoff**
   - *Synthesis:* Native compiled languages + GPU acceleration + local AI is redefining desktop software.
