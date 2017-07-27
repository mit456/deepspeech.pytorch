#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import subprocess
import io
import shutil

from utils import create_manifest

parser = argparse.ArgumentParser(description='Process and build train/test manifest files from sphinx type dataset')
parser.add_argument("--sphinx_dataset_dir", help="directory that contains sphinx dataset", required=True)
parser.add_argument('--target_dir', default='complete_indian_70/', help='Path to save dataset')
parser.add_argument('--sample_rate', default=16000, type=int, help='Sample rate')

args = parser.parse_args()


def _format_data(root_path, data_tag):
    print("In format data")
    data_path = args.target_dir + data_tag + '/'
    new_transcript_path = data_path + '/txt/'
    new_wav_path = data_path + '/wav/'

    os.makedirs(new_transcript_path)
    os.makedirs(new_wav_path)

    dataset = root_path.split('/')[-1]

    wav_path = root_path + '/wav/'
    file_ids = root_path + '/' + dataset + "_%s.fileids" % data_tag
    transcripts = root_path + '/' + dataset + "_%s.transcription" % data_tag

    print("File ids, transcripts", file_ids, transcripts)
    _format_files(file_ids, new_transcript_path, new_wav_path, transcripts)

def _format_files(file_ids, new_transcript_path, new_wav_path, transcripts):
    with open(file_ids, 'r') as f:
        with open(transcripts, 'r') as t:
            paths = f.readlines()
            transcripts = t.readlines()

            for x in range(len(paths)):
                path = args.sphinx_dataset_dir + '/wav/' + paths[x].strip() + '.wav'
                cmd_duration = ['soxi', '-D', path]
                process = subprocess.Popen(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, error = process.communicate()
                if float(out) < 1.0:
                    print("Wav length less than 1.0 sec.. Skipping", path)
                    continue

                filename = path.split('/')[-1]
                extracted_transcript = _process_transcript(transcripts, x)
                text_path = new_transcript_path + filename.replace('.wav', '.txt')
                new_path = new_wav_path + filename

                # Creating text files
                with io.FileIO(text_path, "w") as txt_file:
                    txt_file.write(extracted_transcript.encode('utf-8'))

                #assert not os.path.exists(new_wav_path)
                shutil.copy(path, new_path)
                #print(paths[x])

def _convert_audio_to_wav(path):
    with os.popen('find %s -type f -name "*.wav"' % path) as pipe:
        for line in pipe:
            raw_path = line.strip()
            #new_path = line.replace('.raw', '.wav').strip()
            cmd = 'sox -t raw -r %d -b 16 -e signed-integer -B -c 1 \"%s\" \"%s\"' % (
                args.sample_rate, line.strip(), line.strip())
            os.system(cmd)


def _process_transcript(transcripts, x):
    extracted_transcript = transcripts[x].split('(')[0].strip("<s>").split('<')[0].strip().upper()
    return extracted_transcript

def main():
    """
    Main function
    """

    root_path = args.sphinx_dataset_dir

    if os.path.exists(root_path):
        print("INFO: Sphinx data directory found: Location:", os.path.abspath(__file__) + "/../" + root_path)

        os.makedirs(args.target_dir)
        _format_data(root_path, "train")
        _format_data(root_path, "test")
        train_path = args.target_dir + '/train/'
        test_path = args.target_dir + '/test/'

        #_convert_audio_to_wav(train_path + 'wav/')
        #_convert_audio_to_wav(test_path + 'wav/')

        create_manifest(train_path, "complete_indian_70_train")
        create_manifest(test_path, "complete_indian_70_test")


if __name__ == "__main__":
    if not sys.argv[0]:
        print("Please input --sphinx_dataset_dir")
        sys.exit(1)
    main()
