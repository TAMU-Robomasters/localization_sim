# Localization Sim
A simulation of a robot and environment using pygame to test our localization algorithms.

## Setup
- Initialize the submodule `git submodule update --init`
- Make sure to copy the `.env.template` file to a file named `.env` before running.
- Install [uv](https://docs.astral.sh/uv/)
    - Mac/Linux
    `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Windows
    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- sync environment `uv sync`
- run code `uv run main.py`

TODO: Add more setup and usage instructions here.
