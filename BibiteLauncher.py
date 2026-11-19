# To Do
# Make background image show behind other objects (remove their background)
import os, sys, zipfile, json, subprocess, platform, webbrowser, shutil, configparser, stat
from tkinter import Tk, Label, Frame, Canvas, Button, Checkbutton, Entry, Variable, BooleanVar, Listbox, Toplevel, Text, messagebox, Scrollbar
from pathlib import Path
from showinfm import show_in_file_manager
from threading import Thread
##from PIL import ImageTk, Image # Used for background image

if "__compiled__" in globals():
    # This resolves symlinks and returns the actual path to the binary
    scriptDir = Path(os.path.realpath(sys.argv[0])).parent
else:
    # Running in script mode
    scriptDir = Path(__file__).parent.absolute()

os_map = {
    "Windows": "Windows",
    "Darwin": "Mac",
    "Linux": "Linux"
}
OS_TYPE = os_map.get(platform.system(), "Unknown") # The os the program thinks it is running on

CONFIG_VERSION = 1 # The version of the current config. Updated only when conversion is needed or variables in the config file change name. Conversion needs to be coded in when its needed

APPLICATION_NAME = "BibiteLauncher Python" # Name of the application

# Create Tkinter window
window = Tk()
window.title(APPLICATION_NAME)

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set window size and position to fullscreen windowed
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
window.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

window.minsize(940, 820)

# BG image. Currently not used and code needs to be changed before it can be used
#imageFolderPath = os.path.join(scriptDir, "images")
#backgroundImage = Image.open(os.path.join(imageFolderPath, "Background.jpg"))
#backgroundImage = backgroundImage.resize((backgroundImage.size[0]*2, backgroundImage.size[1]*2), Image.LANCZOS)
#backgroundImageTk =ImageTk.PhotoImage(backgroundImage)
#background_label = Label(window, image=backgroundImageTk)
#background_label.place(x=0, y=0)


# Title label
title_label = Label(window, text=APPLICATION_NAME, font=("Arial", 24, "bold"))
title_label.pack(pady=(20, 10))

# Initialise default variables values and paths
availableVersions = []
availableBepInExVersions = []

dataPath = os.path.join(scriptDir, "data")
installationFolderPath = os.path.join(dataPath, "instances")
localVersionsFolderPath = os.path.join(dataPath, "versions")
localBepInExVersionsFolderPath = os.path.join(dataPath, "BepInEx")
includedModsFolderPath = os.path.join(scriptDir, "included-plugins")

def deleteFileOrFolder(path):
    """Deletes a file or folder"""
    if os.path.isfile(path):
        os.remove(path) # Delete file
    elif os.path.isdir(path):
        shutil.rmtree(path) # Delete directory (folder)

def cleanFolder(path):
    """Deletes all files and folders inside a folder"""
    for filename in os.listdir(path):
        filePath = os.path.join(path, filename)
        if os.path.isfile(filePath):
            os.remove(filePath) # Delete file
        elif os.path.isdir(filePath):
            shutil.rmtree(filePath) # Delete directory (folder)

def getIncludedModsList():
    """Returns a list of all mods that are included (stored in included-plugins)"""
    if os.path.isdir(includedModsFolderPath):
        return os.listdir(includedModsFolderPath)

def getAvailableVersions():
    """Returns two list of one for available game versions another for available BepInEx versions"""
    # Get all available game versions
    if os.path.isdir(localVersionsFolderPath):
        availableVersions = os.listdir(localVersionsFolderPath)
    else:
        os.makedirs(localVersionsFolderPath)
        availableVersions = []

    # Get all available BepInEx versions
    if os.path.isdir(localBepInExVersionsFolderPath):
        BepInExWindows64 = []
        for version in os.listdir(os.path.join(localBepInExVersionsFolderPath, "Windows64")):
            BepInExWindows64.append("Windows64/" + version)

        BepInExWindows32 = []
        for version in os.listdir(os.path.join(localBepInExVersionsFolderPath, "Windows32")):
            BepInExWindows32.append("Windows32/" + version)

        BepInExMac = []
        for version in os.listdir(os.path.join(localBepInExVersionsFolderPath, "Mac")):
            BepInExMac.append("Mac/" + version)

        BepInExLinux = []
        for version in os.listdir(os.path.join(localBepInExVersionsFolderPath, "Linux")):
            BepInExLinux.append("Linux/" + version)

        availableBepInExVersions = BepInExWindows64 + BepInExWindows32 + BepInExMac + BepInExLinux
    else:
        os.makedirs(localBepInExVersionsFolderPath)
        os.makedirs(os.path.join(localBepInExVersionsFolderPath, "Windows64"))
        os.makedirs(os.path.join(localBepInExVersionsFolderPath, "Windows32"))
        os.makedirs(os.path.join(localBepInExVersionsFolderPath, "Mac"))
        os.makedirs(os.path.join(localBepInExVersionsFolderPath, "Linux"))
        availableBepInExVersions = []
    return  availableVersions, availableBepInExVersions

