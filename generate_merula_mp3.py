import json
import os
import subprocess

def run_command(command):
    result = subprocess.run(command)
    if result.returncode != 0:
        raise RuntimeError(f"Command {command} failed with return code {result.returncode}")

merula_json = open("merula.json").read()
merula_resources = json.loads(merula_json)

for focus, chapters in merula_resources.items():
    for chapter, url in chapters.items():
        output_dir = f"./out/{focus}/{chapter}"
        os.makedirs(output_dir, exist_ok=True)

        # scrap merula into input.json
        run_command(["python", "scrap_merula_pl.py", url])

        # generate mp3 from input.json
        run_command(["python", "generate_mp3.py", output_dir])

        # print in red color:
        print(f"\n\n\033[91m{focus} {chapter} generated!\033[0m\n\n")

