import json, time, os
import container.AddGlobals
import warnings
from pathlib import Path
from container.Transcribe import Transcriber

warnings.filterwarnings('ignore')
container.AddGlobals.add_globals()

print("MASAKA?????!!!!!!")

OUT_DIR = Path("/jobs/out")

trans = Transcriber()

IN_DIR = Path("/jobs/in")
idx = 0
while True:
    if not os.path.exists(Path(IN_DIR / f"out_{idx}.wav")):
        print(f"File out_{idx}.wav not found, waiting...")
        time.sleep(5)
        continue
    else:
        result = trans.transcribe(f"/jobs/in/out_{idx}.wav")
        out_file = OUT_DIR / (f"out_{idx}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(trans.to_json(result), f, ensure_ascii=False)
        idx += 1
        print(f"Transcription index: {idx}")
    if os.path.exists("/jobs/in/DONE"):
        print("DONE file found, exiting.")
        with open("/jobs/out/DONE", "w") as f:
            f.write("DONE\n")
            f.write(str(idx))
        break