def updateAvailableVersions():
    """Refreshes the listboxes with currently available game and BepInEx versions"""
    global availableVersions
    availableVersions, availableBepInExVersions = getAvailableVersions()
    versionsListbox.delete(0, "end")
    editVersionsListbox.delete(0, "end")
    versionsBepInExListbox.delete(0, "end")
    editVersionsBepInExListbox.delete(0, "end")
    if availableVersions == [] or availableBepInExVersions == []:
        missingVersionFrame.grid(column=4, row=3, sticky="nw", pady=40)
    else:
        missingVersionFrame.grid_forget()
    for version in availableVersions:
        versionsListbox.insert("end", version)
    for version in availableBepInExVersions:
        versionsBepInExListbox.insert("end", version)

def getGameOSVersion(name):
    """Return the os version the installed version of the bibites is built for"""
    gameFiles = os.listdir(os.path.join(installationFolderPath, name, "gameFolder"))
    version = "unknown"
    if "The Bibites.exe" in gameFiles:
        version = "Windows64"
    if "The Bibites 32x.exe" in gameFiles:
        version = "Windows32"
    if "The Bibites.app" in gameFiles:
        version = "Mac"
    if "The Bibites.x86_64" in gameFiles:
        version = "Linux"
    return version

def installBepInExToInstance(name, BepInExVersion):
    """Installs BepInEx to an installation"""
    instancesFolderPath = os.path.join(installationFolderPath, name)
    gameFolderPath = os.path.join(instancesFolderPath, "gameFolder")

    configFolderPath = os.path.join(instancesFolderPath, "BepInEx-config")
    BepInExConfigFolderPath = os.path.join(gameFolderPath, "BepInEx", "config")

    modsFolderPath = os.path.join(instancesFolderPath, "mods")
    BepInExPluginsFolderPath = os.path.join(gameFolderPath, "BepInEx", "plugins")

    splitBepInExVersion = BepInExVersion.split("/")
    BepInExOSVersionPath = os.path.join(localBepInExVersionsFolderPath, splitBepInExVersion[0], splitBepInExVersion[-1])
    with zipfile.ZipFile(os.path.join(BepInExOSVersionPath), "r") as BepInExZip:
        BepInExZip.extractall(gameFolderPath)

    # Symlink mods folder into BepInEx plugins folder
    if not os.path.isdir(modsFolderPath):
        os.makedirs(modsFolderPath)
    if not os.path.isdir(configFolderPath):
        os.makedirs(configFolderPath)

    if os.path.isdir(BepInExPluginsFolderPath):
        deleteFileOrFolder(BepInExPluginsFolderPath)
    if os.path.isdir(BepInExConfigFolderPath):
        deleteFileOrFolder(BepInExConfigFolderPath)

    if OS_TYPE == "Windows": # Special case for windows
        subprocess.check_call(["mklink", "/J", BepInExPluginsFolderPath, modsFolderPath], shell=True)
        subprocess.check_call(["mklink", "/J", BepInExConfigFolderPath, configFolderPath], shell=True)
    else: # Case for Linux and MacOS
        os.symlink(modsFolderPath, BepInExPluginsFolderPath, target_is_directory=True)
        os.symlink(configFolderPath, BepInExConfigFolderPath, target_is_directory=True)

def removeBepInExFromInstance(name):
    """Attempts to remove BepInEx from the installation without touching any of The Bibites game files by selectively deleting only the files/folders used by BepInEx"""
    instancesFolderPath = os.path.join(installationFolderPath, name)
    gameFolderPath = os.path.join(instancesFolderPath, "gameFolder")

    if os.path.isdir(os.path.join(gameFolderPath, "BepInEx")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "BepInEx"))

    if os.path.isfile(os.path.join(gameFolderPath, "run_bepinex.sh")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "run_bepinex.sh"))

    if os.path.isfile(os.path.join(gameFolderPath, "libdoorstop.so")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "libdoorstop.so"))

    if os.path.isfile(os.path.join(gameFolderPath, "changelog.txt")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "changelog.txt"))

    if os.path.isfile(os.path.join(gameFolderPath, ".doorstop_version")):
        deleteFileOrFolder(os.path.join(gameFolderPath, ".doorstop_version"))

    if os.path.isfile(os.path.join(gameFolderPath, "winhttp.dll")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "winhttp.dll"))

    if os.path.isfile(os.path.join(gameFolderPath, "doorstop_config.ini")):
        deleteFileOrFolder(os.path.join(gameFolderPath, "doorstop_config.ini"))

