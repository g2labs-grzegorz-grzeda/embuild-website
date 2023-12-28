from jinja2 import Environment, FileSystemLoader
from os import path, makedirs
from shutil import rmtree
from argparse import ArgumentParser
from vt100logging import vt100logging_init, D, I, W, E
from json import load as json_load
from markdown import markdown

TEMPLATES_DIR = 'templates'
INDEX_TEMPLATE = 'index.html'
LIBRARY_TEMPLATE = 'library.html'

TITLE = "embuild"
AUTHOR = "G2Labs Grzegorz Grzęda"
LICENSE = "MIT"
DESCRIPTION = "embuild is a tool for C/CMake static library management"
GOOGLE_TAG = 'G-9EFJ6KQXGD'

VERBOSE = False


def set_verbose(verbose):
    global VERBOSE
    VERBOSE = verbose


def is_verbose():
    return VERBOSE


def script_path():
    return path.dirname(path.realpath(__file__))


def get_templates_dir():
    return path.join(script_path(), TEMPLATES_DIR)


def parse_args():
    parser = ArgumentParser(description='Generate website')
    parser.add_argument('libraries_info_file', type=str,
                        help='libraries info file')
    parser.add_argument('destination_dir', type=str,
                        help='destination directory')
    parser.add_argument('--verbose', '-v',
                        action='store_true', help='verbose output')
    args = parser.parse_args()
    set_verbose(args.verbose)
    return args


def get_template_environment() -> Environment:
    return Environment(loader=FileSystemLoader(get_templates_dir()))


def get_index_template(environment: Environment):
    return environment.get_template(INDEX_TEMPLATE)


def get_library_template(environment: Environment):
    return environment.get_template(LIBRARY_TEMPLATE)


def load_libraries_info(libraries_info_file: str) -> dict:
    with open(libraries_info_file) as f:
        return json_load(f)


def create_website(environment: Environment, libraries_info: dict, destination_dir: str):
    rmtree(destination_dir, ignore_errors=True)
    makedirs(destination_dir, exist_ok=True)
    environment.globals['title'] = TITLE
    environment.globals['author'] = AUTHOR
    environment.globals['license'] = LICENSE
    environment.globals['main_description'] = DESCRIPTION
    environment.globals['google_tag'] = GOOGLE_TAG
    with open(path.join(destination_dir, 'index.html'), 'w') as f:
        f.write(get_index_template(environment).render({
            'libraries': libraries_info.keys(),
        }))

    for name, content in libraries_info.items():
        readme = content['readme']
        libraries = content['project']['libraries'] if 'libraries' in content['project'] else [
        ]
        description = content['project']['description'] if 'description' in content['project'] else ''
        makedirs(path.join(destination_dir, name), exist_ok=True)
        with open(path.join(destination_dir, name,  'index.html'), 'w') as f:
            f.write(get_library_template(environment).render({
                'name': name,
                'repository': content['repository'],
                'description': description,
                'readme': markdown(readme),
                'libraries': libraries,
            }))


def main():
    args = parse_args()
    vt100logging_init('website-generator', args.verbose)
    env = get_template_environment()
    libraries_info = load_libraries_info(args.libraries_info_file)
    create_website(env, libraries_info, args.destination_dir)


if __name__ == '__main__':
    main()
