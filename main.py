import configparser
import requests
import sys
import re


def get_package_dependencies(package_name):
    url = f'https://pypi.org/pypi/{package_name}/json'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            dependencies = data.get('info', {}).get('requires_dist', [])
            return dependencies if dependencies is not None else []
        else:
            return []
    except requests.RequestException as e:
        print(f"Error fetching dependencies for {package_name}: {e}")
        return []


def generate_dot(package_name, dependencies, dot_file, depth=0, max_depth=2):
    if depth == max_depth:
        return

    indent = "  " * depth
    dot_file.write(f"{indent}\"{package_name}\"\n")

    if dependencies:
        for dependency in dependencies:
            dep_name = extract_package_name(dependency)
            dot_file.write(f"{indent}\"{package_name}\" -> \"{dep_name}\"\n")
            generate_dot(dep_name, get_package_dependencies(dep_name), dot_file, depth + 1, max_depth)


def extract_package_name(dep_string):
    dep_string = re.sub(r'\[.*?\]', '', dep_string)
    return re.split('[ ;<>=]', dep_string)[0].strip()


def create_dot_file(package_name, max_depth, output_file):
    with open(output_file, 'w') as dot_file:
        dot_file.write("digraph G {\n")
        dependencies = get_package_dependencies(package_name)
        generate_dot(package_name, dependencies, dot_file, max_depth=max_depth)
        dot_file.write("}\n")


def main(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    package_name = config.get('settings', 'package_name')
    max_depth = config.getint('settings', 'max_depth')
    dot_file = config.get('settings', 'output_file')
    print(f"Generating DOT file for package '{package_name}': {dot_file}")

    create_dot_file(package_name, max_depth, dot_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)

    main(sys.argv[1])