def repairInstance(name):
    """Poorly attempts to repair an instance that is broken"""
    # This needs to be updated
    instancesFolderPath = os.path.join(installationFolderPath, name)
    if os.path.isdir(installationFolderPath):
        modsFolderPath = os.path.join(instancesFolderPath, "mods")
        gameFolderPath = os.path.join(instancesFolderPath, "gameFolder")
        if not os.path.isdir(modsFolderPath):
            os.makedirs(modsFolderPath)
        instanceDataFilePath = os.path.join(instancesFolderPath, "instanceData.json")
        instanceData = {}
        if os.path.isfile(instanceDataFilePath):
            with open(instanceDataFilePath, "r") as instanceDataFile:
              instanceData = json.load(instanceDataFile)

        instanceData["CONFIG_VERSION"] = CONFIG_VERSION
        if not "version" in instanceData:
            instanceData["version"] = "error"
        else:
           with zipfile.ZipFile(os.path.join(localVersionsFolderPath, instanceData["version"]), "r") as gameZip:
                gameZip.extractall(os.path.join(gameFolderPath))

        if not "gameOSVersion" in instanceData:
            instanceData["gameOSVersion"] = getGameOSVersion(name)

        if not "showBepInExLog" in instanceData:
            instanceData["showBepInExLog"] = True

        if os.path.isdir(os.path.join(gameFolderPath, "BepInEx")):
            instanceData["BepInExInstalled"] = True
            instanceData["BepInExVersion"] = "installed"
        else:
            if "BepInExVersion" in instanceData and "BepInExInstalled" in instanceData:
                installBepInExToInstance(name, instanceData["BepInExVersion"])
            else:
                instanceData["BepInExInstalled"] = False
                instanceData["BepInExVersion"] = "error"

        with open(instanceDataFilePath, "w") as instanceDataFile:
            json.dump(instanceData, instanceDataFile)


    updateInstallationsList()

def generateInstance():
    """Generates an instance"""
    error = True
    name = installationNameInput.get()
    if versionsListbox.curselection():
        version = versionsListbox.get(versionsListbox.curselection())
    if versionsBepInExListbox.curselection():
        BepInExVersion = versionsBepInExListbox.get(versionsBepInExListbox.curselection())
    if includedModsListbox.curselection():
        includedModsToInstall = [includedModsListbox.get(i) for i in includedModsListbox.curselection()]
    showBepInExLog = bool(showBepInExLogVariable.get())

    if name != "" and "version" in locals():
        instancesFolderPath = os.path.join(installationFolderPath, name)
        gameFolderPath = os.path.join(instancesFolderPath, "gameFolder")
        modsFolderPath = os.path.join(instancesFolderPath, "mods")
        if not os.path.isdir(instancesFolderPath):
            os.makedirs(instancesFolderPath)
            if not os.path.isdir(modsFolderPath):
                os.makedirs(modsFolderPath)

            with zipfile.ZipFile(os.path.join(localVersionsFolderPath, version), "r") as gameZip:
                gameZip.extractall(os.path.join(gameFolderPath))
            instanceDataFilePath = os.path.join(instancesFolderPath, "instanceData.json")

            instanceData = {}
            instanceData["CONFIG_VERSION"] = CONFIG_VERSION
            instanceData["version"] = version
            instanceData["gameOSVersion"] = getGameOSVersion(name)
            if "BepInExVersion" in locals():
                installBepInExToInstance(name, BepInExVersion)
                instanceData["BepInExVersion"] = BepInExVersion
                instanceData["BepInExInstalled"] = True
                if instanceData["gameOSVersion"] == "Linux":
                    run_bepinex = os.path.join(gameFolderPath, "run_bepinex.sh")
                    st = os.stat(run_bepinex)
                    os.chmod(run_bepinex, st.st_mode | stat.S_IEXEC)
            else:
                instanceData["BepInExInstalled"] = False

            if "includedModsToInstall" in locals():
                for mod in includedModsToInstall:
                    includedModPath = os.path.join(includedModsFolderPath, mod)
                    instanceModPath = os.path.join(modsFolderPath, mod)
                    # Symlink mods into BepInEx plugins folder
                    if os.path.isfile(instanceModPath):
                        deleteFileOrFolder(instanceModPath)
                    if OS_TYPE == "Windows": # Copy files on Windows to avoid having to ask for administrator privileges
                        shutil.copy(includedModPath, instanceModPath)
                    else: # Case for Linux and MacOS
                        os.symlink(includedModPath, instanceModPath)

            instanceData["showBepInExLog"] = showBepInExLog

            with open(instanceDataFilePath, "w") as instanceDataFile:
                json.dump(instanceData, instanceDataFile)

            if instanceData["gameOSVersion"] == "Linux":
                The_Bibites = os.path.join(gameFolderPath, "The Bibites.x86_64")
                st = os.stat(The_Bibites)
                os.chmod(The_Bibites, st.st_mode | stat.S_IEXEC)

            error = False
        else:
            ""
    if not error:
        swapToMainFrame()
        updateInstallationsList()

