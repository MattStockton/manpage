#!/usr/bin/env python

import sys, argparse, os

def main(args):
    """
    Command line tool to generate txt version of manpages
    """
    parser = argparse.ArgumentParser(description="Generate txt versions of manpages")
    parser.add_argument("-i", "--input-file", help="Location of txt file containing manpages to parse", required=True)
    parser.add_argument("-o", "--output-dir", help="Location of output directory where txt manpages should be written", required=True)
    parser.add_argument("--clean", help="Delete all files currently in the output directory", action="store_true")
   
    parsed_args = parser.parse_args(args=args)
    cmd_vars = vars(parsed_args)
    
    output_dir = cmd_vars['output_dir']
    
    if not os.path.isdir(output_dir):
        print "Output directory should exist before running this script"
        sys.exit()
        
    if parsed_args.clean:
        files = os.listdir(output_dir)
        for cur_file in files:
            os.remove(os.path.join(output_dir,cur_file))
    
    try:
        input_lines = [line.strip() for line in open(cmd_vars['input_file'])]
        for cur_line in input_lines:
            new_path = os.path.join(output_dir, cur_line + ".txt")
            shell_command = "man " + cur_line + " | col -bx > " + new_path
            os.system(shell_command)
    except IOError:
        print "There was a problem opening the input file"
    
if __name__ == "__main__":
    main(sys.argv[1:])