# Steganography and Encoding Challenges Write-Up

## Overview

This write-up documents the investigation and solution of three artifact-analysis challenges:

1. Recovering a Morse-code message from `Audio.wav`
2. Repairing and examining a corrupted JPEG named `Cat.jpg`
3. Decoding a layered transmission from `Encoded_Dump.txt`

The work was performed in the supplied Kali Linux lab environment.

---

## Challenge 1 — Morse Code Audio

### Scenario

An audio file named `Audio.wav` was recovered from:

```text
/root/Stego Artifacts/Audio.wav
```

The audio contained a message transmitted using Morse code. The Morse transmission decoded into a stream of binary digits, which then had to be converted from binary to ASCII.

### Initial analysis

The audio was uploaded to the adaptive Morse decoder at:

```text
https://morsecode.world/international/decoder/audio-decoder-adaptive.html
```

The initial result contained valid `0` and `1` characters mixed with recognition errors such as letters, symbols, and repeated `5` characters. These errors were produced because the automatic decoder occasionally misclassified tone lengths or gaps.

### Decoding method

The intended process was:

```text
Audio tones → Morse code → Binary digits → 8-bit ASCII
```

After correcting the incorrectly recognized Morse characters, the binary data was divided into groups of eight bits. Each byte was converted to its ASCII character.

Example:

```text
01100110 → f
01101100 → l
01100001 → a
01100111 → g
01111011 → {
```

The decoded plaintext formed the complete flag.

### Answer

```text
flag{binary_audio_secrets}
```

---

## Challenge 2 — Corrupted JPEG Header

### Scenario

A suspicious image named `Cat.jpg` appeared to be an ordinary cat image, but analysis tools initially failed to recognize it as a valid JPEG.

### Inspecting the file header

The first 32 bytes were examined with:

```bash
xxd -l 32 Cat.jpg
```

The beginning of the file was:

```text
00 D8 FF E0
```

Running ExifTool confirmed that the file was malformed:

```bash
exiftool Cat.jpg
```

Result:

```text
Error: File format error
```

### Identifying the correct JPEG/JFIF signature

A JPEG File Interchange Format file normally begins with:

```text
FF D8 FF E0
```

The markers mean:

| Bytes | Meaning |
|---|---|
| `FF D8` | Start of Image (SOI) |
| `FF E0` | JFIF APP0 marker |

The first byte had therefore been changed from `FF` to `00`.

### Repairing the image

A copy was created to preserve the original evidence:

```bash
cp Cat.jpg Cat-Fixed.jpg
```

The corrupted first byte was replaced:

```bash
printf '\xff' | dd of=Cat-Fixed.jpg bs=1 seek=0 count=1 conv=notrunc
```

The repaired file was checked again:

```bash
xxd -l 16 Cat-Fixed.jpg
file Cat-Fixed.jpg
exiftool Cat-Fixed.jpg
```

ExifTool then recognized it as a valid JPEG/JFIF image.

### Header-marker answer

```text
FF D8 FF E0
```

---

## Challenge 3 — Hidden Data in `Cat.jpg`

### Searching for embedded content

The repaired image was checked with Binwalk:

```bash
binwalk Cat-Fixed.jpg
```

Binwalk only identified the JPEG structure, indicating that the secret was not simply appended to the end of the file.

Steganography analysis recovered an embedded file named:

```text
flag.txt
```

The extracted file contained:

```text
Q1RGe3N0ZWcwXzFzX2NvMGx9
```

The characters and structure indicated Base64 encoding.

### Decoding the extracted data

The value was decoded with:

```bash
echo 'Q1RGe3N0ZWcwXzFzX2NvMGx9' | base64 -d
```

### Answer

```text
CTF{steg0_1s_co0l}
```

---

## Challenge 4 — Layered Encoded Transmission

### Scenario

`Encoded_Dump.txt` contained three candidate transmission strings and two hints:

```text
--- BEGIN TRANSMISSION ---
Z3ZkRG9mSXdlTFVRazF2
2A6fz3V1RQkk4RgpctzF5bPYFCaCXsLLb7Jxot4
R3E5aUR0YlFoeFdFeVla
LmVubyB0c3VqIHNpIGV1cnQgLHN5b2NlZCBlcmEgb3dU
UHJvY2VzczogQmFzZTU4IOKGkiBST1QxMyDihpIgQkFTRTY0IOKGkiBYT1IgKEhleCBLZXk6IDM0MjEyMCk
--- END TRANSMISSION ---
```

### Decoding the first hint

The first hint was Base64-decoded and then reversed. It revealed:

```text
Two are decoys, true is just one.
```

Only the middle candidate was valid Base58 text:

```text
2A6fz3V1RQkk4RgpctzF5bPYFCaCXsLLb7Jxot4
```

The other two candidates contained characters that are excluded from the Base58 alphabet, such as lowercase `l` and the digit `0`.

### Decoding the second hint

Base64-decoding the second hint revealed the required recipe:

```text
Process: Base58 → ROT13 → Base64 → XOR (Hex Key: 342120)
```

Therefore, the correct multiple-choice answer was:

```text
Base58 → ROT13 → Base64 → XOR (Hex Key: 342120)
```

### Applying the layers

The middle candidate was processed in the stated order:

1. Decode from Base58.
2. Apply ROT13.
3. Decode from Base64.
4. XOR the resulting bytes with the repeating hexadecimal key `34 21 20`.

The intermediate values were:

```text
After Base58: pz1up1c2KJWHr1A5IJWVsHE2HJIq
After ROT13:  cm1hc1p2XWJUe1N5VWJIfUR2UWVd
```

After Base64 decoding and XOR processing, the plaintext flag was recovered.

### Answer

```text
FLAG{ViCtOrYaChIeVeD}
```

---

## Final Answers

| Challenge | Answer |
|---|---|
| Morse audio flag | `flag{binary_audio_secrets}` |
| JPEG/JFIF starting marker | `FF D8 FF E0` |
| Cat image steganography flag | `CTF{steg0_1s_co0l}` |
| Layered decoding sequence | `Base58 → ROT13 → Base64 → XOR (Hex Key: 342120)` |
| Layered transmission flag | `FLAG{ViCtOrYaChIeVeD}` |

## Key Lessons

- Always inspect file signatures when an extension and detected file type do not agree.
- Work on a copy of forensic evidence instead of modifying the original artifact.
- `file`, `xxd`, `exiftool`, `binwalk`, and steganography tools complement one another.
- Extracted strings may still require an additional encoding step such as Base64.
- Hints can themselves be encoded, reversed, or used to identify decoy data.
- Automated audio decoders can introduce recognition errors; validate binary output in eight-bit groups before converting it to ASCII.
