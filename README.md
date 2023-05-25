# auto-osint-v #

*An automated tool for Validating OSINT. This forms part of the final step of OSINT production as 
detailed by NATO's open source handbook (2001). This is a research artefact for my Dissertation at 
the University of Portsmouth*

See the results of the different Entity Recognition language models [here](https://up2040499.github.io/auto-osint-v/NER_results_comparison/compare_two_models.html). 
Note how the spaCy standard 'en_core_web_sm' NER model struggles to recognise military information compared to the 
model used for this project using the Defence Science and Technology Laboratory 're3d' dataset.

## 📁 Installation

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
    python -m auto_osint_v
    ```
    ### Windows
    > :warning: Open an 'Anaconda Powershell Prompt' from Start Menu, then run the following:
    ```powershell
    conda init powershell
    conda activate auto-osint-v-python38
    python -m auto_osint_v
    ```

## 🚀 Usage

### 🎓 Google Colab
I strongly recommend using Google Colab to run this tool. However, the default machine in the Google
Colab performs worse than most local machines would (this is likely to do with CPU limits in place).

The Google Colab can be found [here](https://colab.research.google.com/drive/18_PY8sSLYn3ThPBJMMSAfrjj_CxXu1h1?usp=sharing)

The reason it is recommended to use Google Colab, is because it runs the tool remotely.
While performance on a local machine may be better, it is likely that the majority of the machine's
available resources (CPU, RAM) will be utilised by the tool. 

Use Google Colab to avoid hogging your computer's resources.

---
### 💻 Command line instructions:
```shell
python -m auto_osint_v <ARGS>
```

#### 🚧 Arguments 🚧
The following descriptions can also be found by running `auto_osint_v -h`.

- `-s/--Silent` Assumes you have already entered the intelligence statement 
  [here](auto_osint_v/data_files/intelligence_file.txt)
- `-n/--NoEditor` Input intelligence statement into command line rather than into text editor.
- `--html` Output will be in HTML (default: csv).
- `-m/--markdown` Output will be in markdown (default: csv).
- `-f/--FileToUse` Specify the file to read the intelligence statement from
- `-p/--output_postfix` Specify the output file's postfix, e.g. 'output3.txt' rather than default 
  'output.txt'

### Example usage:

#### Typical use / First time use

```shell
python -m auto_osint_v
```

#### Use with options

This reads the statement from the existing intelligence file, and output the results in a 
markdown file called 'output0.md'.

```shell
python -m auto_osint_v -s -m -p 0
```
The postfix (0 in this case) is useful if you are running the tool multiple times and want to save the results 
separately.