def swapToNewInstallationFrame():
    """Swaps over to the new installation frame"""
    global currentFrame
    versionsListbox.selection_clear(0, "end")
    versionsBepInExListbox.selection_clear(0, "end")
    includedModsListbox.selection_clear(0, "end")
    scrollCanvas.delete("all")
    if availableVersions == []:
        missingVersionFrame.grid(column=4, row=3, sticky="nw", pady=40)
    else:
        missingVersionFrame.grid_forget()
    scrollCanvas.create_window((0, 0), window=newInstallationFrame, anchor="nw")

    currentFrame = newInstallationFrame

def swapToMainFrame():
    """Swaps over to the main frame (the first frame a user sees when they start the launcher)"""
    global currentFrame
    scrollCanvas.delete("all")
    scrollCanvas.create_window((0, 0), window=mainFrame, anchor="nw")
    currentFrame = mainFrame

def generateInstallationItem(name, version, BepInExVersion, error):
    """Generates an installation item (instances) that is displayed in a list on the main page"""
    frame = Frame(mainFrame, borderwidth=2, relief="solid")

    nameTextLabel = Label(frame, text="Name:")
    nameTextLabel.grid(column=0, row=0)

    nameLabel = Label(frame, text=name)
    nameLabel.grid(column=1, row=0, padx=20, sticky="w")

    versionTextLabel = Label(frame, text="Game Version:")
    versionTextLabel.grid(column=0, row=1)

    versionLabel = Label(frame, text=version)
    versionLabel.grid(column=1, row=1, padx=20, sticky="w")

    BepInExVersionTextLabel = Label(frame, text="BepInEx Version:")
    BepInExVersionTextLabel.grid(column=0, row=2)

    BepInExVersionLabel = Label(frame, text=BepInExVersion)
    BepInExVersionLabel.grid(column=1, row=2, padx=20, sticky="w")

    window.update()

    textLabelWith = max(versionLabel.winfo_width(), nameLabel.winfo_width(), BepInExVersionLabel.winfo_width())

    if error:
        repairInstanceButton = Button(frame, text="Repair instance", command=lambda: repairInstance(name))
        repairInstanceButton.grid(column=2, row=0, rowspan=2, padx=((406 - textLabelWith),0))
    else:
        playButton = Button(frame, text="Play", command=lambda: startPlayInThread(name))
        playButton.grid(column=2, row=0, rowspan=2, padx=((400 - textLabelWith),0))

    openFolderButton = Button(frame, text="Open Installation folder", command=lambda: openInstallationFolder(name))
    openFolderButton.grid(column=3, row=0, rowspan=2)

    if not error:
        editButton = Button(frame, text="Edit", command=lambda: edit(name))
        editButton.grid(column=4, row=0, rowspan=2)

    if error:
        # Change bg colour of everything
        errorColour = "salmon"
        frame.configure(background=errorColour)
        nameTextLabel.configure(background=errorColour)
        nameLabel.configure(background=errorColour)
        versionTextLabel.configure(background=errorColour)
        versionLabel.configure(background=errorColour)
        BepInExVersionTextLabel.configure(background=errorColour)
        BepInExVersionLabel.configure(background=errorColour)

    return frame

def updateInstallationsList():
    """Updates the list of instances displayed on the main page"""
    for child in mainFrame.winfo_children():
        if type(child) == type(Frame()):
            child.grid_forget()
    if os.path.isdir(installationFolderPath):
        installations = os.listdir(installationFolderPath)
        row = 1
        for installation in installations:
            instanceDataPath = os.path.join(installationFolderPath, installation, "instanceData.json")
            gameFolderPath = os.path.join(installationFolderPath, installation, "gameFolder")

            # check if instance is broken and load correctly based on how broken it is
            if os.path.isfile(instanceDataPath):
                with open(instanceDataPath, "r") as instanceDataFile:
                    data = json.load(instanceDataFile)

                if "BepInExVersion" in data:
                    BepInExVersion = data["BepInExVersion"]
                else:
                    BepInExVersion = None

                if os.path.isdir(gameFolderPath) and len(os.listdir(gameFolderPath)) > 2:
                    installationItem = generateInstallationItem(installation, data["version"], BepInExVersion, error=False)
                else:
                    installationItem = generateInstallationItem(installation, data["version"], BepInExVersion, error=True)
            else:
                installationItem = generateInstallationItem(installation, None, None, error=True)
            installationItem.grid(column=0, row=row, columnspan=5, sticky="w")
            row += 1

def openInstallationFolder(name):
    """Opens a folder in the operating systems file explorer"""
    show_in_file_manager(os.path.join(installationFolderPath, name))

