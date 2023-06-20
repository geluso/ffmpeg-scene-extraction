from subprocess import call, check_output
import sys

# ffprobe -i clip.dv -show_format 2>&1 | grep 'duration='
duration_command = "ffprobe -i %s -show_format 2>&1 | grep 'duration='"

# ffprobe -show_frames -of compact=p=0 -f lavfi "movie=clip-135-02-05\ 05;27;15.dv,select=gt(scene\,.4)" > scenes.txt
probe_command = "ffprobe -show_frames -of compact=p=0 -f lavfi \"movie=%s,select=gt(scene\,.4)\" > %s 2>&1"

# ffmpeg -i clip.dv -f segment -segment_times 7,20,47 -c copy -map 0:0 scenes/%04d.dv"""
#extract_command = "ffmpeg -i %s -f segment -segment_times %s -c copy -map 0:0 %s/%%04d.avi 2>&1"
extract_command = "ffmpeg -i %s -segment_times %s -reset_timestamps 1 -f segment %s/%%04d.mp4 2>&1"

episode = sys.argv[1]
filename = "/Users/geluso/Torrents/I.Think.You.Should.Leave.with.Tim.Robinson.%s.XviD-AFG/I.Think.You.Should.Leave.with.Tim.Robinson.%s.XviD-AFG.avi" % (episode, episode)
output = "output.txt"

video_output_dir = "%s/scenes" % (episode)
audio_output_dir = "%s/audio" % (episode)
text_output_dir = "%s/text" % (episode)

video_to_audio_command = "ffmpeg -i %s -ar 16000 %s"

#audio_to_text_command = "/Users/geluso/Code/whisper.cpp/main -p 8 -t 10 -pp -m /Users/geluso/Code/whisper.cpp/models/ggml-large.bin -f %s -osrt -of %s"
#audio_to_text_command = "/Users/geluso/Code/whisper.cpp/main -m /Users/geluso/Code/whisper.cpp/models/ggml-large.bin -f %s -osrt -of %s"
#audio_to_text_command = "/Users/geluso/Code/whisper.cpp/main -p 4 -m /Users/geluso/Code/whisper.cpp/models/ggml-large.bin -f %s -osrt -of %s"
audio_to_text_command = "/Users/geluso/Code/whisper.cpp/main -m /Users/geluso/Code/whisper.cpp/models/ggml-large.bin -f %s -osrt -of %s"

#cmd = "rm -rf %s" % (video_output_dir)
#call(cmd, shell=True)
#cmd = "rm -rf %s" % (audio_output_dir)
#call(cmd, shell=True)
#cmd = "rm -rf %s" % (text_output_dir)
#call(cmd, shell=True)

cmd = "mkdir -p %s" % (video_output_dir)
call(cmd, shell=True)
cmd = "mkdir -p %s" % (audio_output_dir)
call(cmd, shell=True)
cmd = "mkdir -p %s" % (text_output_dir)
call(cmd, shell=True)

cmd = duration_command % (filename)
duration_result = call(cmd, shell=True)
print("duration:", duration_result)

cmd = probe_command % (filename, output)
probe_result = call(cmd, shell=True)
print("probe:", probe_result)

probe_lines = open(output).readlines()
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
extract_result = call(cmd, shell=True)

for i in range(len(timestamps)):
    video_file = "%s/%04d.mp4" % (video_output_dir, i)
    audio_file = "%s/%04d.wav" % (audio_output_dir, i)
    text_file = "%s/%04d" % (text_output_dir, i)

    cmd = video_to_audio_command % (video_file, audio_file)
    print("converting video to audio:", cmd)
    video_to_audio_result = call(cmd, shell=True)

    cmd = audio_to_text_command % (audio_file, text_file)
    print("converting audio to text")
    print(cmd)
    audio_to_text_result = call(cmd, shell=True)
