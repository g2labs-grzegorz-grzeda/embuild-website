#!/usr/bin/env python3
from os import getcwd, makedirs, path
from shutil import rmtree
from vt100logging import vt100logging_init, D, I, W, E
from subprocess import run, DEVNULL
from json import load as json_load, dump as json_dump
from tempfile import TemporaryDirectory

VERBOSE = False
EMBUILD_REPOSITORY = 'git@github.com:g2labs-grzegorz-grzeda/embuild-repository.git'


def set_verbose(verbose):
    global VERBOSE
    VERBOSE = verbose


def is_verbose():
    return VERBOSE


def run_process(cmd, cwd=getcwd()):
    run(cmd, check=True, shell=True, stdout=None if is_verbose()
        else DEVNULL, stderr=None if is_verbose()else DEVNULL)


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Library parser')
    parser.add_argument('destination_file', help='Path to destination file')
    parser.add_argument('-v', '--verbose',
                        action='store_true', help='verbose output')
    args = parser.parse_args()
    set_verbose(args.verbose)
    return args


def get_libraries():
    libraries = {}
    I(f'Cloning embuild repository')
    with TemporaryDirectory() as tempdir:
        run_process(f'git clone {EMBUILD_REPOSITORY} {tempdir}')
        with open(path.join(tempdir, 'repository.json')) as f:
            libraries = json_load(f)['libraries']
    return libraries


def get_libraries_info(libraries: dict) -> dict:
    libraries_info = {}

    for library_name, library_repository in libraries.items():
        I(f'Processing {library_name}')
        library_info = {}
        with TemporaryDirectory() as tempdir:
            run_process(f'git clone {library_repository} {tempdir}')
            if path.exists(path.join(tempdir, 'project.json')):
                with open(path.join(tempdir, 'project.json')) as f:
                    library_info['project'] = json_load(f)
            else:
                library_info['project'] = {}
            if path.exists(path.join(tempdir, 'README.md')):
                with open(path.join(tempdir, 'README.md')) as f:
                    library_info['readme'] = f.read()
            else:
                library_info['readme'] = ''
        libraries_info[library_name] = library_info

    return libraries_info


def store_libraries_info(libraries_info: dict, destination_file: str):
    I(f'Storing libraries info in {destination_file}')
    with open(destination_file, 'w') as f:
        json_dump(libraries_info, f, indent=2)


def main():
    try:
        args = parse_args()
        vt100logging_init('library-parser', args.verbose)
        libraries = get_libraries()
        libraries_info = get_libraries_info(libraries)
        store_libraries_info(libraries_info, args.destination_file)
    except Exception as e:
        E(e)
        exit(1)


if __name__ == '__main__':
    main()
