#!/usr/local/bin/python

import datetime
import argparse
from subprocess import call, check_output
from uuid import uuid1

# ffprobe -i clip.dv -show_format 2>&1 | grep 'duration='
duration_command = "ffprobe -i %s -show_format 2>&1 | grep 'duration='"

# ffprobe -show_frames -of compact=p=0 -f lavfi "movie=clip-135-02-05\ 05;27;15.dv,select=gt(scene\,.4)" > scenes.txt
probe_command = "ffprobe -show_frames -of compact=p=0 -f lavfi \"movie=%s,select=gt(scene\,.4)\" > scenes.txt"

# ffmpeg -i clip.dv -f segment -segment_times 7,20,47 -c copy -map 0:0 scenes/1989-%03d.dv"""
segment_command = "ffmpeg -i %s -f segment -segment_times LIST_OF_TIMES -c copy -map 0:0 %s/%04d.dv"

# TODO:
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

def print_movie_length(filename):
  cmd = duration_command % (filename)
  duration = check_output(cmd, shell=True)
  duration = duration.split("duration=")[1]

  # eliminate fractions of a second
  duration = duration.split(".")[0]
  duration = int(duration)

  # calculate hours, minutes, seconds
  minutes = duration / 60
  if (minutes > 60):
    hours = minutes / 60
    minutes = minutes % 60
  seconds = duration % 60

  print "Movie is %02d:%02d:%02d long" % (hours, minutes, seconds)

def detect_scenes(filename):
  # probe the movie and create a text file containing timestamps of scene changes
  print "Probing movie for scene changes..."
  cmd = probe_command % (filename)
  call(cmd, shell=True)

  print "Probing complete. N scenes found."
  print "Processing scene timestamps..."

def extract_scenes():
  print "Creating directory for scenes..."
  # create out directory for clips
  call("mkdir %s" % args.out_dir, shell=True)

  print "Extracting scenes..."

def main():
  args = parser.parse_args()
  filename = args.in_file.replace(" ", "\\ ")

  print_movie_length(filename)
  detect_scenes(filename)

main()
