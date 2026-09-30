# GITHUB PROJECT RADAR FACTORY V2
# LONG-FORM MODE SPECIFICATION
# Version 2.1

## 0. PURPOSE

Add a production-grade LONG_FORM mode to GitHub Project Radar Factory V2.

The existing Shorts pipeline must remain fully functional.

The Factory must support:

1. 2–3 Shorts per day
2. 1 Long-form video per day
3. Fully autonomous scheduled production
4. Fully autonomous publishing when every safety gate passes
5. Fail-closed behavior
6. Internal QA and Red-Team validation
7. No manual approval gate during normal scheduled operation

The architecture must remain:

DISCOVERY
→ REPOSITORY INTELLIGENCE
→ CONTENT SCORING
→ STORY SELECTION
→ FACT VERIFICATION
→ SCRIPT GENERATION
→ VISUAL PLANNING
→ ASSET GENERATION
→ VOICE GENERATION
→ AUDIO QA
→ VIDEO RENDER
→ RENDER QA
→ FINAL RED TEAM QA
→ PUBLISH
→ POST-PUBLISH VERIFICATION

Do NOT create a second independent Factory.

LONG_FORM is a production mode inside the existing Factory.

---

# 1. CORE CONTENT PHILOSOPHY

The Factory is NOT a README summarizer.

The Factory creates curiosity-driven technology content about interesting GitHub repositories.

Primary viewer motivations:

- discover new technology
- discover interesting GitHub projects
- understand what a repository actually does
- see why the project is interesting
- understand how the technology works
- discover possible real-world use cases
- follow emerging developer/AI technology
- satisfy curiosity

The viewer does NOT necessarily need to install or run the repository.

Therefore:

STAR COUNT ≠ AUTOMATIC STORY QUALITY.

A repository may be selected because:

- very high stars
- rapid star growth
- high developer attention
- unusual technology
- visually explainable architecture
- surprising capability
- strong curiosity factor
- important ecosystem position
- major release
- controversial/interesting technical change
- strong community activity
- strong narrative potential

The system must optimize for:

CONTENT POTENTIAL

not merely:

POPULARITY.

---

# 2. SHORTS MODE

Shorts remain optimized for:

30–60 seconds.

Typical structure:

HOOK
→ WHAT IS IT?
→ WHY IS IT INTERESTING?
→ HOW DOES IT WORK?
→ WHY SHOULD VIEWERS CARE?
→ PAYOFF
→ CTA

CTA policy:

ONLY:

LIKE
SHARE
ĐĂNG KÝ KÊNH

Never request comments.

Never use:

"Comment below"
"Comment AI"
"Tell me what you think"
"Drop a comment"

---

# 3. LONG-FORM MODE

Target duration:

6–12 minutes.

Default target:

8–10 minutes.

Long-form must NOT simply concatenate Shorts.

Long-form requires:

- deeper narrative
- stronger research
- multiple visual chapters
- contextual explanation
- architecture explanation
- practical implications
- comparisons where appropriate
- limitations
- conclusion
- visual continuity

A Long-form video should feel like a coherent technology documentary / deep-dive.

---

# 4. LONG-FORM STORY TYPES

The Story Selection Agent may select one of these formats.

## TYPE A — SINGLE REPOSITORY DEEP DIVE

Example:

"How browser-use lets AI control a real browser"

Structure:

1. Hook
2. What problem exists?
3. What is the repository?
4. Why did it become popular?
5. How does it work?
6. Architecture
7. Example workflow
8. What makes it different?
9. Limitations
10. Who should care?
11. Final takeaway
12. CTA

---

## TYPE B — MULTI-REPOSITORY THEME

Example:

"7 GitHub projects changing AI agents"

Each repository receives a meaningful segment.

The Factory must NOT force exactly 7 repositories.

Repository count is dynamic.

Choose the number based on:

- narrative strength
- research depth
- total runtime
- visual diversity
- factual confidence

Typical:

4–8 repositories.

---

## TYPE C — TECHNOLOGY EXPLAINER

Example:

"How AI browser agents actually work"

Repositories are evidence/examples supporting the explanation.

The topic is primary.

Repositories are secondary evidence.

---

## TYPE D — TREND / ECOSYSTEM REPORT

Example:

"The GitHub AI Agent ecosystem is changing fast"

Use multiple repositories, releases, stars, activity and technical developments.

