import os
import yaml
import re

path_matcher = re.compile(r'\$\{([^}^{]+)\}')


def path_constructor(loader, node):
    ''' Extract the matched value, expand env variable, and replace the match '''
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    return os.environ.get(env_var) + value[match.end():]


yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)
with open('app.yaml') as yaml_file:
    try:
        CONFIG = yaml.load(yaml_file)
    except yaml.YAMLError as exc:
        print('Config file load exception')
        print(exc)
