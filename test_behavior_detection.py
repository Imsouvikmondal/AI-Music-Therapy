"""
Test the behavior detection with the example video of autistic child flapping hands.
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(repo_root))

from emotion_behavior.motion_detector import MotionBehaviorDetector


def test_behavior_detection():
    """Test behavior detection on the example video."""
    video_path = r"c:\Users\Srinjoy\Downloads\Flapping Hands in Autistic child.mp4"
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return False
    
    print(f"📹 Testing behavior detection on: {video_path.name}")
    print(f"   File size: {video_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        detector = MotionBehaviorDetector()
        print("✅ MotionBehaviorDetector initialized successfully")
        
        # Analyze the video
        print("\n🔍 Analyzing video... (this may take a moment)")
        analysis = detector.analyze_video(
            video_path,
            max_frames=120,
            analysis_seconds=10,
        )
        
        print("\n📊 Analysis Results:")
        print(f"   Detected Label: {analysis.label}")
        print(f"   Confidence: {analysis.confidence:.2%}")
        print(f"   Motion Intensity: {analysis.motion_intensity:.2%}")
        print(f"   Arm Movement: {analysis.arm_movement_intensity:.2%}")
        print(f"   Flapping/Repetition Score: {analysis.repetition_score:.2%}")
        print(f"   Frames Analyzed: {analysis.frames_analyzed}")
        
        # Provide interpretation
        print("\n📝 Interpretation:")
        if analysis.label == "normal":
            print("   → Classified as NORMAL behavior (typically calm/stimming)")
        else:
            print("   → Classified as FIGHT behavior (aggressive/intense movement)")
        
        if analysis.repetition_score > 0.5:
            print("   → HIGH repetitive movement detected (consistent with flapping)")
        
        print("\n✅ Behavior detection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_behavior_detection()
    sys.exit(0 if success else 1)
