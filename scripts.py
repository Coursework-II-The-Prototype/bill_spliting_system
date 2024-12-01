import subprocess


def format():
    subprocess.run(["poetry", "run", "black", "-l 79", "."])


def lint():
    subprocess.run(["poetry", "run", "flake8"])
