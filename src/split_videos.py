"""

This script splits the downloaded video into frames.

Author: Kung-hsiang, Huang, 2018
"""
import glob
import subprocess
from joblib import Parallel, delayed
import argparse
import os
import shutil
import multiprocessing
from util import *

def video2frames(video_id, video_path, processed_videos_dir, frame_path, sample_rate):
    """
    Execute shell command which calls ffmpeg to split video into frames.
    Parameters
    ----------
    video_id : str
        The video id of a video
    video_path: str
        The directory storing the videos
    processed_video_path: str
        The directory storing videos that have been split.
    sample_rate: int
        The sample rate for splitting the video.
    """
    #concat path and video id
    path_video = video_path + video_id + '.mp4'
    video_duration = get_duration(path_video)
    # split only the main part of the video
    starting_time = 0.2 * video_duration
    # split_duration = 0.6 * video_duration
    split_duration = 10 * video_duration
    
    try:
        #-loglevel panic: slience
        #-hwaccel vdpau: hardware acceleration with GPU
        # -ss starting time
        # -t duration
        cmd = f'ffmpeg -ss {starting_time} -t {split_duration} -i {path_video} -r {sample_rate} {frame_path}/{video_id}-%07d-{sample_rate}.png'.split(" ")
        # subprocess.run(cmd)
        subprocess.check_output(cmd)
        shutil.move(path_video, f"{processed_videos_dir}/{video_id}.mp4")
        print('----')

    except Exception as e:
        print(f'Failed to cut videos {video_id}: {e}')

    
def get_duration(path_video):
    
    """
    Get the duration of a video

    Parameters
    ----------
    path_video : str
        The path of the video (path+file name)
    
    Returns
    --------
    the duration of path_video in second
    """
    
    #execute the command
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {path_video}'
    return float(subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0].strip())

def path2id(path):
    """
    Extract video id from path 
    e.g. ADFBSDFG.mp4 --> ADFBSDFG

    Parameters
    ----------
    path : str
        The path of the video (only file name)
    
    Returns
    --------
    str
        The extracted video id
    """
    return path.split('.')[0]


def extract_audio(video_id, videos_dir, audios_dir):
    """
    Download the videos
    Parameters
    ----------
    video_id : str
        A Youtube video id.
    videos_dir: str
        The directory which stores videos.
    audios_dir: str
        The directory which stores audios.

    """
    start = 79650
    end = 79830
    video_path = f'{videos_dir}/{video_id}.mp4'
    audio_path = f'{videos_dir}/{video_id}.mp3'
    # -i: it is the path to the input file. The second option -f mp3 tells ffmpeg that the ouput is in mp3 format.
    # -ab 192000: we want the output to be encoded at 192Kbps
    # -vn :we dont want video.
    # execute the command
    mil_sec_start = start % 100
    start = start // 100
    sec_start = start % 60
    start = start // 60
    min_start = start % 60
    start = start // 60
    hour_start = start % 60
    start_time = "%02d:%02d:%02d.%02d0" % (hour_start, min_start, sec_start, mil_sec_start)
    mil_sec_end = end % 100
    end = end // 100
    sec_end = end % 60
    end = end // 60
    min_end = end % 60
    end = end // 60
    hour_end = end % 60
    video_id = 1
    i = 1
    end_time = "%02d:%02d:%02d.%02d0" % (hour_end, min_end, sec_end, mil_sec_end)
    # audio_cmd = f"ffmpeg -y -i {audios_dir}/{video_id}.mp3 -ss {start_time} -to {end_time} -acodec copy {result_dir}/{video_id}/{video_id}-{i:05d}.mp3"
    # audio_cmd = f"ffmpeg -y -i {audios_dir}/drama_sample1.mp3 -ss {start_time} -to {end_time} -acodec copy "+"drama_split_"+str(video_id)+".mp3"
    #mp4 to mp3
    videotomp3_cmd = f"ffmpeg -i {video_path} {audio_path}"
    print(videotomp3_cmd)
    cmd = videotomp3_cmd.split(" ")
    subprocess.call(cmd, shell=False)

    print('audio path' + audio_path)
    audio_cmd = f"ffmpeg -y -i {audio_path} -ss {start_time} -to {end_time} -acodec copy " + "drama_split_" + str(video_id) + ".mp3"

    print(audio_cmd)
    cmd = audio_cmd.split(" ")
    subprocess.call(cmd, shell=False)


parent_dir = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/data/'
result_dir = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/data/result'

