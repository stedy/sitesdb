"""script to format image files and group similar images together"""

import os
import subprocess as sh
import argparse


def main():
	parser = argparse.ArgumentParser(description = """Generate concatenated
	image files with Imagemagick from ABI trace files""")
	parser.add_argument('input_path', help = """input path to files of
	interest""")
	parser.add_argument('output_path', help = """where to write files to""")
	args = parser.parse_args()
	#path = "converted_image_files"
	
	files = os.listdir(args.input_path)
	
	i = 0
	vals = []
	for x in files:
	    k = files[i:len(files)]
	    images = k[0:5]
	    if len(images):
	        vals.append(images)
	    i += 5
	for v in vals:
	    root = v[0].split("_")[0]
	    shargs = ['montage -mode concatenate -font Helvetica -tile 1x %s %s %s \
                  %s %s %s' %
	        (args.input_path+v[0], args.input_path+v[1], args.input_path+v[2],
	            args.input_path+v[3], 
                args.input_path+v[4],
                args.output_path+root+'.jpg')]
	    print shargs
        sh.Popen(shargs, shell = True)
	
if __name__ == '__main__':
    main()
