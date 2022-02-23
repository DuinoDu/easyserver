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


def create_template_config(toml_file, py_file):
    """Create template config."""

    toml_str = r"""
[server]
name = "hello"
host = "0.0.0.0"
port = 8800

# TEST

[[function]]
name = "test1"
path = "/"
method = "echo 'hello, easyserver'"
engine = "shell"

[[function]]
name = "test2"
path = "/hello"
method = "echo {name} {book}"
engine = "bash"

[[function]]
name = "test3"
path = "/python"
method = "hello_easyserver.py::hello"
engine = "python3"

[[function]]
name = "test4"
path = "/get_sum"
method = "hello_easyserver.py::get_sum"
engine = "python3"
    """

    py_str = r'''
def hello(name: str, config: str) -> None:
    """Test python function.

    Args:
        name: demo input args1.
        config: demo input args2.

    """
    print(name, config)


def get_sum(a: float, b: float) -> float:
    """Test python function.

    Args:
        a: demo input args1.
        b: demo input args2.

    """
    return float(a) + float(b)

    '''

    with open(toml_file, "w") as fid:
        fid.write(toml_str)
    with open(py_file, "w") as fid:
        fid.write(py_str)


def main():
    args = parse_args()

    if args.init_cfg:
        f1, f2 = "hello_easyserver.toml", "hello_easyserver.py"
        create_template_config(f1, f2)
        cprint(f"saved in {f1} {f2}", "green")
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
