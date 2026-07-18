"""Generate a short test WAV tone (stdlib only) to prove the audio import
pipe end to end, before wiring in real TTS output."""
import wave
import struct
import math

def make_beep(path, freq=440.0, duration=1.0, sample_rate=44100, volume=0.3):
    n_samples = int(duration * sample_rate)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            # Fade in/out 50ms to avoid a click
            fade = min(1.0, t / 0.05, (duration - t) / 0.05)
            sample = int(volume * fade * 32767 * math.sin(2 * math.pi * freq * t))
            frames += struct.pack("<h", sample)
        wav.writeframes(bytes(frames))

make_beep(r"C:\temp\test_beep_440hz.wav")
print("Wrote C:\\temp\\test_beep_440hz.wav")
