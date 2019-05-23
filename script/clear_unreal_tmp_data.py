import os
import re
import sys
import shutil


WORKING_DIRECTORY = ''


def clear_folders(*args):
    words = list(args)

    # Default values
    if not words:
        words = ['Binaries', 'Intermediate', 'Saved']

    assert ([isinstance(word, str) for word in words])

    print 'Going to delete {} in {}'.format(', '.join(words), WORKING_DIRECTORY)
    pattern = '.+/({})$'.format('|'.join(words))

    matcher = re.compile(pattern)

    matching_dirs = []
    for root, sub, files in os.walk(WORKING_DIRECTORY):
        if matcher.match(root):
            matching_dirs.append(root)

    print '{} matching folders found'.format('No' if not matching_dirs else len(matching_dirs))

    for root in matching_dirs:
        print 'Deleting ' + root
        shutil.rmtree(root, True)


def main():
    args = sys.argv

    path_to_script = os.path.realpath(__file__)
    global WORKING_DIRECTORY
    WORKING_DIRECTORY = path_to_script[:path_to_script.rfind('/')]

    print 'Running {}'.format(path_to_script)
    print 'Working directory: {}'.format(WORKING_DIRECTORY)

    if len(args) == 1:
        print "Script must be launched with command line arguments. Aborting.".format(args[0])
        return

    else:
        func = args[1]

        func_args = []
        if len(args) > 2:
            func_args = args[2:]

        globals()[func](*func_args)

    print 'Job finished!'


main()
