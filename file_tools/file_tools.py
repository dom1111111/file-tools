from argparse import ArgumentParser
import ffuncs as ff

parser = ArgumentParser(                                        # create argument parser
    description="Copy, Move, or Delete Files"
)
parser.add_argument('source', help='the source directory')                          
parser.add_argument('-p', '--path', help='the destination directory')
parser.add_argument('-t', '--type', choices=['python', 'web'], help='the type of project it is')

if __name__ == "__main__":
    args = parser.parse_args()

    # set_up_coding_project(args.name, args.path, args.type)

    print('these are the args')
    print(args)