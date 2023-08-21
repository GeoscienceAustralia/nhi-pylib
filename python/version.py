import sys
import ast
from git import Repo


def getVersion(path=''):
    """
    Retrieve the latest tag and commit of a file/repo

    :param path: Path of the repository to get version info for, defaults to ''
    :type path: str, optional
    :return: String of the latest repo tag and current commit hash
    :rtype: str
    """
    r = Repo(path, search_parent_directories=True)
    tags = sorted(r.tags, key=lambda t: t.tag.tagged_date)
    tag = tags[-1]
    commit = str(r.commit('HEAD'))
    return f"{tag} ({commit})"


def get_explicit_imports():
    """
    Retrieve a lit of explicit imports used in the current script

    :return: List of module names that are imported in the
    executing script.
    :rtype: list
    """
    script_path = sys.argv[0]  # Get the path of the script being executed
    with open(script_path, "r") as f:
        script_code = f.read()

    tree = ast.parse(script_code)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for name in node.names:
                imports.append(f"{module}.{name.name}")

    return imports


def get_loaded_module_versions():
    """
    Retrieve a dict of imported modules and their version numbers.
    The dict uses the module name as the key, and the version string
    (from the `__version__` attribute) as the value

    :return: Dict of module name/version pairs
    :rtype: Dict
    """
    loaded_modules = {}

    explicit_imports = get_explicit_imports()
    for module_name, module in sys.modules.items():
        if module_name in explicit_imports and hasattr(module, "__version__"):
            loaded_modules[module_name] = module.__version__

    return loaded_modules
