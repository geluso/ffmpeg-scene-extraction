#!/usr/local/bin/python

import datetime
import argparse
from subprocess import call
from uuid import uuid1

# ffprobe -show_frames -of compact=p=0 -f lavfi "movie=clip-135-02-05\ 05;27;15.dv,select=gt(scene\,.4)" > scenes.txt
probe_command = "ffprobe -show_frames -of compact=p=0 -f lavfi \"movie=%s,select=gt(scene\,.4)\" > scenes.txt"

# ffmpeg -i clip.dv -f segment -segment_times 7,20,47 -c copy -map 0:0 scenes/1989-%03d.dv"""
segment_command = "ffmpeg -i %s -f segment -segment_times LIST_OF_TIMES -c copy -map 0:0 %s/%04d.dv"

# TODO:
# - detect and print the length of the video
# - suppress ffprobe output
# - run ffprobe on another thread
# - create a second thread to repeatedly poll the file scenes file
# - print the progress of the number of scenes detected and the current time in the movie.


now = datetime.datetime.now()
default_out_name = "scenes_%d_%02d_%02d_%02d.mp4" % (now.year, now.hour, now.minute, now.second)

# Define the command line parser
parser = argparse.ArgumentParser(description="This takes one large video file and creates smaller video files representing each scene in the original movie file.")
parser.add_argument("in_file", type=str, help="Name of the input file.")
parser.add_argument("out_dir", nargs="?", type=str, default=default_out_name, help="Name of the output directory to be created.")

args = parser.parse_args()

# probe the movie and create a text file containing timestamps of scene changes
print "Probing movie for scene changes..."
cmd = probe_command % (args.in_file)
call(cmd, shell=True)

print "Probing complete. N scenes found."
print "Processing scene timestamps..."

print "Creating directory for scenes..."
# create out directory for clips
call("mkdir %s" % args.out_dir, shell=True)

print "Extracting scenes..."

