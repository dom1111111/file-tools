from pathlib import Path
import shutil
from pprint import pprint


#--------- Support Functions ---------#

def _path_parts_valid(a_path:str|Path, include:list=[], exclude:list=[]) -> bool:
    """Determine if all of the individual parts in a path match none of the `exclude` 
    glob patterns first (if exclusions provided), and then at least one of the `include` 
    patterns (if provided). Return True if this is case, otherwise False."""
    a_path = Path(a_path)                                               # ensure that a_path is a Path object
    if not include and not exclude:
        return True                                                     # if neither inclusions nor exclusions were provided, then immediately return True 
    for part in a_path.parts:
        for pattern in exclude:                                         # if no exclusions are provided, this won't do anything, and go straight to checking inclusions
            if Path(part).match(pattern):
                return False                                            # if any parts match any of the exclusion patterns, return False
    if not include:                                                     
        return True                                                     # if there were no exclusion matches, but no inclusions are provided, then return True
    for part in a_path.parts:
        for pattern in include:
            if Path(part).match(pattern):
                return True                                             # if matches matches *any* of the inclusion patterns, return True
    return False                                                        # but if not at least one inclusion matches, then return False

def is_dir_empty(a_path:Path) -> bool:
    """Return `True` if `a_path` is an empty directory, and `False` if not"""
    if a_path.is_dir():
        for p in a_path.iterdir():
            if p:
                return False                                            # immediately return False if a directory, but not empty
        return True                                                     # return True if a direectory and is empty
    return False                                                        # return False if not a directory

def _handle_existing_filepath(filepath:Path, exists_action:str="ask") -> Path|None:
    """Check if the `filepath` exists, and apply the `exisits_action` to it if it does."""
    if filepath.is_file():                                              # if the file already exists, then handle it with `exists_action`                                               
        print(f'\nThe file path "{filepath}" already exisits.')
        # if the exists action is "ask", ask the user what to do for this file (modify the action based on input):
        if exists_action == 'ask':
            msg = 'Enter "rename", "replace", or "skip" to determine what to with this path'
            while True:
                print(msg)
                i = input("> ").strip().lower()                         # get user input for what to do
                if i in ("rename", "replace", "skip"):
                    exists_action = i                                   # if a valid action was entered, set action and break loop
                    break
        # apply solution to the file:
        if exists_action == 'rename':                                   # if rename: add '(#)' suffix to path
            copy_num = 1
            # if the path stem already ends with a '(#)', then make the copy_num be one greater than that number between the parenthesis:
            if (filepath.stem[-3] == '(') and (filepath.stem[-1] == ')'):
                try:
                    i = int(filepath.stem[-2])
                    copy_num = i+1
                except:
                    pass
            # apply '(#)' suffix to path stem (name without file extension):
            new_stem = filepath.stem + f'({copy_num})'                  
            filepath = filepath.with_stem(new_stem)
            print(f'renaming new file to "{filepath}"')
        elif exists_action == 'replace':
            print('existing file will be replaced')                     # if replace, do no file operations (would be replaced by any copy or move operations, so no need to do anything)
        elif exists_action == 'skip':
            print('skipping new file')
            return                                                      # if skip, return None
    return filepath                                                     # return the filepath


#--------- Path Listing Functions ---------#