def video_main():
    parser = argparse.ArgumentParser("Script for splitting youtube videos")
    parser.add_argument("--thread_count", type=int)
    parser.add_argument("--videos_dir", type=str, default=parent_dir, required=False)
    parser.add_argument("--processed_videos_dir", default=parent_dir + 'processed_videos', type=str, required=False)
    parser.add_argument("--frames_dir", type=str, default=parent_dir + 'frames', required=False)
    # parser.add_argument("--sample_rate", type=float, default = 2, required=False)
    parser.add_argument("--sample_rate", type=float, default = 2, required=False)
    parser.add_argument("--video_id_file", type=str,default='../video_ids.txt', required=False)
    
    args = parser.parse_args()
    # get all video_ids
    video_ids = get_video_id_from_file(args.video_id_file)
    
    # *********WE HAVE TO SET (# OF THREADS) = (LENGTH OF THE VIDEOS) SO THAT THE PROGRAM PROCESS ALL THE FILES******
    if args.thread_count == None:
        thread_count = len(video_ids)
    else:
        thread_count = args.thread_count
    
    os.makedirs(args.frames_dir, exist_ok=True)
    
    # parallel processing to increase speed
    parallel = Parallel(thread_count, backend="threading", verbose=0)

    try: 
        #split video into frames
        # parallel(delayed(video2frames)(video_id, video_path=args.videos_dir, processed_videos_dir=args.processed_videos_dir, frame_path=args.frames_dir, sample_rate=args.sample_rate) for video_id in video_ids)
        for video_id in video_ids:
            video2frames(video_id, video_path=args.videos_dir, processed_videos_dir=args.processed_videos_dir, frame_path=args.frames_dir, sample_rate=args.sample_rate)
        print('split finished')
    except Exception as e:
        print('Failed to split videos: {}'.format(e))

def audio_main():
    parent_dir = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/'
    parser = argparse.ArgumentParser("Script for splitting youtube videos")
    parser.add_argument("--thread_count", type=int)
    parser.add_argument("--videos_dir", type=str, default=parent_dir + '/data/', required=False)
    parser.add_argument("--frames_dir", type=str, default=parent_dir + 'frames', required=False)
    # parser.add_argument("--sample_rate", type=float, default = 2, required=False)
    parser.add_argument("--sample_rate", type=float, default=2, required=False)
    parser.add_argument("--video_id_file", type=str, default='../video_ids.txt', required=False)
    args = parser.parse_args()

    video_ids = get_video_id_from_file(args.video_id_file)
    extract_audio(video_id='drama_sample1', videos_dir=args.videos_dir, audios_dir=parent_dir + '/processed_audio')

def get_duration_mp3(filename):
    args = '/usr/local/bin/ffprobe -v quiet -print_format compact=print_section=0:nokey=1:escape=csv -show_entries format=duration '+filename
    # args = '/usr/local/bin/ffprobe -v quiet compact=print_section=0:nokey=1:escape=csv -show_entries format=duration ' + filename
    args = args.split(' ')

    print (args)
    output = subprocess.check_output(args)
    result = str(output)
    print(result)
    return result


def split_audio(audios_dir, audio_id):
    input_audio_path = f'{audios_dir}/{audio_id}.mp3'
    duration_time = get_duration_mp3(input_audio_path)
    print('Duration time:' + str(duration_time))
    output_base_path = audios_dir +'/processed_audio/'
    start_tag = 79650
    end_tag = start_tag
    idx = 1
    while True:
        try:
            end_tag = start_tag + 170

            start = start_tag
            end = end_tag

            mil_sec_start = start % 100
            start = start // 100
            sec_start = start % 60
            start = start // 60
            min_start = start % 60
            start = start // 60
            hour_start = start % 60
            start_time = "%02d:%02d:%02d.%02d0" % (hour_start, min_start, sec_start, mil_sec_start)
            mil_sec_end = end % 100
            end = end // 100
            sec_end = end % 60
            end = end // 60
            min_end = end % 60
            end = end // 60
            hour_end = end % 60
            end_time = "%02d:%02d:%02d.%02d0" % (hour_end, min_end, sec_end, mil_sec_end)
            # audio_cmd = f"ffmpeg -y -i {audios_dir}/{video_id}.mp3 -ss {start_time} -to {end_time} -acodec copy {result_dir}/{video_id}/{video_id}-{i:05d}.mp3"
            # audio_cmd = f"ffmpeg -y -i {audios_dir}/drama_sample1.mp3 -ss {start_time} -to {end_time} -acodec copy "+"drama_split_"+str(video_id)+".mp3"
            video_file_id = '%07d'%(idx)
            audio_cmd = f"ffmpeg -y -i {input_audio_path} -ss {start_time} -to {end_time} -acodec copy " + output_base_path + '/drama_sample1_' + video_file_id + "-2.mp3"
            idx = idx + 1

            print('start:', start_time, 'end:', end_time)
            cmd = audio_cmd.split(" ")
            subprocess.call(cmd, shell=False)
            start_tag = end_tag
        except :
            print('')

def split_main():
    parent_dir = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation'
    parser = argparse.ArgumentParser("Script for splitting youtube videos")
    parser.add_argument("--thread_count", type=int)
    parser.add_argument("--videos_dir", type=str, default=parent_dir + '/data/', required=False)
    parser.add_argument("--frames_dir", type=str, default=parent_dir + 'frames', required=False)
    # parser.add_argument("--sample_rate", type=float, default = 2, required=False)
    parser.add_argument("--sample_rate", type=float, default=2, required=False)
    parser.add_argument("--video_id_file", type=str, default='../video_ids.txt', required=False)
    args = parser.parse_args()

    video_ids = get_video_id_from_file(args.video_id_file)
    split_audio(audios_dir=parent_dir +'/data', audio_id='drama_sample1' )


if __name__ == "__main__":

    # video_main()
    # audio_main()
    split_main()
