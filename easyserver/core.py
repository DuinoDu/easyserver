# type: ignore
import argparse
import importlib
import os
import subprocess
from abc import ABC, abstractmethod

import toml
from flask import Flask, jsonify, request
from termcolor import cprint


class Engine(ABC):
    def __init__(self, function):
        self.method = function["method"]
        self.__name__ = function["name"]

    @abstractmethod
    def __call__(self):
        pass


class ShellEngine(Engine):
    def __init__(self, function):
        super(ShellEngine, self).__init__(function)

    def __call__(self):
        params = request.args.to_dict()
        method = self.method.format(**params)
        (status, output) = subprocess.getstatusoutput(method)
        return jsonify(message=output)


class Python3Engine(Engine):
    def __init__(self, function):
        super(Python3Engine, self).__init__(function)
        self.py_func = Python3Engine.load_python(self.method)

    @staticmethod
    def load_python(method):
        """Load python mod and function."""
        assert "::" in method
        py_file, py_func = method.split("::")
        py_mod = py_file.split(".py")[0]
        mod = importlib.import_module(py_mod)
        assert py_func in dir(mod), f"Bad python method: {method}"
        return getattr(mod, py_func)

    def __call__(self):
        params = request.args.to_dict()
        result = self.py_func(**params)
        if not result:
            result = "done"
        return jsonify(message=result)


EngineFactory = {
    "bash": ShellEngine,
    "shell": ShellEngine,
    "python3": Python3Engine,
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", default="easyserver.toml", type=str, help="input config"
    )
    parser.add_argument(
        "--init-cfg",
        dest="init_cfg",
        action="store_true",
        help="create demo config",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    if args.init_cfg:
        cfg_template = os.path.join(os.path.dirname(__file__), "example")
        os.system(f"cp -r {cfg_template} .")
        cprint("saved in ./example", "green")
        return

    if not os.path.exists(args.config):
        cprint("Please provide config file by --config", "red")
        return
    config = toml.load(args.config)

    app = Flask(config["server"].pop("name", __name__))

    for function in config["function"]:
        assert function["engine"] in EngineFactory
        view_func = EngineFactory[function["engine"]](function)
        app.add_url_rule(function["path"], None, view_func)

    host = config["server"].pop("host", "0.0.0.0")
    port = config["server"].pop("port", 6160)
    app.run(
        host=host,
        port=port,
        **config["server"],
    )


if __name__ == "__main__":
    main()
