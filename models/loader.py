import glob
import importlib.util
import logging
import sys
from pathlib import Path


class RoutesLoader:
    _initialized = False
    _loaded_modules = []

    def __init__(self):
        self._path = "./models/routes"

    def __iterate(self, files: list):
        for name in files:
            if name.find("__init__") != -1:
                continue
            # Returns -1 if string was not found
            with open(name) as file:
                route_name = Path(file.name).stem
                if route_name in self._loaded_modules:
                    return
                path = Path(files[files.index(name)])
                name = f"{self._path}.{route_name}.py"
                spec = importlib.util.spec_from_file_location(name, path)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules[self._path + route_name] = load
                self._loaded_modules.append(route_name)
                logging.info("Imported new route from %s.py", route_name)

    def load_all(self):
        if RoutesLoader._initialized:
            return
        # Load all routes from the directory
        self.__iterate(glob.glob(self._path + "/**/*.py", recursive=True))
        RoutesLoader._initialized = True
