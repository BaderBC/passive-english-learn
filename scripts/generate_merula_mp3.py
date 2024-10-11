import json
import os
import subprocess

merula_json = open("merula.json").read()
merula_resources = json.loads(merula_json)

for focus, chapters in merula_resources.items():
    for chapter, url in chapters.items():
        output_dir = f"./out/{focus}/{chapter}"
        os.makedirs(output_dir, exist_ok=True)

        # scrap merula into input.json
        subprocess.run(["python", "scrap_merula_pl.py", url])

        # generate mp3 from input.json
        subprocess.run(["python", "generate_mp3.py", output_dir])

        # print in red color:
        print(f"\n\n\033[91m{focus} {chapter} generated!\033[0m\n\n")
