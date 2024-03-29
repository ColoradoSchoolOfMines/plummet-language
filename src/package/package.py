import subprocess
import requests
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from headers.result import Result

#
# TODO: Make a standard for library packages. They will need to follow a certain
#       structure in order to be installed. If they do not follow this structure
#       this program should give a error code that can be ran through the
#       explain.py subprogram.
#
# TODO: Add functionality to keep track of what version each package is on.
#
# TODO: Add functionality to specify what version of a package to install or use.
#
# TODO: Make an online repo website that hosts official packages. This way the
#       user can just use the name of the package from the website and the url
#       for any other packages.
#
# TODO: Create repair_inventory() this will check the packages folder and
#       reconstruct the inventory file if it is corrupted or missing packages.
#       This should be easy since each package contains its own config.json that
#       contains all relevant information about the package.
#

INVENTORY_PATH = "./inventory.json"


def inventory_exists() -> None:
    """
    Checks if the inventory file exists, if it does not, it prints an error
    """

    if not os.path.exists(INVENTORY_PATH):
        print("Error: No inventory file found.")
        sys.exit(1)


def format_url_for_git(url: str) -> str:
    """
    Returns a url that is formatted for git.
    """

    if not url.endswith(".git"): url += ".git"
    return url


def get_repo_name_from_url(url: str) -> str:
    """
    Returns the name of the repository from the given url.
    """

    parts: list[str] = url.split("/")          # split the url by /
    repo = parts[-1]                           # get the last part of the url
    if repo.endswith(".git"): repo = repo[:-4] # remove .git from the end
    return repo                                # return the repo name


# TODO: Review and Refactor this function
def repair_inventory() -> Result:
    """
    Repairs the inventory file if it is corrupted or missing packages.
    """

    inventory = {}
    packages = list(filter(os.path.isdir, os.listdir("./packages")))

    # This is bad right now
    for package in packages:
        package_data = json.load(open(f"./packages/{package}/config.json", "r"))
        inventory.update(package_data.keys(), package_data.values())


def get_inventory_data() -> dict:
    """
    Returns the inventory file as a json object.
    """

    inventory_exists()
    
    return json.load(open(INVENTORY_PATH, "r"))


def set_inventory_data(new_data: dict) -> None:
    """
    Overwrite or create the inventory file with the given inventory.
    """

    inventory_exists()
    
    inventory: dict = get_inventory_data()

    # TODO: make it so that it errors if new_data has more than one key
    for package in new_data.keys():
        if package in inventory:
            print("Package already installed.")
            sys.exit(1)

    inventory.update(new_data)

    try:
        json.dump(inventory, open(INVENTORY_PATH, "w"), indent = 4)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# TODO: Review and Refactor this function
def package_installed(repository: str) -> Result:
    
    #
    # Check if the inventory file exists and is valid
    #

    inventory_exists()
    
    inventory = None
    with open(f"./inventory.json", "r") as inv:
        try:
            inventory = json.load(inv)
        except json.JSONDecodeError:
            # TODO: Add a error code for this
            return Result("Inventory file is corrupted.", False)
        except Exception as e:
            return Result(e, False)
        
    #
    # Check if the package is in the inventory file
    #

    return Result(repository in inventory, True)        


# TODO: Review and Refactor this function
# NOTE: for now this function will assume that package_installed has already
#       been called and that the package is not already installed
def add_package_to_inventory(repository: str) -> Result:

    #
    # Open the inventory file as a json object
    #

    inventory = None
    with open(f"./inventory.json", "r") as inv:
        try:
            inventory: dict = json.load(inv)
        except json.JSONDecodeError:
            return Result("Inventory file is corrupted.", False)
        except Exception as e:
            return Result(e, False)
        
    #
    # Add the package to the inventory variable
    #


# TODO: Review and Refactor this function
def remove_package_from_inventory(repository: str) -> Result:
    pass


# TODO: Review and Refactor this function
def help_command() -> None:
    print("Usage: Subcommand: package [install/uninstall/installed] [link to git repository]")


# TODO: Review and Refactor this function
def installed_packages() -> None:
    # _path = "./inventory.json"
    # inventory = None
    # if not os.path.exists(_path):
    #     print("Error: No inventory file found.")
    #     return inventory
    # else:
    #     with open(_path, "r") as f:
    #         try:
    #             inventory = json.load(f)
    #         except json.JSONDecodeError:
    #             print("Error: Inventory file is corrupted.")
    #             return inventory
    #         except Exception as e:
    #             print(f"Error: {e}")
    #             return inventory
    # # convert to a map
    # return 

    pass


# TODO: Review and Refactor this function
def install_package(repository: str) -> Result:

    #
    # Check if url is valid and that the repo is public
    #

    response = None
    try:
        response = requests.head(repository, allow_redirects = True)
    except requests.RequestException:
        return Result("Could not connect to the internet.", False)
    except Exception as e:
        return Result(e, False)

    #
    # Check status code
    #

    if response.status_code != 200:
        return Result("Repository is not public.", False)
    
    #
    # Check if the url points to a git repo
    #

    try:
        subprocess.check_output(["git", "ls-remote", "-q", repository])
    except subprocess.CalledProcessError:
        return Result("Invalid git repository.", False)
    except Exception as e:
        return Result(e, False)
    
    #
    # If the package is not already installed, add the package to the inventory.json file and try to install it
    #

    result = package_installed(repository)
    result.unwrap(result.value)
    if result.value: return Result("Package already installed.", True)

    #
    # Clone the repo into ./packages/ folder and add it to the inventory.json file
    #

    add_package_to_inventory(repository)
    repo_name = get_repo_name_from_url(repository)
    try:
        subprocess.call(["git", "clone", repository, f"./packages/{repo_name}"])
    except subprocess.CalledProcessError:
        return Result("Could not clone repository.", False)
    except Exception as e:
        return Result(e, False)

    #
    # Check if the repo is a valid package
    #

    # TODO: Implement this

    # If not, delete the repo, print an error code, exit

    # If the package is already installed, print an error code, exit

    return Result("Installed package.", True)


# TODO: Review and Refactor this function
def uninstall_package(repository: str) -> Result:
    pass


if __name__ == "__main__":

    print(get_inventory())
    exit(1)

    #
    # Parse command line arguments
    #

    if len(sys.argv) == 2 and sys.argv[1] == "help":
        help_command()
        sys.exit(0)

    if len(sys.argv) == 2 and sys.argv[1] == "installed":
        installed_packages()
        sys.exit(0)

    if len(sys.argv) != 3 or sys.argv[1] not in ["install", "uninstall"]:
        help_command()
        sys.exit(4)

    #
    # Run the subcommand
    #

    command = sys.argv[1]
    repository = sys.argv[2]

    # If repository does not end with .git, add it
    if not repository.endswith(".git"): repository += ".git"

    result = None
    if command == "install":
        result = install_package(repository)
    elif command == "uninstall":
        result = uninstall_package(repository)
    else:
        # This indicates a bug in the subprogram
        print("Error: Invalid command. -- This is a bug in the program.")
        sys.exit(5)

    #
    # Print the result of the command
    #
        
    try:
        print(result.unwrap(result.value))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)