def _get_paths(src_dir:str|Path, dst_dir:str|Path=None, exists_action:str="ask", include:list=[], exclude:list=[]):# -> list:
    """Get a recursive list of Path objects for all paths in a given directory path (`src_dir`).

    If a destination path is provided (`dst_dir`), then the list will instead contain tuples where 
    the first items are the same (all paths in `src_dir`), and the second items paths made from 
    replacing the parent portion of the source paths with the destination directory (`dst_dir`). 
    This can be used for functions which copy or move files from one directory to another.
    - If this is the case, then this function will also check for and apply the 
    `exists_action` to any destination file paths which already exist (existing dirs are ignored):
        - 'ask' - prompt the user what to do for each individual file.
        - 'rename' - keep the existing file and rename the current one.
        - 'replace' - delete the existing file, before copying/moving the current file.
        - 'skip' - don't copy/move this file, skip over it.

    If a list of strings with simple glob patterns for `include` and/or 
    `exclude` is provided, then this will only return the paths which have all of their 
    *relative* (so not including the parents directory) individual parts not 
    matching any of the exclusion patterns and/or matching at least one inclusion 
    pattern.
    - This does not work like regular glob patterns, but instead makes it so
    that only simple glob patterns will apply to each individual path component.
    Patterns targeting other directories or levels within the path will not be applied.
    - This function will always include the parent paths (containing directories) of 
    any path, even if those parent paths do not match inclusions themselves. This is
    so that the other functions in this module can easily display or create the 
    directories to contain the matching paths. However, if a path is a directory and 
    it matches an exclusion pattern, then it and none of its contents will be included.
    """
    src = Path(src_dir)
    dst = Path(dst_dir) if dst_dir else None                            # ensure that src_dir and dst_dir (if provided) are Path objects
    assert src.is_dir(), f'"{src}" is not an existing directory'        # ensure that src is an existing directory
    path_list = []                                                      # the list to store all valid paths, to be eventually returned
    parent_dirs = []                                                    # will be used to temporarily hold all non-empty directories
    for src_p in src.rglob('*'):                                        # `rglob('*')` is an easy way to get all paths recursively within the directory
        rel_src_path = src_p.relative_to(src)                           # get the relative version of the source path (without `src` parent directory)
        if (src_p.is_file() or is_dir_empty(src_p)) and not _path_parts_valid(rel_src_path, include, exclude):
            # Valid means all parts in the relative path match no exclusions and 
            # at least one inclusion (or there aren't any exlusions/inclusions).
            # If the path is a file or an empty directory, but not valid, skip it
            continue
        the_path = src_p
        the_parent = src_p.parent
        if dst:                                                         # if a destination directory was provided:
            dst_p = dst / rel_src_path                                  # make the destination path by combining the destination directory + the relative source path
            if src_p.is_file():
                dst_p = _handle_existing_filepath(dst_p, exists_action) # modify destination filepath if it exists (exisiting directories are ignored)
                if not dst_p:
                    continue                                            # don't append paths if destination path is None (result of "skip" exists_action)      
            the_path = (src_p, dst_p)                                   # change the_path to be a tuple of both the original source path + the destination path
            the_parent = (src_p.parent, dst_p.parent)                   # and change the_parent in the same way 
        if src_p.is_file() or is_dir_empty(src_p):
            path_list.append(the_path)                                  # If the source path is a file or empty directory, append the path(s) to to path_list
        else:
            parent_dirs.append(the_path)                                # otherwise if a directory containing other paths, append the path(s) to parent_dirs list
        # Non-empty directories are initially not added to path_list to prevent including directories 
        # which may have all non-valid files/dirs in them. But they may be added later only if they 
        # are the parents of existing valid paths, even if they themselves are not a valid match.
        if the_parent in parent_dirs:
            parent_dirs.remove(the_parent)
            path_list.append(the_parent)                                # if this current path's parent path is in the parent_dirs list, then remove it from that and add it to the path_list
    path_list.sort()
    return path_list                                                    # sort the path_list and return it

#--------- Main File Functions ---------#

