# auto-osint-v #

*An automated tool for Validating OSINT. This forms part of the final step of OSINT production as 
detailed by NATO's open source handbook (2001). This is a research artefact for my Dissertation at 
the University of Portsmouth*

## :file_folder: Installation

> **Note**
> First, please attempt to use the Google Colab, more info [below](#mortar_board-google-colab).


### Linux / Windows

- Clone this GitHub repository ```git clone https://github.com/UP2040499/auto-osint-v.git```
- Install conda (mamba also works) 
  - [Conda installation guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- Check conda is installed by checking the version: ```conda --version```
- Move into the repo
    ```bash
    cd ~/<install directory>/auto-osint-v 
    ```
- Create a conda OR mamba environment and install dependencies:
  - Install dependencies with conda:
    ```bash
    conda env create -f environment.yml -n auto-osint-v-python38
    ```
  - Install dependencies using mamba
    ```bash
    mamba env create -f environment.yml
    ```
- Activate conda environment and run the tool.
    ### Linux (bash)
    ```bash
    eval "$(conda shell.bash hook)" #copy conda command to shell
    conda activate auto-osint-v-python38
    python -m auto_osint_v.main
    ```
    ### Windows
    > :warning: Open an 'Anaconda Powershell Prompt' from Start Menu, then run the following.
    ```powershell
    conda init powershell
    conda activate auto-osint-v-python38
    python -m auto_osint_v.main
    ```

## :rocket: Usage

### :mortar_board: Google Colab
I strongly recommend using Google Colab to run this tool. However, the default machine in the Google
Colab performs worse than most local machines would (this is likely to do with CPU limits in place).

The Google Colab can be found [here](https://colab.research.google.com/drive/18_PY8sSLYn3ThPBJMMSAfrjj_CxXu1h1?usp=sharing)

The reason it is recommended to use Google Colab, is because it runs the tool remotely.
While performance on a local machine may be better, it is likely that the majority of the machine's
available resources (CPU, RAM) will be utilised by the tool. 

Use Google Colab to avoid hogging your computer's resources.

---
### :computer: Command line instructions:
```shell
python -m auto_osint_v.main <ARGS>
```

#### :construction: Arguments :construction:
```
arg1:
arg2:
...
```

### Example usage:
```bash
python -m auto_osint_v.main -arg1 -arg2
```


