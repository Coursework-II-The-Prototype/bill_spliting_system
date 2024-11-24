import subprocess


def format():
    subprocess.run(["poetry", "run", "black", "."])


def lint():
    subprocess.run(["poetry", "run", "flake8"])