Must clearly separate:

FACT
from
INTERPRETATION.

---

# 5. LONG-FORM NARRATIVE ARCHITECTURE

Every Long-form script should have chapters.

Recommended structure:

CHAPTER 01 — HOOK
0:00–0:30

CHAPTER 02 — THE PROBLEM
0:30–1:30

CHAPTER 03 — DISCOVERY
1:30–2:30

CHAPTER 04 — HOW IT WORKS
2:30–4:30

CHAPTER 05 — VISUAL / TECHNICAL DEEP DIVE
4:30–6:00

CHAPTER 06 — REAL-WORLD IMPLICATION
6:00–7:30

CHAPTER 07 — LIMITATIONS / TRADE-OFFS
7:30–8:30

CHAPTER 08 — FINAL TAKEAWAY
8:30–9:00

CHAPTER 09 — CTA
Final 10–15 seconds

These timestamps are guidelines, not hardcoded.

The Script Agent must dynamically adjust chapters according to actual content.

---

# 6. RETENTION DESIGN

Every chapter must introduce at least one new information event.

Avoid:

- repetitive explanations
- repeating the same repository description
- generic filler
- unnecessary introductions
- long greetings
- paragraph-heavy visual cards
- excessive statistics
- repeated CTA

The narrative should continuously answer:

"What is interesting about this?"

Then:

"How does it actually work?"

Then:

"Why does it matter?"

Then:

"What should I remember?"

---

# 7. VISUAL STORYTELLING

CRITICAL RULE:

Do not create visuals merely to decorate narration.

Every major visual must either:

1. prove the narration
2. demonstrate the narration
3. explain the narration
4. visualize an abstract technical concept
5. show repository evidence
6. create a visual payoff

Required visual relationship:

VOICE
→ VISUAL EVIDENCE / EXPLANATION
→ CAMERA MOVEMENT
→ VISUAL PAYOFF
→ NEXT IDEA

Never:

VOICE
→ RANDOM IMAGE
→ RANDOM IMAGE
→ RANDOM IMAGE

---

# 8. LONG-FORM VISUAL LANGUAGE

Use the existing Visual Storytelling Engine V2.

Extend it with:

- chapter opening visuals
- architecture diagrams
- repository UI
- GitHub statistics
- terminal demonstrations
- code snippets
- browser simulations
- system diagrams
- data flows
- animated arrows
- node graphs
- zoom-ins
- push-ins
- pan transitions
- visual reveals
- comparison layouts
- timeline visuals

Each visual beat must have:

visual_purpose
narration_reference
evidence_reference
camera_motion
transition
payoff

---

# 9. VISUAL PACING

Long-form pacing should be slower than Shorts.

But NEVER become static.

Recommended:

New meaningful visual event every:

2–6 seconds.

Some technical scenes may remain longer when the visual itself contains progressive animation.

Avoid:

one static slide remaining for 20–30 seconds.

---

# 10. VOICE

Use the existing Microsoft Neural Voice system.

Primary Vietnamese:

vi-VN-HoaiMyNeural

Secondary:

vi-VN-NamMinhNeural

No silent fallback to macOS "say".

If Microsoft Neural Voice fails:

RETRY.

If still failing:

STOP JOB.

Do not generate robotic fallback audio.

Voice characteristics:

- natural Vietnamese
- conversational
- confident
- technically knowledgeable
- warm
- documentary / technology presenter style
- variable sentence rhythm
- appropriate pauses
- no monotonous machine cadence

Long-form pacing should prioritize natural storytelling rather than fixed WPM.

---

# 11. LONG-FORM AUDIO

Target:

-16 LUFS integrated.

True peak:

<= -1.5 dBTP.

Voice must remain intelligible over music.

Background music:

LOW.

Never compete with narration.

Use subtle transitions and technology ambience when appropriate.

---

# 12. FACT VERIFICATION

Long-form requires stronger fact verification than Shorts.

Every important factual claim must have:

source
claim
verification status

Preferred sources:

1. Official GitHub repository
2. Official documentation
3. Official release notes
4. Official paper
5. Official organization announcement
6. Primary technical source

Secondary sources may provide context but must not silently replace primary evidence for important technical claims.

---

# 13. CLAIM TYPES

Classify claims:

FACT
INFERENCE
INTERPRETATION
OPINION / COMMENTARY

Do not present inference as fact.

