#!/usr/bin/env python3
"""

"""

import sys
import argparse
import json
from PIL import Image
from pathlib import Path
from pprint import pprint
import logging

import wave_filter as wavr

#########################################################
# globals
#########################################################

VERSION = "V01"

logging.basicConfig(level=logging.INFO)
logging.info( f" {sys.argv[0]} Version {VERSION}")

#########################################################
# methods
#########################################################

def dowavr(inimage,json_dict):

    logging.info("*** Input json dictionary ***")
    pprint(json_dict)
    wvl = json_dict["wavelength"]
    amp = json_dict["amplitude"]
    drc = json_dict["direction"]
    phs = json_dict["phase"]

    fltimg = wavr.apply_wave_filter(inimage, wvl, amp, drc, phs)
    if json_dict["number_of_waves"] == 2:
        nextfltimg = wavr.apply_wave_filter(fltimg, wvl/2, amp, drc, phs)
        return nextfltimg
    elif json_dict["number_of_waves"] == 3:
        nextfltimg = wavr.apply_wave_filter(fltimg, wvl/2, amp, drc, phs)
        nextfltimg2 = wavr.apply_wave_filter(nextfltimg, wvl/4, amp, drc, phs)
        return nextfltimg2
    else:  
        return fltimg

def main():
    parser = argparse.ArgumentParser(description = 'Filter input image file')
    parser.add_argument('inputimage', action='store', help='input image file to be filtered')
    parser.add_argument('inputjson', action='store', help='input json file with filter arguments')
    parser.add_argument('outputimage', action='store', help='output filtered image file')
    args = parser.parse_args()

    try:
        # Load the input image
        print(f"Loading input image: {args.inputimage}")
        image = Image.open(args.inputimage)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.inputimage}' not found", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Load the input json file
        print(f"Loading json input: {args.inputjson}")
        jsonfile = open(args.inputjson, 'r+')
        jsondict = json.load(jsonfile)
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.inputjson}' not found", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    outimage = dowavr(image, jsondict)
    outimage.save(args.outputimage, 'JPEG', quality = jsondict["quality"])

    sys.exit(0)

if __name__ == '__main__':
    main()