def updateInstance(name):
    """Updates an instance based on the name"""
    instancesFolderPath = os.path.join(installationFolderPath, name)
    gameFolderPath = os.path.join(instancesFolderPath, "gameFolder")
    modsFolderPath = os.path.join(instancesFolderPath, "mods")
    instanceDataFilePath = os.path.join(instancesFolderPath, "instanceData.json")
    with open(instanceDataFilePath, "r") as instanceDataFile:
        instanceData = json.load(instanceDataFile)

    if editVersionsListbox.curselection():
        newVersion = editVersionsListbox.get(editVersionsListbox.curselection())
    if editVersionsBepInExListbox.curselection():
        NewBepInExVersion = editVersionsBepInExListbox.get(editVersionsBepInExListbox.curselection())
    if editIncludedModsListbox.curselection():
        includedModsToInstall = [editIncludedModsListbox.get(i) for i in editIncludedModsListbox.curselection()]
    showBepInExLog = editShowBepInExLogVariable.get()

    if "newVersion" in locals() and newVersion != instanceData["version"]:
        cleanFolder(gameFolderPath)
        with zipfile.ZipFile(os.path.join(localVersionsFolderPath, newVersion), "r") as gameZip:
            gameZip.extractall(gameFolderPath)

        instanceData["version"] = newVersion
        instanceData["gameOSVersion"] = getGameOSVersion(name)
        if instanceData["gameOSVersion"] == "Linux":
                The_Bibites = os.path.join(gameFolderPath, "The Bibites.x86_64")
                st = os.stat(The_Bibites)
                os.chmod(The_Bibites, st.st_mode | stat.S_IEXEC)
    if editDeleteBepInExVariable.get():
        removeBepInExFromInstance(name)
        instanceData["BepInExInstalled"] = False
        if "BepInExVersion" in instanceData:
            instanceData.pop("BepInExVersion")
    else:
        if "BepInExVersion" in instanceData:
            oldBepInExVersion = instanceData["BepInExVersion"]
        else:
            oldBepInExVersion = None
        if "NewBepInExVersion" in locals() and NewBepInExVersion != oldBepInExVersion:
            removeBepInExFromInstance(name)
            installBepInExToInstance(name, NewBepInExVersion)
            instanceData["BepInExVersion"] = NewBepInExVersion
            instanceData["BepInExInstalled"] = True
            if instanceData["gameOSVersion"] == "Linux":
                run_bepinex = os.path.join(gameFolderPath, "run_bepinex.sh")
                st = os.stat(run_bepinex)
                os.chmod(run_bepinex, st.st_mode | stat.S_IEXEC)

    if "includedModsToInstall" in locals():
        for mod in includedModsToInstall:
            includedModPath = os.path.join(includedModsFolderPath, mod)
            instanceModPath = os.path.join(modsFolderPath, mod)
            # Symlink mods into BepInEx plugins folder
            if os.path.isfile(instanceModPath):
                deleteFileOrFolder(instanceModPath)
            if OS_TYPE == "Windows": # Copy files on Windows to avoid having to ask for administrator privlages
                shutil.copy(includedModPath, instanceModPath)
            else: # Case for Linux and MacOS
                os.symlink(includedModPath, instanceModPath)

    instanceData["showBepInExLog"] = showBepInExLog

    with open(instanceDataFilePath, "w") as instanceDataFile:
        json.dump(instanceData, instanceDataFile)
    swapToMainFrame()
    updateInstallationsList()

def edit(name):
    """Swaps over to the edit instance page and inputs the values from an instance to get ready for editing"""
    global currentFrame
    instancesFolderPath = os.path.join(installationFolderPath, name)

    scrollCanvas.delete("all")
    currentFrame = EditInstanceFrame
    instanceName.configure(text=f"Editing: {name}")

    with open(os.path.join(instancesFolderPath, "instanceData.json"), "r") as instanceDataFile:
        data = json.load(instanceDataFile)

    editInstalledVersionText.configure(text=f"Current version: {data["version"]}")
    editUpdateButton.configure(command=lambda: updateInstance(name))

    if "showBepInExLog" in data:
        editShowBepInExLogVariable.set(data["showBepInExLog"])
    else:
        editShowBepInExLogVariable.set(True)
    editShowBepInExLogCheckbox.configure(variable=editShowBepInExLogVariable)

    editDeleteBepInExVariable.set(False)
    editDeleteBepInExCheckbox.configure(variable=editDeleteBepInExVariable)

    editVersionsListbox.selection_clear(0, "end")
    editVersionsBepInExListbox.selection_clear(0, "end")
    editIncludedModsListbox.selection_clear(0, "end")

    scrollCanvas.create_window((0, 0), window=EditInstanceFrame, anchor="nw")

