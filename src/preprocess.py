from pathlib import Path
import json
import subprocess
import pandas as pd
import shutil  # Add this import

def preprocess_accented_recordings():
    """
    Standardize all audio files to 16kHz mono WAV format
    and create metadata CSV for analysis.
    """
    
    organized_dir = Path("data/accented/organized")
    processed_dir = Path("data/accented/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Load reference sentences
    with open(organized_dir / "reference_sentences.json", 'r') as f:
        sentences = json.load(f)
    
    metadata = []
    
    # Get all speaker directories
    speaker_dirs = sorted([d for d in organized_dir.iterdir() 
                          if d.is_dir() and d.name.startswith("speaker_")])
    
    print(f"Processing {len(speaker_dirs)} speakers...\n")
    
    for speaker_dir in speaker_dirs:
        speaker_id = speaker_dir.name
        print(f"Processing {speaker_id}...")
        
        # Load speaker info
        with open(speaker_dir / "speaker_info.json", 'r') as f:
            speaker_info = json.load(f)
        
        # Create processed speaker directory
        processed_speaker_dir = processed_dir / speaker_id
        processed_speaker_dir.mkdir(exist_ok=True)
        
        audio_files = []
        for ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
            audio_files.extend(list(speaker_dir.glob(f'*{ext}')))
        
        for audio_file in sorted(audio_files):
            # Extract sentence number from filename
            parts = audio_file.stem.split('_')
            if len(parts) >= 3 and parts[2].startswith('sent'):
                sent_key = parts[2]  # sent1, sent2, sent3 
                sent_num = sent_key.replace('sent', '')
                sentence_key = f"sentence{sent_num}"
                
                if sentence_key in sentences:
    
                    output_file = processed_speaker_dir / f"{speaker_id}_sent{sent_num}.wav"
                    
                    # Convert using ffmpeg
                    try:
                        subprocess.run([
                            'ffmpeg', '-i', str(audio_file),
                            '-ar', '16000',  # 16kHz sample rate
                            '-ac', '1',       # Mono
                            '-y',             # Overwrite
                            str(output_file)
                        ], check=True, capture_output=True)
                        
                        print(f"  {audio_file.name} -> {output_file.name}")
                        
                        # Add to metadata
                        metadata.append({
                            'speaker_id': speaker_id,
                            'name_initial': speaker_info.get('name_initial', ''),
                            'sentence_num': sent_num,
                            'sentence_key': sentence_key,
                            'reference_text': sentences[sentence_key],
                            'audio_file': str(output_file.relative_to(Path("data"))),
                            'age_group': speaker_info.get('age_group', ''),
                            'gender': speaker_info.get('gender', ''),
                            'accent_type': speaker_info.get('accent_type', ''),
                            'native_language': speaker_info.get('native_language', ''),
                            'region': speaker_info.get('region', ''),
                            'condition': 'accented'  
                        })
                        
                    except subprocess.CalledProcessError as e:
                        print(f"  Error processing {audio_file.name}: {e}")
                else:
                    print(f"   Skipping {audio_file.name} - no matching sentence")
        
        # Copy speaker info to processed directory (Windows-compatible)
        shutil.copy2(
            speaker_dir / "speaker_info.json",
            processed_speaker_dir / "speaker_info.json"
        )
        
        print()
    
    # Save metadata CSV
    df = pd.DataFrame(metadata)
    metadata_file = processed_dir / "metadata.csv"
    df.to_csv(metadata_file, index=False)
    
    print(f"Preprocessing complete!")
    print(f"Processed {len(metadata)} audio files")
    print(f"Metadata saved to: {metadata_file}")
    print(f"\nSummary:")
    print(df.groupby(['accent_type', 'native_language']).size())
    
    return df


if __name__ == "__main__":
    
    preprocess_accented_recordings()