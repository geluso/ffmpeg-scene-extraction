#!/usr/local/bin/python

import argparse
import os
import threading

from collections import defaultdict
from datetime import datetime
from subprocess import call, check_output
from time import sleep
from uuid import uuid1

# ffprobe -i clip.dv -show_format 2>&1 | grep 'duration='
duration_command = "ffprobe -i %s -show_format 2>&1 | grep 'duration='"

# ffprobe -show_frames -of compact=p=0 -f lavfi "movie=clip-135-02-05\ 05;27;15.dv,select=gt(scene\,.4)" > scenes.txt
probe_command = "ffprobe -show_frames -of compact=p=0 -f lavfi \"movie=%s,select=gt(scene\,.4)\" > %s 2>&1"

# ffmpeg -i clip.dv -f segment -segment_times 7,20,47 -c copy -map 0:0 scenes/%04d.dv"""
extract_command = "ffmpeg -i %s -f segment -segment_times %s -c copy -map 0:0 %s/%%04d.dv 2>&1"

# Define the command line parser
parser = argparse.ArgumentParser(description="This takes one large video file and creates smaller video files representing each scene in the original movie file.")
parser.add_argument("in_file", type=str, help="Name of the input file.")

def log_current_time():
  print datetime.now().isoformat()

def unescape(path):
  path = path.replace("\\ ", " ")
  return path

def path_exists(path):
  # ugh. unescape previously escaped spaces.
  path = unescape(path)
  return os.path.exists(path)

def seconds_to_timestamp(seconds):
  # calculate hours, minutes, seconds
  hours = 0
  minutes = seconds / 60
  if minutes > 60:
    hours = minutes / 60
    minutes = minutes % 60
  seconds = seconds % 60

  timestamp = "%02d:%02d:%02d" % (hours, minutes, seconds)
  return timestamp

def get_duration(filename):
  cmd = duration_command % (filename)
  print cmd
  duration = check_output(cmd, shell=True)
  duration = duration.split("duration=")[1]

  # eliminate fractions of a second
  duration = duration.split(".")[0]
  duration = int(duration)
  return duration

def create_scenes_dir(filename):
  dir_name = get_dir(filename) + "/scenes"
  if path_exists(dir_name):
    print "Directory already exists: %s" % dir_name
  else:
    cmd = "mkdir %s" % (dir_name)
    call(cmd, shell=True)

  timestamps_txt = "%s/timestamps.txt" % (dir_name)
  if path_exists(timestamps_txt):
    print "timestamps.txt already exists"
  else:
    cmd = "touch %s" % (timestamps_txt)
    call(cmd, shell=True)

  return timestamps_txt

def is_timestamp(line):
  return "pkt_pts_time=" in line

def line_to_timestamp(line):
  # extract the timestamp from a line that looks like this:
  # media_type=video|key_frame=1|pkt_pts=94|pkt_pts_time=3.136467|pk...
  return float(line.split("time=")[1].split("|")[0])

def detect_scenes(filename, timestamps_txt, duration):
  scenes = []

  def probe():
    # probe the movie and create a text file containing timestamps of scene changes
    print "Probing movie for scene changes..."
    cmd = probe_command % (filename, timestamps_txt)
    call(cmd, shell=True)

  def show_progress(timestamp):
    t1 = seconds_to_timestamp(timestamp)
    t2 = seconds_to_timestamp(duration)
    percent = 100 * (timestamp / duration)
    print "Found scene change at %s of %s (%02.2f%% complete)" % (t1, t2, percent)

  def poll():
    cmd = "cat %s" % (timestamps_txt)
    lines = check_output(cmd, shell=True)
    lines = lines.split("\n")
    lines = filter(is_timestamp, lines)

    timestamps = map(line_to_timestamp, lines)

    for timestamp in timestamps:
      if timestamp not in scenes:
        scenes.append(timestamp)
        show_progress(timestamp)

  prober = threading.Thread(target=probe)
  prober.start()

  while (prober.is_alive()):
    poll()
    sleep(1)

  print "Scene detection complete. %d scenes found." % (len(scenes))

  scenes.sort()
  return scenes

def extract_scenes(filename, scenes):
  print "Extracting scenes..."
  scenes = map(str, scenes)
  times = ",".join(scenes)

  scenes_dir = get_dir(filename) + "/scenes"
  cmd = extract_command % (filename, times, scenes_dir)
  call(cmd, shell=True)

def get_dir(filename):
  path = filename.split("/")
  return "/".join(path[:-1])

def main():
  args = parser.parse_args()
  filename = args.in_file.replace(" ", "\\ ")

  log_current_time()
  print "Processing", filename

  duration = get_duration(filename)
  timestamps_txt = create_scenes_dir(filename)

  times = open(unescape(timestamps_txt)).readlines()
  if len(times) > 0:
    times = filter(is_timestamp, times)
    scenes = map(line_to_timestamp, times)
  else:
    log_current_time()
    scenes = detect_scenes(filename, timestamps_txt, duration)

  log_current_time()
  extract_scenes(filename, scenes)

main()
