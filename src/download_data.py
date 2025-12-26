import os
import tarfile
import urllib.request
from pathlib import Path
import shutil
from tqdm import tqdm
import json
import pandas as pd
class DownloadProgressBar(tqdm):
    """Progress bar for downloads."""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_url(url, output_path):
    """Download file with progress bar."""
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path,
                                  reporthook=t.update_to)

def download_librispeech_test_clean(data_dir="data/raw"):
    """
    Download LibriSpeech test-clean dataset.
    This contains ~5 hours of clean speech with transcriptions.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # LibriSpeech test-clean URL
    url = "https://www.openslr.org/resources/12/test-clean.tar.gz"
    tar_path = data_dir / "test-clean.tar.gz"
    
    print("Downloading LibriSpeech test-clean dataset...")
    print(f"Size: ~346 MB")
    print(f"This will take a few minutes depending on your connection.\n")
    
    # Download
    if not tar_path.exists():
        download_url(url, tar_path)
        print(f"\n✓ Downloaded to {tar_path}")
    else:
        print(f"✓ Already downloaded: {tar_path}")
    
    # Extract
    extract_dir = data_dir / "LibriSpeech"
    if not extract_dir.exists():
        print("\nExtracting archive...")
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(data_dir)
        print(f"✓ Extracted to {extract_dir}")
    else:
        print(f"✓ Already extracted: {extract_dir}")
    
    return extract_dir / "test-clean"

def process_librispeech_transcripts(librispeech_dir, output_dir="data/clean"):
    """
    Process LibriSpeech data into a clean format.
    LibriSpeech structure:
    - Audio files: speaker_id/chapter_id/speaker_id-chapter_id-utterance_id.flac
    - Transcripts: speaker_id/chapter_id/speaker_id-chapter_id.trans.txt
    """
    librispeech_dir = Path(librispeech_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\nProcessing LibriSpeech transcripts...")
    
    # Find all transcript files
    transcript_files = list(librispeech_dir.rglob("*.trans.txt"))
    
    all_samples = []
    
    for trans_file in tqdm(transcript_files, desc="Processing transcripts"):
        with open(trans_file, 'r') as f:
            for line in f:
                # Format: utterance_id TRANSCRIPT TEXT
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    utterance_id, transcript = parts
                    
                    # Find corresponding audio file
                    audio_file = trans_file.parent / f"{utterance_id}.flac"
                    
                    if audio_file.exists():
                        all_samples.append({
                            'utterance_id': utterance_id,
                            'audio_path': str(audio_file.relative_to(librispeech_dir.parent)),
                            'transcript': transcript,
                            'speaker_id': utterance_id.split('-')[0],
                            'chapter_id': utterance_id.split('-')[1]
                        })
    
    print(f"\n✓ Found {len(all_samples)} audio samples with transcripts")
    
    # Save metadata
    import pandas as pd
    df = pd.DataFrame(all_samples)
    metadata_path = output_dir / "metadata.csv"
    df.to_csv(metadata_path, index=False)
    print(f"✓ Saved metadata to {metadata_path}")
    
    # Also save as JSON for easy reading
    json_path = output_dir / "metadata.json"
    with open(json_path, 'w') as f:
        json.dump(all_samples, f, indent=2)
    
    return df

def select_subset(metadata_df, n_samples=100, output_file="data/clean/selected_samples.csv"):
    """
    Select a subset of samples for the experiment.
    Stratified by speaker to ensure diversity.
    """
    print(f"\nSelecting {n_samples} samples for experiment...")
    
    # Group by speaker and sample proportionally
    samples_per_speaker = metadata_df.groupby('speaker_id').size()
    
    # Aim for diverse speakers
    selected = metadata_df.groupby('speaker_id', group_keys=False).apply(
        lambda x: x.sample(min(len(x), max(1, n_samples // len(samples_per_speaker))))
    )
    
    # If we need more samples, sample randomly from the rest
    if len(selected) < n_samples:
        remaining = metadata_df[~metadata_df.index.isin(selected.index)]
        additional = remaining.sample(min(n_samples - len(selected), len(remaining)))
        selected = pd.concat([selected, additional])
    else:
        selected = selected.sample(n_samples)
    
    selected.to_csv(output_file, index=False)
    print(f"✓ Selected {len(selected)} samples from {selected['speaker_id'].nunique()} speakers")
    print(f"✓ Saved to {output_file}")
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"  - Total samples: {len(selected)}")
    print(f"  - Unique speakers: {selected['speaker_id'].nunique()}")
    print(f"  - Unique chapters: {selected['chapter_id'].nunique()}")
    
    return selected

def main():
    """Main function to download and prepare clean speech data."""
    print("="*60)
    print("STEP 1: Acquiring Clean Speech Data")
    print("="*60)
    
    # Download LibriSpeech
    librispeech_path = download_librispeech_test_clean()
    
    # Process transcripts
    metadata_df = process_librispeech_transcripts(librispeech_path)
    
    # Select experimental subset (start with 100 samples)
    selected_df = select_subset(metadata_df, n_samples=100)
    
    print("\n" + "="*60)
    print("✓ CLEAN DATA ACQUISITION COMPLETE!")
    print("="*60)
    print(f"\nNext steps:")
    print(f"1. Review data/clean/selected_samples.csv")
    print(f"2. Run Step 2 to download accented speech data")
    print(f"3. Run Step 3 to create noisy versions")
    
    return selected_df

if __name__ == "__main__":
    main()