from subprocess import call, check_output
import os
import sys
import time

import gather_srt

EXPECTED_EXTENSIONS = ["avi", "mp4", "mkv", "mov"]

# ffprobe -i clip.dv -show_format 2>&1 | grep 'duration='
duration_command = "ffprobe -i '%s' -show_format 2>&1 | grep 'duration='"

# ffprobe -show_frames -of compact=p=0 -f lavfi "movie=clip-135-02-05\ 05;27;15.dv,select=gt(scene\,.4)" > scenes.txt
probe_command = "ffprobe -show_frames -of compact=p=0 -f lavfi \"movie='%s',select=gt(scene\,.4)\" > '%s' 2>&1"

# ffmpeg -i clip.dv -f segment -segment_times 7,20,47 -c copy -map 0:0 scenes/%04d.dv"""
#extract_command = "ffmpeg -i %s -f segment -segment_times %s -c copy -map 0:0 %s/%%04d.avi 2>&1"
extract_command = "ffmpeg -i '%s' -ac 2 -segment_times '%s' -reset_timestamps 1 -f segment '%s/%%04d.mp4' 2>&1"

video_to_audio_command = "ffmpeg -i %s -ar 16000 %s"

audio_to_text_command = "/Users/geluso/Code/whisper.cpp/main -m /Users/geluso/Code/whisper.cpp/models/ggml-base.en.bin -f '%s' -osrt -of '%s'"


create_json_structure_command = 'tree -J > structure.json'

def main():
    with open("progress", "a") as progress_file:
        for root, dirs, filenames in os.walk("."):
            msg = "Found %d files." % len(filenames)
            print(msg)
            progress_file.writelines(msg)
            progress_file.flush()

            for filename in filenames:
                extension = filename.split(".")[-1]
                if extension in EXPECTED_EXTENSIONS and not filename.startswith("._"):
                    process_file(filename, progress_file)
                else:
                    print("Skipping file with non-expected extension:", filename)
        do_cmd(create_json_structure_command)

def do_cmd(cmd, is_checking_output=False, is_breakpoint=False):
    print(cmd)
    if is_breakpoint:
        breakpoint()
    if not is_checking_output:
        call(cmd, shell=True)
        return
    result = check_output(cmd, shell=True)
    print(result)
    print()
    return result


def make_dir(dir_name):
    cmd = "mkdir -p '%s'" % (dir_name)
    return do_cmd(cmd)

def get_duration(filename):
    cmd = duration_command % (filename)
    return do_cmd(cmd, True)

def probe_scenes(filename, output):
    cmd = probe_command % (filename, output)
    return do_cmd(cmd)

def process_file(filename, progress_file):
    print("Processing", filename)

    print("with spaces", filename)
    filename_no_extension = os.path.splitext(filename)[0]
    filename_no_extension = filename_no_extension.replace(" ", "_")
    print(" w/o spaces", filename_no_extension)

    probed_scene_timestamps_file = "%s.txt" % filename_no_extension
    video_output_dir = "%s/scenes" % (filename_no_extension)
    audio_output_dir = "%s/audio" % (filename_no_extension)
    text_output_dir = "%s/text" % (filename_no_extension)

    #cmd = "rm -rf %s" % (video_output_dir)
    #call(cmd, shell=True)
    #cmd = "rm -rf %s" % (audio_output_dir)
    #call(cmd, shell=True)
    #cmd = "rm -rf %s" % (text_output_dir)
    #call(cmd, shell=True)

    make_dir(video_output_dir)
    make_dir(audio_output_dir)
    make_dir(text_output_dir)

    get_duration(filename)
    probe_scenes(filename, probed_scene_timestamps_file)

    probe_lines = open(probed_scene_timestamps_file).readlines()
    timestamps = []
    for line in probe_lines:
        if "best_effort_timestamp_time" in line:
            line = line.split("best_effort_timestamp_time=")
            line = line[1]
            line = line.split("|")
            line = line[0]
            line = str(int(float(line)))
            timestamps.append(line)

    print("Found", len(timestamps), "scenes")
    print("Extracting...")

    all_segment_times = ",".join(timestamps)
    cmd = extract_command % (filename, all_segment_times, video_output_dir)
    do_cmd(cmd)

    for i in range(len(timestamps)):
        video_file = "%s/%04d.mp4" % (video_output_dir, i)
        audio_file = "%s/%04d.wav" % (audio_output_dir, i)
        text_file = "%s/%04d" % (text_output_dir, i)

        cmd = video_to_audio_command % (video_file, audio_file)
        print("converting video to audio:", cmd)
        call(cmd, shell=True)

        cmd = audio_to_text_command % (audio_file, text_file)
        print("converting audio to text")
        print(cmd)
        call(cmd, shell=True)

    gather_srt.create_json_file(filename_no_extension)


main()
