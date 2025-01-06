from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os

class CustomInstallCommand(install):
    """Customized setuptools install command - installs Node.js dependencies."""
    def run(self):
        install.run(self)

        # Set the node_dir as the root of the project
        node_dir = os.path.abspath(os.path.dirname(__file__))
        package_json_path = os.path.join(node_dir, 'package.json')
        print(f"Looking for package.json in: {node_dir}")

        if not os.path.exists(package_json_path):
            print(f"package.json not found at {package_json_path}")
            raise FileNotFoundError(f"No package.json found at {package_json_path}")

        try:
            print("Installing Node.js dependencies...")
            subprocess.check_call(['npm', 'install'], cwd=node_dir)
        except subprocess.CalledProcessError as e:
            print("Failed to install Node.js dependencies:", e)
            raise

setup(
    name='pysatimage',
    version='0.0.16',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "requests>=2.32.3",
        "numpy>=2.0.0",
        "opencv-python>=4.8.0",
        "tqdm>=4.67.1",
        "xyconvert>=0.1.2",
        "pyyaml>=6.0.2",
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)
