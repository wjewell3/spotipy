# PyMuse
<b>Objective:</b> Use Python to analyze your Spotify Top Artists to create a dynamic, personalized playlist  
<b>Audience:</b> Those interested in music and learning Python!  
<b>Prerequisite:</b> You must have a [Spotify account](https://accounts.spotify.com/en/login?continue=https)  
<b>Last Revised:</b> Nov 8, 2020 (Still in Beta testing - Please send feedback to jewell.will@gmail.com)

### Run the code yourself in a Jupyter Notebook!

1. Install Dependencies
    - [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
        - Use Git to save work at checkpoints and share your work 
    - Install <b>Python 3.7.3</b>
        - Windows/PCs: download Python 3.7.3 [here](https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64-webinstall.exe)
            - <b>IMPORTANT:</b> Click the option to "Add Python 3.7 to PATH". If you miss this, you can always uninstall and reinstall.
            - If you are experiencing difficulties from have another version of Python installed previously, check out the Stack Overflow article [here](https://stackoverflow.com/questions/5087831/how-should-i-set-default-python-version-in-windows)
            - Optional: If you want to manage multiple versions of Python on your Windows machine, check out pyenv-win [here](https://github.com/pyenv-win/pyenv-win)
        - Macs: check out the guide [here](https://opensource.com/article/19/5/python-3-default-mac)

2. Open Terminal (Mac) or CMD (Windows)
    - Navigate to a folder where you want to download this project/repo. 
        - E.g. If you want to download to your "Documents" folder:
            - Windows: Type ```cd C:\Users\<INSERT YOUR COMPUTER NAME>\Documents``` 
            - Macs: Type ```cd /Users/<INSERT YOUR COMPUTER NAME>/Documents```
            - <b>Please Note</b>: Your path will probably be a little different, depending on your computer.
    - Install the Git repo:
        - Type ```git clone https://github.com/wjewell3/spotipy.git```
        - Step into the repo. Type ```cd spotipy``` (not ```cd spotify```)
    - Install the Python dependendencies
        - Type ```pip install -r requirements.txt```
        - Pip is Python's package installer. It is reading the packages to be installed from requirements.txt
    - Launch Jupyter Notebook 
        - A Jupyter Notebook is an interactive notebook to run code and see the outputs in-line
        - Type ```jupyter notebook```
            - Select your default browser if prompted.
    - Click on <b>Create Spotify Playlist Using Python.ipynb</b> to open the notebook