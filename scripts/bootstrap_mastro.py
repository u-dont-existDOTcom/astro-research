"""Create a local Python3.12 research environment without changing global tools."""
import json
from pathlib import Path
import subprocess
import sys
import venv


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit('Use Python3.12: python3.12 scripts/bootstrap_mastro.py')
    root=Path(__file__).resolve().parent.parent
    environment=root/'.venv'
    if environment.exists() and not (environment/'pyvenv.cfg').is_file():
        raise SystemExit('Existing .venv is not a recognized virtual environment; inspect it before continuing')
    venv.EnvBuilder(with_pip=True).create(environment)
    python=environment/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    subprocess.run([str(python),'-m','pip','install','-r',str(root/'requirements-research.txt')],check=True)
    check='import json,importlib.metadata as m,numpy,openpyxl,swisseph; print(json.dumps({n:m.version(n) for n in ["numpy","openpyxl","pyswisseph"]}))'
    subprocess.run([str(python),'-c',check],check=True)
    print('Environment ready. Activate .venv, then run the commands in AGENTS.md.')


if __name__=='__main__':main()