def startPlayInThread(name):
    """Runs the play function in a thread to avoid making the launcher unresponsive"""
    playThread = Thread(target=play, args=[name])
    playThread.start()

def play(name):
    """Starts the game stored inside an instance based on the name of an instance"""
    instancesFolderPath = os.path.join(installationFolderPath, name)

    with open(os.path.join(instancesFolderPath, "instanceData.json"), "r") as instanceDataFile:
        instanceData = json.load(instanceDataFile)

    gameOSVersion = instanceData["gameOSVersion"]
    if "BepInExInstalled" in instanceData:
        BepInExInstalled = instanceData["BepInExInstalled"]
    else:
        BepInExInstalled = False

    showBepInExLog = instanceData["showBepInExLog"]

    gameFolder = os.path.join(installationFolderPath, name, "gameFolder")
    if gameOSVersion == "Windows64":
        gamePath = os.path.join(gameFolder, "The Bibites.exe")
    elif gameOSVersion == "Windows32":
        gamePath = os.path.join(gameFolder, "The Bibites 32x.exe")
    elif gameOSVersion == "Mac":
        gamePath = os.path.join(gameFolder, "The Bibites.app")
    elif gameOSVersion == "Linux":
        gamePath = os.path.join(gameFolder, "The Bibites.x86_64")

    if OS_TYPE == "Windows":
        if gameOSVersion == "Windows64" or gameOSVersion == "Windows32":
            if BepInExInstalled:
                BepInExcfgPath = os.path.join(gameFolder, "BepInEx", "config", "BepInEx.cfg")
                if os.path.exists(BepInExcfgPath):
                    config = configparser.ConfigParser()
                    config.optionxform = str
                    config.read(BepInExcfgPath)
                    config['Logging.Console']['Enabled'] = str(showBepInExLog)
                    with open(BepInExcfgPath, 'w') as configfile:
                        config.write(configfile)

                theBibites = subprocess.Popen([gamePath], stdout=subprocess.PIPE)
            else:
                theBibites = subprocess.Popen([gamePath], stdout=subprocess.PIPE)
        else:
            messagebox.showerror("Version incompatible with windows", f"{gameOSVersion} version can't launch on windows")
    elif OS_TYPE == "Mac":
        if gameOSVersion == "Windows64" or gameOSVersion == "Windows32":
            theBibites = subprocess.Popen(["wine", gamePath], stdout=subprocess.PIPE)
        elif gameOSVersion == "Mac":
            theBibites = subprocess.Popen([gamePath], stdout=subprocess.PIPE)
        else:
            messagebox.showerror("Version incompatible with MacOS", f"{gameOSVersion} version can't launch on MacOS")
    elif OS_TYPE == "Linux":
        if gameOSVersion == "Windows64" or gameOSVersion == "Windows32":
            # Running Windows version on Linux
            if BepInExInstalled:
                BepInExcfgPath = os.path.join(gameFolder, "BepInEx", "config", "BepInEx.cfg")
                if os.path.exists(BepInExcfgPath):
                    config = configparser.ConfigParser()
                    config.optionxform = str
                    config.read(BepInExcfgPath)
                    config['Logging.Console']['Enabled'] = str(showBepInExLog)
                    with open(BepInExcfgPath, 'w') as configfile:
                        config.write(configfile)

                env = os.environ.copy()
                env['WINEDLLOVERRIDES'] = 'winhttp.dll=n,b'
                theBibites = subprocess.Popen(["wine", gamePath], env=env, stdout=subprocess.PIPE)
            else:
                theBibites = subprocess.Popen(["wine", gamePath], stdout=subprocess.PIPE)
        elif gameOSVersion == "Linux":
            # Running Linux version on Linux
            if BepInExInstalled:
                BepInExcfgPath = os.path.join(gameFolder, "BepInEx", "config", "BepInEx.cfg")
                if os.path.exists(BepInExcfgPath):
                    config = configparser.ConfigParser()
                    config.optionxform = str
                    config.read(BepInExcfgPath)
                    config['Logging.Console']['Enabled'] = str(showBepInExLog)
                    with open(BepInExcfgPath, 'w') as configfile:
                        config.write(configfile)

                theBibites = subprocess.Popen(
                    ["bash", "-c",
                     f'exec -a "run_bepinex.sh" "{os.path.join(gameFolder, "run_bepinex.sh")}" "{gamePath}" "-force-vulkan"'],
                    stdout=subprocess.PIPE
                    )
            else:
                theBibites = subprocess.Popen([gamePath, "-force-vulkan"], stdout=subprocess.PIPE)
        else:
            messagebox.showerror("Version incompatible with Linux", f"{gameOSVersion} version can't launch on Linux")

    if "theBibites" in locals():
        # Create log window
        logWindow = Toplevel(window)
        logWindow.title("The Bibites Log for instance: " + name)
        logText = Text(logWindow, height=50, width=80, state='disabled', bg='white', fg='black', font=('Consolas', 10))
        logText.pack()
        terminateGameWindowButton = Button(logWindow, text="Terminate The Bibites", command=theBibites.terminate)
        terminateGameWindowButton.pack()
        killGameWindowButton = Button(logWindow, text="If frozen Kill The Bibites", command=theBibites.kill)
        killGameWindowButton.pack()

        # Capture the log from the running game
        poll = None
        while poll is None:
            poll = theBibites.poll()

            logText.config(state='normal')
            logText.insert('end', f"{theBibites.stdout.readline().decode()}")
            logText.see('end')
            logText.config(state='disabled')

