## Data Organization

Raw recordings were collected with naming convention: `[initial][sentence_number]`
(e.g., j1, j2, j3 for speaker J's three sentences).

These were organized into standardized folders using:
```bash
python src/0_organize_recordings.py
```

This script:
- Groups files by speaker initial
- Renames to `speaker_XX_sentY.format`
- Creates metadata templates