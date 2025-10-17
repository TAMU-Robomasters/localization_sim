# Localization Sim
A simulation of a robot, sensors, and environment using pygame to test our auto-nav algorithms.

## Setup
- Initialize the submodule `git submodule update --init`
- Make sure to copy the `.env.template` file to a file named `.env` before running.
- Install [uv](https://docs.astral.sh/uv/)
    - Mac/Linux
    `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Windows
    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
> [!WARNING]
> You may have to restart your Windows machine after installing uv
- Sync environment `uv sync`
- Run code `uv run main.py`
> [!IMPORTANT]
> If someone changes the code in a submodule you have to run `git pull --recurse-submodules` instead of `git pull`. `git pull` only updates a pointer to a submodule commit it does NOT update the actually submodule code

## How To
Guides for common tasks

### How to Interact with Simulation
- Use 'wasd' to move robot around
- Use 'jk' to rotate robot
- Click on the screen to assign a new target position for pathfinding
- Type 'q' to exit program

### Adding and removing non-local packages/dependencies
- Add `uv add <package-name>`
- Remove `uv remove <package-name>`

### Editing and Testing Submodule Code Within Main Module Repo
All submodules are in the `lib/` directory.
- Go to submodules `cd lib/<submodule-name>`
- Code
- Go back to main module `cd ../../` or use a new terminal. Test code with pygame sim `uv run main.py` 
- When code works commit and push within `lib/<submodule-name>` directory 
- Go to main module directory
- Commit and push within main module directory
> [!NOTE]
> uv will automatically rebuild any local packages or submodules that were edited when you run `uv run main.py` in the main module directory

### Editing Submodule Code Within Submodule Repo
- Code and test
- Commit and push
- Go to main module repo and run `git pull --recurse-submodules`. New submodule code should appear.

### Adding New Submodule/Local Package
- Integrate uv with submodule:
    - Go to submodule repo
    - Create template project files with uv `uv init --lib --build-backend <backend-name>`
        - If your submodule is pure python code `backend-name = uv`
        - If you're creating a purely c/c++ package `backend-name = scikit-build-core`
        - Fill out template files and use uv and build backend documentation
    - Make sure `uv run code.py` doesn't fail
    - Commit and push
- Go to main module repo
- Add submodule `git submodule add <web-url or ssh-key> lib/<submodule-name>
- Add local dependency to uv `uv add lib/<submodule-name>`
- Add code that uses that submodule and test it with `uv run code.py`

TODO: Add how to add map
