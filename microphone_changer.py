#!/usr/bin/env python 
import subprocess

# function to parse output of command "wpctl status" and return a dictionary of sinks with their id and name.
def parse_wpctl_status():
    # Execute the wpctl status command and store the output in a variable.
    output = str(subprocess.check_output("wpctl status", shell=True, encoding='utf-8'))

    # remove the ascii tree characters and return a list of lines
    lines = output.replace("├", "").replace("─", "").replace("│", "").replace("└", "").splitlines()

    # get the index of the Sources line as a starting point
    sources_index = None
    for index, line in enumerate(lines):
        if "Sources:" in line:
            sources_index = index
            break

    # start by getting the lines after "Sources:" and before the next blank line and store them in a list
    sources = []
    for line in lines[sources_index +1:]:
        if not line.strip():
            break
        sources.append(line.strip())

    # remove the "[vol:" from the end of the source name
    for index, source in enumerate(sources):
        sources[index] = source.split("[vol:")[0].strip()
    
    # strip the * from the default source and instead append "- Default" to the end. Looks neater in the wofi list this way.
    for index, source in enumerate(sources):
        if source.startswith("*"):
            sources[index] = source.strip().replace("*", "").strip() + " - Default"

    # make the dictionary in this format {'source_id': <int>, 'source_name': <str>}
    sources_dict = [{"source_id": int(source.split(".")[0]), "source_name": source.split(".")[1].strip()} for source in sources]

    return sources_dict

# get the list of sources ready to put into wofi - highlight the current default source
output = ''
sources = parse_wpctl_status()
for items in sources:
    if items['source_name'].endswith(" - Default"):
        output += f"<b>-> {items['source_name']}</b>\n"
    else:
        output += f"{items['source_name']}\n"

# Call wofi and show the list. take the selected source name and set it as the default source
wofi_command = f"echo '{output}' | wofi --show=dmenu --hide-scroll --allow-markup --define=hide_search=true --location=top_right --width=600 --height=200 --xoffset=-60"
wofi_process = subprocess.run(wofi_command, shell=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if wofi_process.returncode != 0:
    print("User cancelled the operation.")
    exit(0)

selected_source_name = wofi_process.stdout.strip()
sources = parse_wpctl_status()
selected_source = next(source for source in sources if source['source_name'] == selected_source_name)
subprocess.run(f"wpctl set-default {selected_source['source_id']}", shell=True)

#See this URL for updates: https://github.com/Sebastiaan76/waybar_wireplumber_audio_changer
