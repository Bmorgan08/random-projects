import librosa
import numpy as np
import sounddevice as sd
import sys

file = sys.argv[1]

y, sr = librosa.load(file, sr=None)

FRAME_SIZE = 1024
HOP_SIZE = 512

def bit_reverse(x, bits):
    result = 0
    for _ in range(bits):
        result = (result << 1) | (x & 1)
        x >>= 1
    return result

def fft(signal):
    N = len(signal)

    if N & (N - 1):
        raise ValueError("FFT size must be power of 2")

    bits = int(np.log2(N))

    data = [0] * N
    for i in range(N):
        j = bit_reverse(i, bits)
        data[j] = complex(signal[i], 0)

    size = 2
    while size <= N:
        half = size // 2
        step = -2j * np.pi / size

        for start in range(0, N, size):
            for k in range(half):
                twiddle = np.exp(step * k) * data[start + k + half]

                temp = data[start + k]

                data[start + k] = temp + twiddle
                data[start + k + half] = temp - twiddle

        size *= 2

    return data

def ifft(spectrum):
    N = len(spectrum)

    conj = [x.conjugate() for x in spectrum]
    transformed = fft(conj)

    return np.array([x.conjugate().real / N for x in transformed])

def frame_audio(y, frame_size, hop_size):
    frames = []
    for i in range(0, len(y) - frame_size, hop_size):
        frames.append(y[i:i + frame_size])
    return frames

def hann_window(N):
    w = np.zeros(N)
    for n in range(N):
        w[n] = 0.5 * (1 - np.cos(2 * np.pi * n / (N - 1)))
    return w

frames = frame_audio(y, FRAME_SIZE, HOP_SIZE)
window = hann_window(FRAME_SIZE)

output = np.zeros(len(y))
window_sum = np.zeros(len(y))

print(f"Processing {len(frames)} frames...")

for i, frame in enumerate(frames):

    if i % 50 == 0:
        print(f"Frame {i}/{len(frames)}")

    windowed = frame * window

    spectrum = fft(windowed)

    reconstructed = ifft(spectrum)

    start = i * HOP_SIZE
    end = start + FRAME_SIZE

    output[start:end] += reconstructed
    window_sum[start:end] += window

# -----------------------------
# Normalize overlap-add
# -----------------------------
window_sum[window_sum == 0] = 1
output /= window_sum

# normalize audio amplitude
output /= np.max(np.abs(output))

sd.play(output, sr)
sd.wait()