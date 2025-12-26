import tarfile
import urllib.request
from pathlib import Path

import pandas as pd
from tqdm import tqdm


LIBRISPEECH_URL = "https://www.openslr.org/resources/12/test-clean.tar.gz"


def download_librispeech_test_clean(data_dir="data/raw"):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    tar_path = data_dir / "test-clean.tar.gz"
    extract_dir = data_dir / "LibriSpeech"

    if not tar_path.exists():
        urllib.request.urlretrieve(LIBRISPEECH_URL, tar_path)

    if not extract_dir.exists():
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(data_dir)

    return extract_dir / "test-clean"


def process_librispeech_transcripts(librispeech_dir, output_dir="data/clean"):
    librispeech_dir = Path(librispeech_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = []

    transcript_files = librispeech_dir.rglob("*.trans.txt")

    for trans_file in tqdm(list(transcript_files), desc="Processing transcripts"):
        with open(trans_file) as f:
            for line in f:
                utt_id, transcript = line.strip().split(" ", 1)
                audio_file = trans_file.parent / f"{utt_id}.flac"

                if audio_file.exists():
                    speaker, chapter, _ = utt_id.split("-")
                    samples.append({
                        "utterance_id": utt_id,
                        "audio_path": str(audio_file.relative_to(librispeech_dir.parent)),
                        "transcript": transcript,
                        "speaker_id": speaker,
                        "chapter_id": chapter,
                    })

    df = pd.DataFrame(samples)
    df.to_csv(output_dir / "metadata.csv", index=False)
    return df


def select_subset(df, n_samples=100, output_file="data/clean/selected_samples.csv"):
    speakers = df["speaker_id"].unique()
    per_speaker = max(1, n_samples // len(speakers))

    subset = (
        df.groupby("speaker_id", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), per_speaker), random_state=42))
    )

    if len(subset) < n_samples:
        remaining = df.loc[~df.index.isin(subset.index)]
        subset = pd.concat([
            subset,
            remaining.sample(n_samples - len(subset), random_state=42)
        ])

    subset = subset.sample(n_samples, random_state=42)
    subset.to_csv(output_file, index=False)
    return subset


def main():
    librispeech_dir = download_librispeech_test_clean()
    metadata = process_librispeech_transcripts(librispeech_dir)
    select_subset(metadata, n_samples=100)


if __name__ == "__main__":
    main()
