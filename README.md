![linting](assets/pylint.svg) ![python](https://img.shields.io/badge/python-3.10-blue.svg) ![minecraft](https://img.shields.io/badge/minecraft-1.19.0-blue.svg) ![node](https://img.shields.io/badge/node-18.16.0-blue.svg)
# Robot Parade
___
This repository is a jumping off point for creating Minecraft bots. The intended use is to have two scripts, one that allows the user to add a bot to there game that follows commands and does the actions. The second script will be a langchain iterative prompting algorithm that has the ability to make actions for Minecraft bots to use.

This project is still a work in progress, and will be constantly updated with new features.

To begin using the repository, you will need to 

1. Install Python v3.10.0
2. Create a Python virtual environment
3. Install the Python requirements.txt
4. Install Minecraft Java Edition v1.19.0
5. Install Node v18.16.0
6. Install the Node requirements
## Installation
### Install Python v3.10.0
___
Follow the link and install Python 3.10.0 for your machine.
https://www.python.org/downloads/release/python-3100/
### Create a Python virtual environment
___
After you have installed Python v3.10.0, you'll need to create a Python virtual environment to run the code.
A quick way to create an environment is to run this command in a command prompt.
```commandline
python -m venv your_env_name
```
After creating the environment, make sure to activate the environment.
```commandline
cd your_env_name/Scripts
activate
```
### Install the Python requirements.txt
___
To install all the needed dependencies run this command with the path to the repository's requirements.txt.
```commandline
pip install -r ./path_to_repository/requirements.txt
```
### Install Minecraft Java Edition v1.19.0
___
Follow the link and install Minecraft v1.19.0 for your machine.
https://www.minecraft.net/en-us/download
### Install Node v18.16.0
___
Follow the link and install Node v18.16.0 for your machine.
https://nodejs.org/en/download
### Install the Node requirements
___
To install all the needed dependencies run these commands.
```commandline
npm install mineflayer
```
## Command Line Arguments
### main.py Options and Arguments
___
| Argument  | Type   | Description                                                       | Default  |
|-----------|--------|-------------------------------------------------------------------|----------|
| -h, --host| \<str> | The ip address to the host machine or server. (i.e. 123.45.67.89) | Required |
| -p, --port| \<int> | The port on the host ip address. (i.e. 45678)                     | Required |
| -n, --name| \<str> | The name of the Minecraft bot being created.                      | "Bot"    |
### train.py Options and Arguments
___
| Argument  | Type   | Description                                                       | Default  |
|-----------|--------|-------------------------------------------------------------------|----------|
| -h, --host| \<str> | The ip address to the host machine or server. (i.e. 123.45.67.89) | Required |
| -p, --port| \<int> | The port on the host ip address. (i.e. 45678)                     | Required |
| -n, --name| \<str> | The name of the Minecraft bot being created.                      | "Bot"    |
## Contributing
___
To make changes to the repository, please follow the instructions in `CONTRIBUTING.md`.
## References
___
https://github.com/MineDojo/Voyager
