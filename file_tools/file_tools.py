from argparse import ArgumentParser
import os
import ffuncs as ff

#--------- Argparse Setup ---------#

# Main parser and subparsers action:
parser = ArgumentParser(description="Perform common file operations")
main_action_subparsers = parser.add_subparsers(description="The file action to perform", dest="command")
    # ^ this is similar to adding a single optional positional argument to the main parser, 
    # but this argument would choose a subparser (to create branching commands)

# Delete subcommand:
delete_parser = main_action_subparsers.add_parser('delete')
delete_parser.add_argument('-nc', '--noconfirm', help="do not ask for confirmation before deletion")

# List subcommand (root parent for other commands):
list_parser = main_action_subparsers.add_parser('list')
list_parser.add_argument('source', help='the source directory to perform the action on', nargs='?', default=os.getcwd())
list_parser.add_argument('-i', '--include', 
    help='a "quoted" string of comma-seprated glob patterns which each individual part of the path must match in order to be included.'
)
list_parser.add_argument('-e', '--exclude', 
    help='a "quoted" string of comma-seprated glob patterns which each individual part of the path must NOT match in order to be included.'
)

# Copy subcommand (borrows args from List command):
copy_parser = main_action_subparsers.add_parser('copy', parents=[list_parser], add_help=False)
    # `add_help=False` must be added to all parsers which use parents
copy_parser.add_argument('destination', help='the destination directory that the source contents should be copied/moved to')
copy_parser.add_argument('-x', '--exists', 
    help='the action to perform if paths in the destination already exist', 
    choices=['ask', 'rename', 'replace', 'skip'],
    default='ask'
)

# Move subcommand (borrows args from Copy command):
move_parser = main_action_subparsers.add_parser('move', parents=[copy_parser], add_help=False)


#--------- Main Execution ---------#

command_map = {
    'list':     ff.display_dir,
    'copy':     ff.copy_move_dir,
    'move':     ff.copy_move_dir,
    'delete':   ff.permanent_delete,
}

if __name__ == "__main__":
    args = parser.parse_args()
    # If include/exclude was provided and they're not None, split their string 
    # by commas into a list, and remove extra whitespace from each value:
    include = [s.strip() for s in (args.include).split(',')] if (hasattr(args, 'include') and args.include) else []
    exclude = [s.strip() for s in (args.exclude).split(',')] if (hasattr(args, 'exclude') and args.exclude) else []
    # Apply args to function according to 'command':
    if args.command == 'list':
        ff.display_dir(args.source, include, exclude)
    elif args.command == 'copy':
        ff.copy_move_dir(args.source, args.destination, False, include, exclude, args.exist)
    elif args.command == 'move':
        ff.copy_move_dir(args.source, args.destination, True, include, exclude, args.exist)
    elif args.command == 'delete':
        ff.permanent_delete(args.source, args.noconfirm)
