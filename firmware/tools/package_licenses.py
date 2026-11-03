"""Bundle the pinned dependencies' actual license files and source notices."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "firmware/build/delivery/licenses"
OUT.mkdir(parents=True,exist_ok=True)
for source, name in [("zephyr/LICENSE","Zephyr-LICENSE"),
                     ("modules/hal/cmsis/LICENSE.txt","CMSIS-LICENSE")]:
    (OUT/name).write_bytes((ROOT/source).read_bytes())
# The vendored Nordic and TinyCrypt trees retain notices in source headers,
# rather than in the standalone root LICENSE files used by their upstreams.
for directory, name in [("modules/hal/nordic","Nordic-source-notices.txt"),
                        ("modules/crypto/tinycrypt","TinyCrypt-source-notices.txt")]:
    notices = {}
    module = ROOT/directory
    for path in sorted(module.rglob("*")):
        if path.suffix not in (".c",".h"): continue
        text = path.read_text(errors="strict")
        for block in re.findall(r"/\*.*?\*/",text,re.S):
            if "copyright" not in block.lower(): continue
            notices.setdefault(block,[]).append(str(path.relative_to(ROOT)))
    if not notices:
        raise RuntimeError("No source notices found for "+directory)
    chunks = ["Unmodified copyright/license comment blocks from the pinned module.\n"]
    for block,paths in notices.items():
        chunks.extend(["\nSources: "+", ".join(paths)+"\n",block+"\n"])
    (OUT/name).write_text("".join(chunks))
    print("Bundled",len(notices),"distinct source notices from",directory)
