from argparse import ArgumentParser
import os
import ffuncs as ff

# Main parser and sub-command parser:
parser = ArgumentParser(description="Copy, Move, or Delete Files")      # create argument parser
main_action_subparsers = parser.add_subparsers(description="The file action to perform")    # this is similar to adding a single optional positional argument to the main parser, but this argument would choose a sub parser (to create branching commands)

# List sub command
list_parser = main_action_subparsers.add_parser('list')
list_parser.add_argument('source', help='the source directory to perform the action on', nargs='?', default=os.getcwd())
list_parser.add_argument('-i', '--include', 
    help='a "quoted" string of comma-seprated glob patterns which each individual part of the path must match in order to be included.'
)
list_parser.add_argument('-e', '--exclude', 
    help='a "quoted" string of comma-seprated glob patterns which each individual part of the path must NOT match in order to be included.'
)

#delete_parser = main_action_subparsers.add_parser('delete', parents=[list_parser])
#delete_parser.add_argument()

# Copy sub command (borrows from List command)
copy_parser = main_action_subparsers.add_parser('copy', parents=[list_parser])
copy_parser.add_argument('destination', help='the destination directory that the source contents should be copied/moved to')
copy_parser.add_argument('-x', '--exists', 
    help='the action to perform if paths in the destination already exist', 
    choices=['ask', 'rename', 'replace', 'skip'],
    default='ask'
)

# Copy sub command (borrows from Copy command)
move_parser = main_action_subparsers.add_parser('move', parents=[copy_parser])

# parser.add_argument('action', help='the file action to perform',  choices=['list', 'copy', 'move', 'delete'], default='list')
# parser.add_argument('source', help='the source directory to perform actions on', nargs='?', default=os.getcwd())               
# parser.add_argument('destination', help='the destination directory that the source contents should be copied/moved to', nargs='?')
# parser.add_argument()

if __name__ == "__main__":
    args = parser.parse_args()

    print('these are the args')
    print(args)