from datasets import load_dataset
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import soundfile as sf
import numpy as np

def download_common_voice_accents(output_dir="data/accented", n_samples_per_accent=30):
    """
    Download Common Voice samples with different accents.
    Using HuggingFace datasets library.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("STEP 2: Acquiring Accented Speech Data")
    print("="*60)
    
    # Common Voice - English (using latest version)
    print("\nLoading Common Voice dataset (this may take a few minutes)...")
    print("We'll use the 'test' split which is smaller and faster to download.\n")
    
    # Load dataset - removed trust_remote_code parameter
    dataset = load_dataset("mozilla-foundation/common_voice_17_0", 
                          "en", 
                          split="test")
    
    print(f"✓ Loaded {len(dataset)} samples")
    
    # Common Voice has accent information in 'accent' field
    # Let's see what accents are available
    accents = {}
    for item in tqdm(dataset, desc="Cataloging accents"):
        accent = item.get('accent', 'unknown')
        if accent not in accents:
            accents[accent] = []
        if len(accents[accent]) < n_samples_per_accent:
            accents[accent].append(item)
    
    print(f"\n✓ Found {len(accents)} different accents")
    print("\nAccent distribution:")
    for accent, samples in sorted(accents.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  - {accent}: {len(samples)} samples")
    
    # Select target accents (you can modify this)
    target_accents = ['us', 'england', 'indian', 'african', 'australian', 'canada']
    
    all_samples = []
    
    for accent in target_accents:
        if accent not in accents:
            print(f"\n⚠ Warning: '{accent}' accent not found, skipping...")
            continue
        
        accent_dir = output_dir / accent
        accent_dir.mkdir(exist_ok=True)
        
        print(f"\nProcessing {accent} accent ({len(accents[accent])} samples)...")
        
        for idx, item in enumerate(tqdm(accents[accent], desc=f"{accent}")):
            # Get audio data
            audio = item['audio']
            audio_array = audio['array']
            sample_rate = audio['sampling_rate']
            
            # Get transcript
            transcript = item['sentence']
            
            # Save audio file
            filename = f"{accent}_{idx:03d}.wav"
            audio_path = accent_dir / filename
            
            sf.write(audio_path, audio_array, sample_rate)
            
            all_samples.append({
                'utterance_id': f"{accent}_{idx:03d}",
                'audio_path': str(audio_path.relative_to(Path('data'))),
                'transcript': transcript,
                'accent': accent,
                'speaker_id': item.get('client_id', 'unknown'),
                'age': item.get('age', 'unknown'),
                'gender': item.get('gender', 'unknown')
            })
    
    # Save metadata
    df = pd.DataFrame(all_samples)
    metadata_path = output_dir / "metadata.csv"
    df.to_csv(metadata_path, index=False)
    
    print(f"\n✓ Saved {len(all_samples)} accented samples")
    print(f"✓ Metadata saved to {metadata_path}")
    
    print("\n" + "="*60)
    print("✓ ACCENTED DATA ACQUISITION COMPLETE!")
    print("="*60)
    
    return df

if __name__ == "__main__":
    download_common_voice_accents(n_samples_per_accent=30)