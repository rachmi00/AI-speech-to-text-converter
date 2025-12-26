from pathlib import Path
import json
import shutil

def organize_existing_recordings():
    """
    Organize existing recordings (j1, j2, j3, b1, b2, b3, etc.) 
    into proper speaker folders with standardized naming.
    """
    
    base_dir = Path("data/accented")
    raw_dir = base_dir  # Where  j1, j2, b1 files are files with initial letter and recording number
    organized_dir = base_dir / "organized"
    organized_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all audio files in the accented folder
    audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(list(raw_dir.glob(f'*{ext}')))
    
    # Group files by speaker initial
    speaker_files = {}
    for file in audio_files:
        # Extract initial and sentence number 
        name = file.stem  
        if len(name) >= 2:
            initial = name[0].lower()  # First character (j, b,etc)
            sentence_num = name[1:]    # Rest of the name (1, 2, 3, etc.)
            
            if initial not in speaker_files:
                speaker_files[initial] = []
            speaker_files[initial].append((sentence_num, file))
    
    # Sort initials alphabetically and assign speaker numbers
    sorted_initials = sorted(speaker_files.keys())
    
    print(f"Found {len(sorted_initials)} speakers: {sorted_initials}")
    print("\nOrganizing files...\n")
    
    # Create reference sentences file
    sentences = {
        "sentence1": "The project was completed after weeks of careful planning and repeated testing",
        "sentence2": "Students discussed complex problems, proposed practical solutions, and presented detailed results",
        "sentence3": "When the instructions were unclear, the team asked questions, adjusted their approach, and continued working"
    }
    sentences_file = organized_dir / "reference_sentences.json"
    with open(sentences_file, 'w') as f:
        json.dump(sentences, f, indent=2)
    
    # Speaker info template
    speaker_template = {
        "speaker_id": "",
        "name_initial": "",
        "age_group": "",  
        "gender": "",  # M, F
        "accent_type": "",  
        "native_language": "",  # French, English, Duala, etc.
        "region": "", 
        "notes": ""
    }
    
    # Organize each speaker's files
    for speaker_num, initial in enumerate(sorted_initials, start=1):
        speaker_id = f"speaker_{speaker_num:02d}"
        speaker_dir = organized_dir / speaker_id
        speaker_dir.mkdir(exist_ok=True)
        
        print(f"Processing {speaker_id} (initial: {initial}):")
        
    
        files = sorted(speaker_files[initial], key=lambda x: x[0])
        
        # Copy and rename files
        for sentence_num, file in files:
          
            try:
                sent_num = int(sentence_num)
                new_name = f"{speaker_id}_sent{sent_num}{file.suffix}"
                dest = speaker_dir / new_name
                
                shutil.copy2(file, dest)
                print(f"  {file.name} -> {new_name}")
            except ValueError:
                print(f"  WARNING: Skipping {file.name} (invalid sentence number)")
        
        # Create speaker info file
        speaker_info = speaker_template.copy()
        speaker_info["speaker_id"] = speaker_id
        speaker_info["name_initial"] = initial
        
        speaker_info_file = speaker_dir / "speaker_info.json"
        with open(speaker_info_file, "w") as f:
            json.dump(speaker_info, f, indent=2)
        
        print(f"  Created {speaker_info_file.name}\n")
    
    print(f" Organization complete!")
    print(f"Files saved to: {organized_dir}")
    
    return organized_dir


if __name__ == "__main__":
    organize_existing_recordings()
