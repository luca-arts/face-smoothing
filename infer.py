import os
import argparse
import yaml
import time

import cv2
import matplotlib
import matplotlib.pyplot as plt

from detector.detect import detect_face
from detector.smooth import smooth_face
from utils.image import (load_image, 
                         save_image, 
                         save_steps, 
                         check_img_size,
                         get_height_and_width,
                         process_image,
                         check_if_adding_bboxes)
from utils.video import (split_video,
                         process_video)
from utils.types import (is_image,
                         is_video,
                         is_directory)
import traceback

def parse_args():
    """
    Argument parser for cli.

    Returns
    -------
    args : ArgumentParser object
        Contains all the cli arguments
    """
    parser = argparse.ArgumentParser(description='Facial detection and \
                                     smoothing using OpenCV.')
    parser.add_argument('--input', 
                        type=str, 
                        help='Input file or folder',
                        default='data/images/hillary_clinton.jpg')
    parser.add_argument('--output', 
                        type=str, 
                        help='Output file or folder',
                        default='data/output')
    parser.add_argument('--show-detections', 
                        action='store_true',
                        help='Displays bounding boxes during inference.')
    parser.add_argument('--save-steps', 
                        action='store_true',
                        help='Saves each step of the image.')
    parser.add_argument('--config', 
                        type=str, 
                        help='path to config file',
                        default='configs/configs.yaml')                    
    args = parser.parse_args()
    # assert args.image_shape is None or len(args.image_shape) == 2, \
    #     'You need to provide a 2-dimensional tuple as shape (H,W)'
    # assert (is_image(args.input) and is_image(args.output)) or \
    #        (not is_image(args.input) and not is_image(args.input)), \
    #     'Input and output must both be images or folders'
    return args


def load_configs(config_path):
    """
    Loads the project configurations.

    Returns
    -------
    configs : dict
        A dictionary containing the configs
    """
    with open(config_path, 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def main(args):
    """Puts it all together."""
    
    # Start measuring time
    tic = time.perf_counter()
    # Load project configurations
    cfg = load_configs(args.config)
    # Load the network
    net = cv2.dnn.readNetFromTensorflow(cfg['net']['model_file'], 
                                        cfg['net']['cfg_file'])
    # Input and load image
    input_file = args.input

    try:
        # If file is a compatible video file
        if is_video(input_file):
            # Process video
            process_video(input_file, args, cfg, net)

        # If file is a compatible image file
        elif is_image(input_file):
            # Load image
            input_img = load_image(input_file)
            # Process image
            img_steps = process_image(input_img, cfg, net)
            # Save final image to specified output filename
            out_filename = os.path.join(args.output, cfg['image']['output'])
            # Check for --show-detections flag
            output_img = check_if_adding_bboxes(args, img_steps)
            # Save image
            img_saved = save_image(out_filename, output_img)

        # If input_file is a dir
        elif is_directory(input_file):
            # For each file in the dir
            for file in os.listdir(input_file):
                print('next image: ',file)
                try:
                  # Join input dir and file name
                  file_path = os.path.join(input_file, file)
                  # If file is a compatible video file
                  if is_video(file_path):
                      # Process video
                      process_video(file_path, args, cfg, net)
                  # If file is a compatible image file    
                  if is_image(file_path):
                      # Load image
                      input_img = load_image(file_path)
                      # Process image
                      img_steps = process_image(input_img, cfg, net)
                      if(img_steps != None):
                        print("saving image ",file_path)
                        # Save final image to specified output filename
                        out_filename = os.path.join(args.output, cfg['image']['output']+file)
                        print(out_filename)
                        # Check for --show-detections flag
                        output_img = check_if_adding_bboxes(args, img_steps)
                        # Save image
                        img_saved = save_image(out_filename, output_img)
                except UnboundLocalError as e:
                  print('no face detected?', e)
                  traceback.print_exc()
    except ValueError:
        print('Input must be a valid image, video, or directory.')
    
        
    
    # Save processing steps
    if args.save_steps:
        # Set image output height
        output_height = cfg['image']['img_steps_height']
        # Set output filename
        steps_filename = os.path.join(args.output, cfg['image']['output_steps'])
        # Save file
        save_steps(steps_filename, img_steps, output_height)

    # End measuring time
    toc = time.perf_counter()
    print(f"Operation ran in {toc - tic:0.4f} seconds")


if __name__ == '__main__':
    args = parse_args()
    main(args)
