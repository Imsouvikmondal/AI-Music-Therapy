"""Debug script to analyze the flapping video frame by frame."""

import sys
from pathlib import Path
import cv2
import numpy as np

video_path = r"c:\Users\Srinjoy\Downloads\Flapping Hands in Autistic child.mp4"

# Open video and get properties
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ Cannot open video")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"📹 Video Properties:")
print(f"   Total Frames: {total_frames}")
print(f"   FPS: {fps}")
print(f"   Resolution: {width}x{height}")
print(f"   Duration: {total_frames/fps:.1f} seconds")

# Analyze first few frames for motion
print(f"\n🔍 Analyzing motion...")

frames = []
ret = True
count = 0
while ret and count < min(120, total_frames):
    ret, frame = cap.read()
    if ret:
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    count += 1

cap.release()

if len(frames) < 2:
    print("❌ Could not extract frames")
    sys.exit(1)

print(f"   Extracted: {len(frames)} frames")

# Analyze optical flow
motions = []
for i in range(1, min(len(frames), 50)):
    prev = frames[i-1].astype(np.float32)
    curr = frames[i].astype(np.float32)
    
    diff = cv2.absdiff(prev, curr)
    motion = np.mean(diff)
    motions.append(motion)

if motions:
    print(f"\n📊 Motion Analysis:")
    print(f"   Motion values: {motions[:10]}")
    print(f"   Average motion: {np.mean(motions):.2f}")
    print(f"   Max motion: {np.max(motions):.2f}")
    print(f"   Min motion: {np.min(motions):.2f}")
    print(f"   Std deviation: {np.std(motions):.2f}")
    
    # Check for oscillation
    diffs = np.abs(np.diff(motions))
    print(f"\n🔄 Repetition Analysis:")
    print(f"   Motion differences: {diffs[:5]}")
    print(f"   Avg difference: {np.mean(diffs):.2f}")
    print(f"   Std of differences: {np.std(diffs):.2f}")
    
    if np.mean(diffs) > 0.1:
        rep_score = 1.0 - min(1.0, np.std(diffs) / (np.mean(diffs) + 1e-6))
        print(f"   Repetition Score: {rep_score:.2%}")