availableVersions, availableBepInExVersions = getAvailableVersions()

# Setup main frame
scrollCanvas = Canvas(window, width=250, height=300)

scrollbar = Scrollbar(window, orient="vertical", command=scrollCanvas.yview)
scrollbar.pack(side="right", fill="y")

scrollCanvas.configure(yscrollcommand=scrollbar.set)

mainFrame = Frame(scrollCanvas)

scrollCanvas.create_window((0, 0), window=mainFrame, anchor="nw")

mainFrame.bind(
    "<Configure>",
    lambda e: scrollCanvas.configure(scrollregion=scrollCanvas.bbox("all"))
)

currentFrame = mainFrame
scrollCanvas.pack(side="left", fill="both", expand=True)

newInstallationButton = Button(mainFrame, text="New installation", command=swapToNewInstallationFrame)
newInstallationButton.grid(column=0, row=0, sticky="w")
mainFrame.update()

openVersionsFolderButton = Button(mainFrame, text="Open versions folder", command=lambda: show_in_file_manager(localVersionsFolderPath))
openVersionsFolderButton.grid(column=0, row=0, sticky="nw", padx=newInstallationButton.winfo_width())
mainFrame.update()

openBepInExFolderButton = Button(mainFrame, text="Open BepInEx folder", command=lambda: show_in_file_manager(localBepInExVersionsFolderPath))
openBepInExFolderButton.grid(column=0, row=0, sticky="nw", padx=(newInstallationButton.winfo_width() + openVersionsFolderButton.winfo_width()))
mainFrame.update()

refreshInstallationListButton = Button(mainFrame, text="Refresh installation list", command=updateInstallationsList)
refreshInstallationListButton.grid(column=0, row=0, sticky="nw", padx=(newInstallationButton.winfo_width() + openVersionsFolderButton.winfo_width() + openBepInExFolderButton.winfo_width()))
mainFrame.update()

# Setup new installation frame
newInstallationFrame = Frame(scrollCanvas)

nameText = Label(newInstallationFrame, text="Name")
nameText.grid(column=0, row=0, sticky="w")

installationNameInput = Entry(newInstallationFrame)
installationNameInput.grid(column=0, row=1, columnspan=4, sticky="ew")

VersionText = Label(newInstallationFrame, text="Version")
VersionText.grid(column=0, row=2, sticky="w")

availableVersionsVariable = Variable(value=availableVersions)
versionsListbox = Listbox(newInstallationFrame, font=("Arial", 12), width=40, listvariable=availableVersionsVariable, selectmode="single", exportselection=False)
versionsListbox.grid(column=0, row=3, columnspan=4, sticky="ew")

availableBepInExVersionsVariable = Variable(value=availableBepInExVersions)
versionsBepInExListbox = Listbox(newInstallationFrame, font=("Arial", 12), width=40, listvariable=availableBepInExVersionsVariable, selectmode="single", exportselection=False)
versionsBepInExListbox.grid(column=0, row=4, columnspan=4, sticky="ew")

includedModsVariable = Variable(value=getIncludedModsList())
includedModsListbox = Listbox(newInstallationFrame, font=("Arial", 12), width=40, listvariable=includedModsVariable, selectmode="multiple", exportselection=False)
includedModsListbox.grid(column=0, row=5, columnspan=4, sticky="ew")

showBepInExLogVariable = BooleanVar(value=True)
showBepInExLogCheckbox = Checkbutton(newInstallationFrame, text="Show BepInEx log?", variable=showBepInExLogVariable, onvalue=True, offvalue=False)
showBepInExLogCheckbox.grid(column=0, row=6, sticky="ew")

updateVersionsButton = Button(newInstallationFrame, text="Update available versions", command=updateAvailableVersions)
updateVersionsButton.grid(column=4, row=2, sticky="nw")
newInstallationFrame.update()

openVersionsFolderButton = Button(newInstallationFrame, text="Open versions folder", command=lambda: show_in_file_manager(localVersionsFolderPath))
openVersionsFolderButton.grid(column=4, row=3, sticky="nw")
newInstallationFrame.update()

