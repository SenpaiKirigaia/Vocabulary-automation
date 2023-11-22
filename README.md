# Vocabulary Automation

## Overview
Vocabulary automator is a Python tool designed to expedite the process of compiling English vocabulary from PDF 
articles. It automates the extraction of word definitions and examples from the Cambridge Dictionary website.

## Installation
1. Clone the repository:

    ```sh
    git clone https://github.com/SenpaiKirigaia/Vocabulary-automation.git
    ```
2. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Run `vocabulary.py` with the desired flags and arguments:

    ```sh
    python vocabulary.py ARTICLE_NAME.pdf [-o OUTPUT_FILE] 
    ```
2. Use the `-o` to specify an output file.

3. Follow the prompts in interactive mode to select words.

## Configuration
- The script requires an internet connection to access the Cambridge Dictionary for definitions.
- Specify the path to the PDF file as the first argument.

## Example Run
```sh
python vocabulary.py example.pdf -o output.txt
```

## Output example
The script generates an output like this:
```sh
"development":
Definition:
    the process in which someone or something grows or changes and becomes more advanced
Dictionary example:
    healthy growth and development
Example from article:
    The drug development process is timeand resource-consuming, and it has a low probability of success.
```