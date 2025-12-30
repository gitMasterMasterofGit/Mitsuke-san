import sys, json, queue
import container.AddGlobals
import warnings
from pathlib import Path
from container.Transcribe import Transcriber

warnings.filterwarnings('ignore')
container.AddGlobals.add_globals()

AUDIO_PATH = Path(sys.argv[1])
OUT_DIR = Path("/jobs/out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

trans = Transcriber(queue.Queue())

result = trans.transcribe(AUDIO_PATH)

out_file = OUT_DIR / (AUDIO_PATH.stem + ".json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(trans.to_json(result), f, ensure_ascii=False)

AUDIO_PATH.unlink()
print(f"Wrote {out_file}")
