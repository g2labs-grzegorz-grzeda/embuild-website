from jinja2 import Environment, FileSystemLoader


def main():
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')
    template.render()


if __name__ == '__main__':
    main()
