from pathlib import Path
import pandas as pd
import json

def validate_dataset():
    """Check that all expected files exist and metadata is complete."""
    
    processed_dir = Path("data/accented/processed")
    metadata_file = processed_dir / "metadata.csv"
    
    if not metadata_file.exists():
        print(" metadata.csv not found! Run preprocessing first.")
        return False
    
    df = pd.read_csv(metadata_file)
    
    print("Dataset Validation Report")
    print("=" * 50)
    
    # Check for 10 speakers × 3 sentences = 30 files
    expected_files = 30
    actual_files = len(df)
    
    print(f"\nFile Count:")
    print(f"  Expected: {expected_files}")
    print(f"  Found: {actual_files}")
    
    if actual_files < expected_files:
        print(f"  Missing {expected_files - actual_files} files!")
    else:
        print(f" Complete!")
    
    # Check each speaker has 3 sentences
    print(f"\nSpeakers:")
    speaker_counts = df.groupby('speaker_id').size()
    for speaker, count in speaker_counts.items():
        status = "✓" if count == 3 else "⚠"
        print(f"  {status} {speaker}: {count}/3 sentences")
    
    # Check metadata completeness
    print(f"\n📝 Metadata Completeness:")
    required_fields = ['age_group', 'gender', 'accent_type', 'native_language', 'region']
    for field in required_fields:
        missing = df[field].isna().sum() + (df[field] == '').sum()
        status = "✓" if missing == 0 else "⚠"
        print(f"  {status} {field}: {len(df) - missing}/{len(df)} complete")
    
    # Check audio files exist
    print(f"\n🔊 Audio Files:")
    missing_audio = 0
    for _, row in df.iterrows():
        audio_path = Path("data") / row['audio_file']
        if not audio_path.exists():
            print(f"  ⚠ Missing: {audio_path}")
            missing_audio += 1
    
    if missing_audio == 0:
        print(f"  ✓ All {len(df)} audio files found!")
    else:
        print(f"  ⚠ {missing_audio} audio files missing!")
    
    # Summary statistics
    print(f"\nDataset Statistics:")
    print(f"\nAccent Distribution:")
    print(df['accent_type'].value_counts())
    print(f"\nNative Language Distribution:")
    print(df['native_language'].value_counts())
    print(f"\nRegion Distribution:")
    print(df['region'].value_counts())
    
    return missing_audio == 0 and actual_files >= expected_files


if __name__ == "__main__":
    validate_dataset()