import subprocess


def format():
    subprocess.run(["poetry", "run", "black", "."])


def lint():
    subprocess.run(["poetry", "run", "flake8", ".", "--select=E9,F63,F7,F82"])
