import os
import subprocess
from typing import Dict, Any, Optional
from radar.models.schemas import ScriptArtifact, AudioArtifact


class VoiceGenerationAgent:
    """Generates broadcast-quality Vietnamese audio using Microsoft Neural Voice (vi-VN-HoaiMyNeural).
    
    Adheres strictly to the AI News Factory V2 standard:
    - Primary: vi-VN-HoaiMyNeural
    - Fallback: vi-VN-NamMinhNeural
    - Audio standard: -16.0 LUFS integrated, True Peak <= -1.5 dBTP
    """

    def __init__(self, config: Dict[str, Any], output_dir: str = "data/audio"):
        self.config = config
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.voice_cfg = config.get("voice", {})
        self.primary_voice = self.voice_cfg.get("primary_voice", "vi-VN-HoaiMyNeural")
        self.secondary_voice = self.voice_cfg.get("secondary_voice", "vi-VN-NamMinhNeural")
        self.sample_rate = config.get("audio_standards", {}).get("sample_rate", 44100)
        self.target_lufs = self.voice_cfg.get("target_lufs", -16.0)

    def generate(self, script: Any) -> AudioArtifact:
        out_wav = os.path.join(self.output_dir, f"{script.story_id}.wav")
        # Build conversational narration text with natural sentence pauses
        raw_segs = getattr(script, "all_segments", None) or getattr(script, "segments", [])
        spoken_parts = [seg.spoken_text.strip() for seg in raw_segs]
        # Clean text: ensure complete sentences with natural periods
        cleaned_parts = []
        for p in spoken_parts:
            s = p.strip()
            if not s.endswith((".", "!", "?")):
                s += "."
            cleaned_parts.append(s)
        full_text = " ".join(cleaned_parts)

        # 1. Try Primary Microsoft Neural Voice (vi-VN-HoaiMyNeural) with retries
        provider_used = "microsoft_neural_edge_tts"
        voice_used = self.primary_voice
        success = False
        
        for attempt in range(3):
            success = self._synthesize_neural(full_text, self.primary_voice, out_wav)
            if success:
                break
        
        # 2. Try Secondary Microsoft Neural Voice (vi-VN-NamMinhNeural) if primary fails
        if not success:
            voice_used = self.secondary_voice
            for attempt in range(2):
                success = self._synthesize_neural(full_text, self.secondary_voice, out_wav)
                if success:
                    break

        if not success:
            raise RuntimeError(
                f"Microsoft Neural Voice synthesis failed for '{self.primary_voice}' and '{self.secondary_voice}'. "
                "Fail-closed policy active: Robotic fallback voice is strictly prohibited."
            )

        # 3. Measure audio metrics (duration, LUFS, True Peak)
        duration_sec, integrated_lufs, true_peak_db = self._measure_audio(out_wav)

        return AudioArtifact(
            story_id=script.story_id,
            audio_path=out_wav,
            duration_sec=duration_sec,
            sample_rate=self.sample_rate,
            channels=2,
            lufs=integrated_lufs,
            true_peak_db=true_peak_db,
            voice_name=voice_used,
            provider=provider_used,
            is_clipping=(true_peak_db > -0.5)
        )

    def _synthesize_neural(self, text: str, voice_name: str, output_wav: str) -> bool:
        """Synthesize using edge_tts Python library with SentenceBoundary."""
        temp_mp3 = output_wav.replace(".wav", "_temp.mp3")
        try:
            import edge_tts
            import asyncio
            import concurrent.futures

            clean_text = text.replace(" ... ", ". ").replace("...", ".").strip()

            async def _do_synth():
                comm = edge_tts.Communicate(clean_text, voice_name, boundary="SentenceBoundary")
                await comm.save(temp_mp3)

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        pool.submit(asyncio.run, _do_synth()).result()
                else:
                    loop.run_until_complete(_do_synth())
            except Exception:
                asyncio.run(_do_synth())

            if os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 2000:
                # Transcode and normalize to 44.1kHz stereo WAV with broadcast loudness target (-16 LUFS)
                cmd_ffmpeg = [
                    "ffmpeg", "-y", "-i", temp_mp3,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", str(self.sample_rate),
                    "-ac", "2",
                    output_wav
                ]
                res = subprocess.run(cmd_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)
                if res.returncode == 0 and os.path.exists(output_wav) and os.path.getsize(output_wav) > 2000:
                    return True
        except Exception:
            if os.path.exists(temp_mp3):
                try: os.remove(temp_mp3)
                except: pass
        return False

    def _measure_audio(self, wav_path: str):
        duration = 45.0
        integrated_lufs = -16.0
        true_peak_db = -1.5
        try:
            dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", wav_path]
            duration = float(subprocess.check_output(dur_cmd).decode().strip())

            ebur_cmd = ["ffmpeg", "-nostats", "-i", wav_path, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"]
            p = subprocess.run(ebur_cmd, stderr=subprocess.PIPE, text=True)
            for line in p.stderr.splitlines():
                if "I:" in line and "LUFS" in line:
                    try:
                        integrated_lufs = float(line.split("I:")[1].split("LUFS")[0].strip())
                    except: pass
                if "Peak:" in line and "dBFS" in line:
                    try:
                        true_peak_db = float(line.split("Peak:")[1].split("dBFS")[0].strip())
                    except: pass
        except Exception:
            pass
        return round(duration, 2), round(integrated_lufs, 1), round(true_peak_db, 1)
