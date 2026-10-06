python3 - <<'PY'
import wave
import numpy as np

FILE = "Audio.wav"

with wave.open(FILE, "rb") as w:
    rate = w.getframerate()
    channels = w.getnchannels()
    width = w.getsampwidth()
    raw = w.readframes(w.getnframes())

types = {1: np.uint8, 2: np.int16, 4: np.int32}
audio = np.frombuffer(raw, dtype=types[width]).astype(float)

if width == 1:
    audio -= 128

if channels > 1:
    audio = audio.reshape(-1, channels).mean(axis=1)

# Measure audio energy in 5 ms frames
frame_size = max(1, int(rate * 0.005))
audio = audio[:len(audio) // frame_size * frame_size]
frames = audio.reshape(-1, frame_size)
energy = np.sqrt(np.mean(frames ** 2, axis=1))

low = np.percentile(energy, 10)
high = np.percentile(energy, 90)
tone_on = energy > ((low + high) / 2)

# Run-length encoding
runs = []
start = 0

for i in range(1, len(tone_on)):
    if tone_on[i] != tone_on[start]:
        runs.append((bool(tone_on[start]), i - start))
        start = i

runs.append((bool(tone_on[start]), len(tone_on) - start))

# Collect tone lengths and ignore tiny glitches
tone_lengths = np.array(
    [length for state, length in runs if state and length >= 2],
    dtype=float
)

# Separate dots and dashes using two-cluster fitting
c1, c2 = tone_lengths.min(), tone_lengths.max()

for _ in range(30):
    d1 = np.abs(tone_lengths - c1)
    d2 = np.abs(tone_lengths - c2)
    group1 = tone_lengths[d1 <= d2]
    group2 = tone_lengths[d1 > d2]

    if len(group1):
        c1 = group1.mean()
    if len(group2):
        c2 = group2.mean()

dot, dash = sorted((c1, c2))
cutoff = (dot + dash) / 2

symbols = "".join(
    "." if length < cutoff else "-"
    for length in tone_lengths
)

print("Tone symbols detected:", len(symbols))
print("Dot length:", round(dot, 2))
print("Dash length:", round(dash, 2))

# Morse 1 = .----
# Morse 0 = -----
targets = {"0": "-----", "1": ".----"}

for offset in range(5):
    groups = [
        symbols[i:i+5]
        for i in range(offset, len(symbols) - 4, 5)
    ]

    bits = ""
    errors = 0

    for group in groups:
        distances = {
            bit: sum(a != b for a, b in zip(group, pattern))
            for bit, pattern in targets.items()
        }
        bit = min(distances, key=distances.get)
        bits += bit
        errors += distances[bit]

    for bit_offset in range(8):
        candidate = bits[bit_offset:]
        candidate = candidate[:len(candidate) // 8 * 8]

        if not candidate:
            continue

        decoded = "".join(
            chr(int(candidate[i:i+8], 2))
            for i in range(0, len(candidate), 8)
        )

        printable = sum(32 <= ord(c) <= 126 for c in decoded)

        if "flag{" in decoded.lower() or printable >= len(decoded) * 0.9:
            print("\nPossible result")
            print("Morse offset:", offset)
            print("Binary offset:", bit_offset)
            print("Recognition errors:", errors)
            print("Binary:", candidate)
            print("Decoded:", repr(decoded))
PY