Do not invent:

- user numbers
- revenue
- performance
- adoption
- capabilities
- benchmark results
- security properties

---

# 14. LIMITATIONS SECTION

Every Long-form video should include limitations when relevant.

Examples:

- immature feature
- experimental component
- high compute requirements
- reliability issues
- setup complexity
- ecosystem dependency
- incomplete documentation
- license restrictions
- known technical limitations

Do not manufacture criticism.

If no material limitation is documented:

state that the available evidence did not establish one.

---

# 15. CHAPTER METADATA

Every Long-form video must generate:

LONG_FORM_METADATA.json

Containing:

title
description
chapters
repository_urls
sources
hashtags
thumbnail_text
duration
language
voice
qa_status
publication_status

YouTube chapters must use:

00:00 Chapter Name

format.

---

# 16. THUMBNAIL

Generate a dedicated Long-form thumbnail.

Do NOT reuse Shorts visual assets.

Thumbnail requirements:

- 16:9
- 1280x720 preferred
- high contrast
- 2–6 words maximum
- one dominant visual concept
- repository branding when legally appropriate
- curiosity-driven
- no misleading claims

---

# 17. TITLE GENERATION

Title Agent generates multiple candidates internally.

Select one according to:

- factual accuracy
- curiosity
- clarity
- search relevance
- no clickbait deception

Do not use fabricated claims.

---

# 18. LONG-FORM QA

Add the following QA gates:

LF-01 Chapter Integrity
LF-02 Narrative Continuity
LF-03 Fact Consistency
LF-04 Source Coverage
LF-05 Repetition Detection
LF-06 Visual-Narration Alignment
LF-07 Visual Variety
LF-08 Visual Fatigue
LF-09 Audio Continuity
LF-10 Chapter Timing
LF-11 Retention Structure
LF-12 Thumbnail Integrity
LF-13 Metadata Integrity
LF-14 CTA Compliance
LF-15 Final Red Team

Any:

FAIL
UNKNOWN
MISSING
UNRESOLVED
EXPIRED
CONFLICT

must block publication.

---

# 19. PUBLISHING

If all QA gates PASS:

SHORTS:

publish according to scheduled Shorts slots.

LONG-FORM:

publish according to scheduled Long-form slot.

Use the existing Publisher Engine.

Never bypass:

- authentication
- duplicate protection
- QA
- metadata validation
- upload verification

---

# 20. DAILY PRODUCTION TARGET

Default daily schedule:

SHORT #1
SHORT #2
SHORT #3
LONG-FORM #1

The Scheduler must treat these as independent jobs.

If one job fails:

DO NOT stop unrelated jobs.

Example:

Short #1 FAIL
Short #2 PASS
Short #3 PASS
Long-form PASS

The scheduler continues.

---

# 21. DAILY REPOSITORY STRATEGY

Discovery should continuously scan GitHub.

Prioritize:

- high-star repositories
- rapidly growing repositories
- high engagement
- active development
- unusual technologies
- new releases
- emerging projects
- important ecosystem projects
- visually explainable repositories

Do NOT always select the highest-star repository.

Do NOT always select the newest repository.

Content potential is the deciding metric.

---

# 22. CROSS-DAY DEDUPLICATION

Prevent:

- same repository repeated too frequently
- same story angle repeated
- same headline pattern repeated
- same visual sequence repeated

Maintain:

publication_history.json

Track:

repository
story angle
publication date
format
title
content hash

---

# 23. SHORT + LONG FORM RELATIONSHIP

A repository may appear in both Shorts and Long-form.

But:

SHORT = discovery

LONG = deeper explanation.

Never simply reuse the Short script.

The Long-form script must provide substantial additional information.

---

# 24. FINAL PRINCIPLE

The Factory should behave like an autonomous technology media studio.

Not:

"GitHub README → AI voice → slideshow"

But:

GITHUB DISCOVERY
→ SIGNAL DETECTION
→ REPOSITORY INTELLIGENCE
→ STORY DISCOVERY
→ FACT VERIFICATION
→ NARRATIVE DESIGN
→ VISUAL EXPLANATION
→ NATURAL VOICE
→ CINEMATIC EDITING
→ RED TEAM QA
→ AUTOMATIC PUBLICATION

The goal is:

EVERY VIDEO MUST GIVE THE VIEWER A REASON TO KEEP WATCHING.