def copy_move_dir(src:str|Path, dst:str|Path, move:bool=False, exists_action:str="ask", include:str=[], exclude:str=[]):
    """Copy or move all files, directories, and sub-files/directories from a source directory (`src`), to a 
    destination directory (`dst`).
    
    # Arguments: 
    - `src` and `dst`: path strings specifying the source and destination to copy from / move to.
    - `move`: a bool, where if False the directory will be copied, or if True it will be moved. If 
    not specified, False (so copy) is the default.
    - `exists_action`: a string saying what to do if the a file path in the source already exists in the 
    destination (directories will be ignored). Can be one of the following:
        - 'ask' - prompt the user what to do for each individual file.
        - 'rename' - keep the existing file and rename the current one.
        - 'replace' - delete the existing file, before copying/moving the current file.
        - 'skip' - don't copy/move this file, skip over it.
    - `include`: a lists of strings of a glob patterns which each individual part of the path must match in order to be included.
    - `exclude`: a lists of strings of a glob patterns which each individual part of the path must NOT match in order to be included.
    """
    # 1) Check/setup source and destination directories and args:
    valid_actions = ('ask', 'rename', 'replace', 'skip')                # check `exists_action` value is valid:
    assert exists_action in valid_actions, f'"{exists_action}" is not a valid action. Must be one of: {valid_actions}'
    src, dst = Path(src), Path(dst)                                     # make each path string into a Path object
    assert src.is_dir(), f'"{src}" must be an existing directory'       # check if src is an existing directory, and throw error if not
    if not dst.is_dir():
        print(f'\n"{dst}" is not an existing directory. Creating it now...')
        dst.mkdir(parents=True)                                         # check if dst is an existing directory, and create it if not
    # 2) Get list of all files and sub-dirs in source, determine the destination paths for each, and find and handle any existing paths:
    print(f'\nFinding all paths in "{src}"...')
    src_dst_paths = _get_paths(src, dst, exists_action, include, exclude)
    if not src_dst_paths:
        print(f"\nthere are no paths to {'move' if move else 'copy'}\n")
        return                                                          # if there are no paths, return immeditately
    # 3) Copy or move each file & dir from source to destination:
    print(f'\n{"Moving" if move else "Copying"} all files and directories from "{src}" to "{dst}":\n')
    src_count = len(src_dst_paths)                                      # get the total count of all paths that will be moved
    index_digit_len = len(str(src_count))                               # determine the number of digits of the number of paths in the source (used later for terminal output)
    for i, paths in enumerate(src_dst_paths):
        src_path, dst_path = paths
        if src_path.is_file():
            if not move:
                shutil.copy(src_path, dst_path)                         # if the source path is a file, copy it to the destination path
            else:
                shutil.move(src_path, dst_path)                         # or move it from source to destination
            path_name = dst_path.name                                   # set path_name for terminal display to be the name (final componenet) of the destination path
        elif src_path.is_dir():
            if not dst_path.is_dir():
                dst_path.mkdir()                                        # if the source path is a directory and the destination dir path doesn't exist, create the directory at the destination
            path_name = f"[{dst_path.name}]"                            # add sqaure brackets to name for directories
        # Display file/dir that was copied/moved in a tree:
        idx_str = f"{str(i+1).zfill(index_digit_len)}/{src_count}"      # create the string for the current index and pad it with zeroes so it's the same length as the number of paths in source 
        indent_str = '    ' * len(src_path.relative_to(src).parts)      # each indent is 4 spaces, and the number of parts of the relative source path (without `src` directory path) determines the number of indents to print
        print(idx_str + indent_str + path_name)
    print('\nDone!\n')

def permanent_delete(a_path:str|Path, confirm:bool=True):
    """Delete a file or directory (including anything within that directory).
    If `confirm` is true, will ask user for confirmation before deleting"""
    a_path = Path(a_path)                                               # ensure that a_path is a Path object
    assert a_path.exists(), f'\n"{a_path}" must be an existing file or directory\n' # ensure that the path leads to an exisiting path
    if confirm:                                                         # if `confirm` is True, as user for confirmation
        print(f'\n"{a_path}" will be permanently deleted.')
        print('Are you sure you want to continue? (Y/y)')
        if input('> ').lower() != "y":                                  # if user didn't enter 'y', then abort operation
            print('\nAborting delete. Nothing will be deleted\n')
            return
    print(f'\nDeleting "{a_path}"...')
    if a_path.is_file():
        a_path.unlink()
    elif a_path.is_dir():
        shutil.rmtree(a_path)
    print('\nDone!\n')
