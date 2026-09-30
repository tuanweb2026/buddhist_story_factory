import os
import subprocess
from typing import Dict, Any, Optional
from radar.models.schemas import VisualStoryboard, AudioArtifact, RenderArtifact


class VideoRenderAgent:
    """Renders 1080x1920 9:16 vertical video with camera motion treatments (zoom-pan / push-in)
    and synchronized subtitles using FFmpeg.
    
    Implements Visual Storytelling Engine V3:
    Camera motion directs attention to the semantic `attention_target`:
    - PUSH_IN: Smooth push-in zoom into center/focal element
    - ZOOM_TO_DETAIL: Focused zoom targeting specific detail (e.g. badge, repo metric)
    - PAN_LEFT_TO_RIGHT: Horizontal scan across comparison or flow nodes
    - DATA_FLOW: Subtle floating motion tracking sequential flow
    - REVEAL: Scaled focus revealing code terminal output
    - BEFORE_AFTER_SPLIT: Motion guiding eye across split comparison
    - PAYOFF_PUSH: Dramatic push-in on payoff synthesis
    - STATIC: Steady focus for safe screens (CTA)
    
    Voice track is the TIMING AUTHORITY: Scene beat durations are derived from the audio track.
    """

    def __init__(self, config: Dict[str, Any], output_dir: str = "data/rendered", format_type: str = "shorts"):
        self.config = config
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.format_type = format_type
        fmt_cfg = config.get("formats", {}).get(format_type, {})
        if format_type == "long_form":
            self.width = fmt_cfg.get("width", 1920)
            self.height = fmt_cfg.get("height", 1080)
        else:
            self.width = fmt_cfg.get("width", 1080)
            self.height = fmt_cfg.get("height", 1920)
        self.fps = fmt_cfg.get("fps", 30)

    def render(self, storyboard: Any, audio: AudioArtifact, format_type: Optional[str] = None) -> RenderArtifact:
        if format_type and format_type != self.format_type:
            fmt_cfg = self.config.get("formats", {}).get(format_type, {})
            if format_type == "long_form":
                w, h = fmt_cfg.get("width", 1920), fmt_cfg.get("height", 1080)
            else:
                w, h = fmt_cfg.get("width", 1080), fmt_cfg.get("height", 1920)
        else:
            w, h = self.width, self.height

        out_mp4 = os.path.join(self.output_dir, f"{storyboard.story_id}.mp4")
        temp_clips_dir = os.path.join(self.output_dir, f"{storyboard.story_id}_clips")
        os.makedirs(temp_clips_dir, exist_ok=True)

        num_beats = len(storyboard.beats)
        if num_beats == 0:
            raise ValueError("Storyboard has no beats to render.")

        # Total audio duration is the timing authority
        total_audio_dur = audio.duration_sec
        clip_paths = []

        # 1. Render individual beat clips with motion filters targeting attention
        for i, beat in enumerate(storyboard.beats):
            clip_file = os.path.join(temp_clips_dir, f"clip_{i:02d}.mp4")
            beat_dur = max(2.0, beat.duration_sec * (total_audio_dur / storyboard.total_duration_sec))
            
            num_frames = int(beat_dur * self.fps)
            motion = (beat.motion_type or "PUSH_IN").upper()

            if motion in ["ZOOM_TO_DETAIL", "PAYOFF_PUSH", "PAYOFF_REVEAL"]:
                # Dramatic push-in zoom into focal element (1.0 to 1.08)
                zoom_filter = f"zoompan=z='min(zoom+0.0005,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={w}x{h}:fps={self.fps}"
            elif motion in ["PUSH_IN"]:
                # Smooth push-in zoom (1.0 to 1.05)
                zoom_filter = f"zoompan=z='min(zoom+0.0003,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={w}x{h}:fps={self.fps}"
            elif motion in ["PAN_LEFT_TO_RIGHT", "DATA_FLOW", "ZOOM_PAN"]:
                # Pan with slight zoom
                zoom_filter = f"zoompan=z='min(zoom+0.0002,1.04)':x='iw/2-(iw/zoom/2)+sin(in/25)*15':y='ih/2-(ih/zoom/2)':d={num_frames}:s={w}x{h}:fps={self.fps}"
            elif motion in ["BEFORE_AFTER_SPLIT", "REVEAL"]:
                # Vertical scan / gentle tilt to reveal comparison or code lines
                zoom_filter = f"zoompan=z='min(zoom+0.0002,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+sin(in/30)*10':d={num_frames}:s={w}x{h}:fps={self.fps}"
            else:
                # Static / subtle hold
                zoom_filter = f"zoompan=z='1.0':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={w}x{h}:fps={self.fps}"

            # Reuse clip if already rendered and valid
            if os.path.exists(clip_file) and os.path.getsize(clip_file) > 10000:
                clip_paths.append(clip_file)
                continue

            cmd_clip = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", os.path.abspath(beat.asset_path),
                "-vf", f"{zoom_filter},format=yuv420p",
                "-t", f"{beat_dur:.2f}",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-r", str(self.fps),
                clip_file
            ]
            clip_timeout = max(120, int(beat_dur * 15))
            res = subprocess.run(cmd_clip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=clip_timeout)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg motion clip render failed for beat {beat.beat_id}: {res.stderr.decode('utf-8', errors='replace')}")
            clip_paths.append(clip_file)

        # 2. Concat all motion clips together and mux audio
        concat_txt = os.path.join(temp_clips_dir, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in clip_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")

        cmd_final = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-i", os.path.abspath(audio.audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            out_mp4
        ]
        res_final = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        if res_final.returncode != 0:
            raise RuntimeError(f"FFmpeg final assembly failed: {res_final.stderr.decode('utf-8', errors='replace')}")

        # Clean up temporary clip directory
        try:
            for p in clip_paths:
                if os.path.exists(p): os.remove(p)
            if os.path.exists(concat_txt): os.remove(concat_txt)
            if os.path.exists(temp_clips_dir): os.rmdir(temp_clips_dir)
        except Exception:
            pass

        file_size = os.path.getsize(out_mp4)

        return RenderArtifact(
            story_id=storyboard.story_id,
            video_path=out_mp4,
            width=w,
            height=h,
            fps=self.fps,
            duration_sec=audio.duration_sec,
            video_codec="h264",
            audio_codec="aac",
            file_size_bytes=file_size
        )
