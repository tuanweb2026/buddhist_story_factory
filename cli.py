#!/usr/bin/env python3
import sys
import argparse
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="GitHub Project Radar Factory V2 CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: run (execute single pipeline slot)
    run_parser = subparsers.add_parser("run", help="Run a single pipeline execution slot")
    run_parser.add_argument("--format", default="shorts", choices=["shorts", "long_form"], help="Video format")
    run_parser.add_argument("--repo", default=None, help="Target specific repository candidate (e.g. browser-use/browser-use)")
    run_parser.add_argument("--config", default="config/factory.yaml", help="Path to config")
    run_parser.add_argument("--human-review", action="store_true", help="Stop at READY_FOR_HUMAN_REVIEW (do not publish)")

    # Command: schedule (start scheduled daemon)
    sched_parser = subparsers.add_parser("schedule", help="Start the autonomous factory scheduler")
    sched_parser.add_argument("--config", default="config/factory.yaml", help="Path to config")

    # Command: chat (natural language interface)
    chat_parser = subparsers.add_parser("chat", help="Execute natural language chat command")
    chat_parser.add_argument("prompt", nargs="*", help="Natural language prompt")
    chat_parser.add_argument("--config", default="config/factory.yaml", help="Path to config")

    # Command: pdf (Buddhist story video generator)
    buddhist_parser = subparsers.add_parser("pdf", help="Render complete Buddhist story video from PDF or text")
    buddhist_parser.add_argument("--pdf", required=True, help="Path to Buddhist story PDF or TXT file")
    buddhist_parser.add_argument("--format", default="portrait", choices=["portrait", "landscape"], help="portrait (9:16 Shorts) or landscape (16:9 Long-form)")
    buddhist_parser.add_argument("--voice", default="vi-VN-HoaiMyNeural", help="Vietnamese Neural voice (default: vi-VN-HoaiMyNeural)")
    buddhist_parser.add_argument("--output", default="data/buddhist_production", help="Output directory")
    buddhist_parser.add_argument("--max-scenes", type=int, default=10, help="Max scenes to generate")
    buddhist_parser.add_argument("--no-subtitles", action="store_true", help="Disable subtitles")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "run":
        from radar.utils.helpers import load_config
        from radar.orchestrator.pipeline import Orchestrator
        cfg = load_config(getattr(args, "config", "config/factory.yaml"))
        orchestrator = Orchestrator(cfg)
        mock_candidates = None
        if args.repo:
            from radar.models.schemas import RepositoryCandidate
            r_name = args.repo.split("/")[-1]
            # Dynamic metadata per known repo
            if "zed" in r_name.lower():
                description = "Code at the speed of thought. AI-native code editor built in Rust with GPU rendering."
                stars = 58200
                forks = 3400
                language = "Rust"
                topics = ["editor", "rust", "ai", "gpu", "open-source"]
                stars_today = 680
            elif "omi" in r_name.lower():
                description = "The world's leading open-source AI wearable."
                stars = 13590
                forks = 1200
                language = "Python"
                topics = ["wearable", "ai", "hardware", "open-source"]
                stars_today = 220
            elif "uv" in r_name.lower():
                description = "An extremely fast Python package and project manager, written in Rust."
                stars = 38500
                forks = 1200
                language = "Rust"
                topics = ["python", "rust", "package-manager", "pip"]
                stars_today = 520
            else:
                description = "Make websites accessible to AI agents. Connect your AI to web interactions."
                stars = 32450
                forks = 3100
                language = "Python"
                topics = ["agent", "browser-automation", "ai"]
                stars_today = 450
            mock_candidates = [
                RepositoryCandidate(
                    full_name=args.repo,
                    owner=args.repo.split("/")[0],
                    name=r_name,
                    html_url=f"https://github.com/{args.repo}",
                    description=description,
                    stars=stars,
                    forks=forks,
                    open_issues=45,
                    language=language,
                    pushed_at="2026-09-26T10:00:00Z",
                    stars_today=stars_today,
                    topics=topics
                )
            ]
        print(f"[*] Starting GitHub Project Radar Factory V2 slot ({args.format})...")
        res = orchestrator.run_pipeline(
            format_type=args.format,
            mock_candidates=mock_candidates,
            stop_at_human_review=args.human_review
        )
        print(f"[+] Slot finished with state: {res['state'].value}")
        if "publishing" in res:
            print(f"[+] View URL: {res['publishing'].view_url}")
        if "render" in res:
            print(f"[+] Video file: {res['render'].video_path}")
            print(f"[+] Duration: {res['render'].duration_sec:.2f}s ({res['render'].width}x{res['render'].height})")
        if "thumbnail_path" in res:
            print(f"[+] Thumbnail file: {res['thumbnail_path']}")
        if "editorial_report" in res:
            ed = res['editorial_report']
            print(f"[+] Central Question: '{ed.central_question}'")
            print(f"[+] Viewer Promise: '{ed.viewer_promise}'")
            print(f"[+] Viewer Value Score: {ed.viewer_value_score:.1f}/100 (Decision: {ed.decision})")
        if "metadata" in res:
            meta_p = getattr(res['metadata'], 'story_id', None)
            print(f"[+] Metadata: {meta_p}_metadata.json")
        if "qa_reports" in res:
            print(f"[+] QA Gates passed: {len(res['qa_reports'])}")
            for r in res['qa_reports']:
                print(f"    - {r.gate_name}: {r.status.value}")
    elif args.command == "schedule":
        from radar.utils.helpers import load_config
        from radar.scheduler.scheduler import FactoryScheduler
        cfg = load_config(getattr(args, "config", "config/factory.yaml"))
        scheduler = FactoryScheduler(cfg)
        print("[*] Starting Radar Factory Autonomous Scheduler. Press Ctrl+C to exit.")
        try:
            scheduler.start_background()
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nScheduler stopped.")
    elif args.command == "chat":
        from radar.utils.helpers import load_config
        from radar.chat.chat_command_router import ChatCommandRouter
        cfg = load_config(getattr(args, "config", "config/factory.yaml"))
        router = ChatCommandRouter(cfg)
        prompt_text = " ".join(args.prompt).strip()
        if not prompt_text:
            print("Usage: python cli.py chat <command text>")
            sys.exit(1)
        res = router.handle_command(prompt_text)
        print(res["response_text"])
    elif args.command == "pdf":
        from pdf_story_engine import process_pdf_to_video
        process_pdf_to_video(
            pdf_path=args.pdf,
            output_dir=args.output,
            orientation=args.format,
            voice=args.voice,
            with_subtitles=not args.no_subtitles,
            max_scenes=args.max_scenes
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
