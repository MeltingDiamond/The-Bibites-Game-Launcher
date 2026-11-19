# The-Bibites-Game-Launcher
A community made game launcher programmed in python to download and launch the bibites. This is an alternative to steam for people using The Bibites for free. Supports old versions.

tkinter is used to build the launcher

## How to try this launcher?
For latest version download and run the python source.
For stable release version built into executable go to the [releases page](https://github.com/MeltingDiamond/The-Bibites-Game-Launcher/releases)

If you find any bugs create a new [issue here](https://github.com/MeltingDiamond/The-Bibites-Game-Launcher/issues)

## Included mods
A list of the included mods and a short description.<br><small>You don't have to choose any of them</small>
- Sandboxing - Isolates the save and bibite location to the current instance

- BibiteFixed - Small BepInEx modpack for bug fixes and performance improvements for The Bibites (https://github.com/DrBwaa/BibiteFixes)

## Contribution
If you want to help just clone this repository onto your computer, open it in the program you use to program python, do your changes and push it back as a pull request. Make sure to add a fitting commit message explaining your change and please don't leave broken code when you are finished.

## Build locally
Clone or download repository create a install the required libraries using `pip install -r requirements.txt`.<br>

<sub style="color: orange;">Note on windows you need to manually install make and add it to path, wont be explained here</sub><br>
Run either `make` (global maybe) or os specific `make windows` or `make linux`
If you want to clean up the generated files `make clean-windows` or `make clean-linux`