openBepInExFolderButton = Button(newInstallationFrame, text="Open BepInEx folder", command=lambda: show_in_file_manager(localBepInExVersionsFolderPath))
openBepInExFolderButton.grid(column=4, row=3, sticky="nw", padx=openVersionsFolderButton.winfo_width())

installButton = Button(newInstallationFrame, text="Make Instance", command=generateInstance)
installButton.grid(column=2, row=6)

cancelButton = Button(newInstallationFrame, text="Cancel", command=swapToMainFrame)
cancelButton.grid(column=1, row=6)

# Missing version popup text
def callback(url):
    webbrowser.open_new_tab(url)

missingVersionFrame = Frame(newInstallationFrame)
missingVersionText = Label(missingVersionFrame, text="You don't have any versions downloaded.")
missingVersionText.grid(column=0, row=0, sticky="w")
missingVersionText = Label(missingVersionFrame, text="You can download the latest version from itch:")
missingVersionText.grid(column=0, row=1, sticky="w")
link1 = Label(missingVersionFrame, text="https://thebibites.itch.io/the-bibites", fg="blue", cursor="hand2")
link1.bind("<Button-1>", lambda e: callback("https://thebibites.itch.io/the-bibites"))
link1.grid(column=0, row=2, sticky="w")
missingVersionText = Label(missingVersionFrame, wraplength=300, justify="left", text="For older version you can download it from Melting Diamonds archiving repository:")
missingVersionText.grid(column=0, row=3, sticky="w")
link2 = Label(missingVersionFrame, text="https://github.com/MeltingDiamond/The-Bibites-Downloads", fg="blue", cursor="hand2")
link2.bind("<Button-1>", lambda e: callback("https://github.com/MeltingDiamond/The-Bibites-Downloads"))
link2.grid(column=0, row=4, sticky="w")
missingVersionText = Label(missingVersionFrame, text="Place downloaded versions in zip format in the versions folder.")
missingVersionText.grid(column=0, row=5, sticky="w")
missingVersionText = Label(missingVersionFrame, text="Download BepInEx from the official Github repository:")
missingVersionText.grid(column=0, row=6, sticky="w")
link3 = Label(missingVersionFrame, text="https://github.com/BepInEx/BepInEx/releases", fg="blue", cursor="hand2")
link3.bind("<Button-1>", lambda e: callback("https://github.com/BepInEx/BepInEx/releases"))
link3.grid(column=0, row=7, sticky="w")

# Setup edit instance frame
EditInstanceFrame = Frame(scrollCanvas)

instanceName = Label(EditInstanceFrame, font=("Arial", 16))
instanceName.grid(column=0, row=0, sticky="w")

editInstalledVersionText = Label(EditInstanceFrame, text="Version")
editInstalledVersionText.grid(column=0, row=1, sticky="w")

editVersionsListbox = Listbox(EditInstanceFrame, font=("Arial", 12), width=50, listvariable=availableVersionsVariable, selectmode="single", exportselection=False)
editVersionsListbox.grid(column=0, row=2, columnspan=4, sticky="ew")

editVersionsBepInExListbox = Listbox(EditInstanceFrame, font=("Arial", 12), width=50, listvariable=availableBepInExVersionsVariable, selectmode="single", exportselection=False)
editVersionsBepInExListbox.grid(column=0, row=3, columnspan=4, sticky="ew")

editIncludedModsListbox = Listbox(EditInstanceFrame, font=("Arial", 12), width=40, listvariable=includedModsVariable, selectmode="multiple", exportselection=False)
editIncludedModsListbox.grid(column=0, row=4, columnspan=4, sticky="ew")

editUpdateVersionsButton = Button(EditInstanceFrame, text="Update available versions", command=updateAvailableVersions)
editUpdateVersionsButton.grid(column=4, row=2, sticky="n")

editDeleteBepInExVariable = BooleanVar()
editDeleteBepInExCheckbox = Checkbutton(EditInstanceFrame, text="Delete BepInEx?", variable=editDeleteBepInExVariable, onvalue=True, offvalue=False)
editDeleteBepInExCheckbox.grid(column=0, row=5, sticky="w")

editShowBepInExLogVariable = BooleanVar()
editShowBepInExLogCheckbox = Checkbutton(EditInstanceFrame, text="Show BepInEx log?", variable=editShowBepInExLogVariable, onvalue=True, offvalue=False)
editShowBepInExLogCheckbox.grid(column=0, row=5, sticky="e", padx=(0, 10))

editUpdateButton = Button(EditInstanceFrame, text="Update Instance")
editUpdateButton.grid(column=2, row=5)

editCancelButton = Button(EditInstanceFrame, text="Cancel", command=swapToMainFrame)
editCancelButton.grid(column=1, row=5)

if __name__ == "__main__":
    # Functions to run on first boot
    updateInstallationsList()

    window.mainloop()
