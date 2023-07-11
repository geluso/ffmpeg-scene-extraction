from subprocess import call, check_output
import json
import sys

def create_json_file(video_dir):
    text_dir = "%s/text" % video_dir

    list_text_files = "ls -1 %s" % text_dir
    cmd = list_text_files

    text_files = check_output(cmd, shell=True)

    data = {}
    for file in text_files.split():
        clip = file.decode("utf-8")
        filename = text_dir + '/' + clip
        ff = open(filename)
        lines = ff.readlines()
        clip_json = []

        count = 0
        for line in lines:
            if count % 4 == 0:
                pass
            elif count % 4 == 1:
                timestamp = line.strip()
            elif count % 4 == 2:
                text = line.strip()
                clip_json.append({
                    "timestamp": timestamp,
                    "text": text
                })
            elif count % 4 == 3:
                pass
            count += 1
        data[clip] = clip_json
    print(data)

    jj = json.dumps(data)
    json_filename = "%s/%s.json" % (video_dir, video_dir)
    ff = open(json_filename, mode="w")
    ff.write(jj)
    ff.close()
