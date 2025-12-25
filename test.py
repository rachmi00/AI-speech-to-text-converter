import shutil, os, subprocess
print("ffmpeg which:", shutil.which("ffmpeg"))
print("audio exists:", os.path.exists("lesson_recording.mp3"), os.path.abspath("lesson_recording.mp3"))
subprocess.run(["ffmpeg","-version"])