import sys
import requests
from bs4 import BeautifulSoup
import fitz
import getch
import re


def fetch_definition(word):
    """
    Fetch the definition and example of a word from Cambridge Dictionary.

    Args:
    word (str): The word to search for.

    Returns:
    tuple: Definition and example sentence of the word, or None if not found.
    """
    url = 'https://dictionary.cambridge.org/dictionary/english/{}'.format(word)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    definition = soup.find("div", {"class": "def ddef_d db"})
    examples = soup.find_all("div", {"class": "examp dexamp"})

    if not definition or not examples:
        return None

    return definition.get_text()[:-2], examples[0].get_text().lstrip(' ')


def process_word(word, sentences, output_file):
    """
    Process a word by fetching its definition and finding an example in the article.

    Args:
    word (str): The word to process.
    sentences (list): List of sentences from the article.
    output_file (file object): File to write the output to.
    """
    result = fetch_definition(word)
    if not result:
        print("Word {} not found in the dictionary!".format(word))
        return

    definition, example = result
    print("\n\"{}\":\nDefinition:\n\t{}\nDictionary example:\n\t{}".format(word, definition, example), file=output_file)

    present = False
    for sentence in sentences:
        if word in sentence:
            sentence_formatted = (sentence.replace('\n', ' ') + '.').lstrip(' ').replace('- ', '')
            print("Example from article:\n\t{}".format(sentence_formatted), file=output_file)
            present = True
            break

    if not present:
        print("Word \"{}\" not found in article!".format(word))


def load_pdf_text(file_name):
    """
    Load and extract text from a PDF file.

    Args:
    file_name (str): Path to the PDF file.

    Returns:
    str: Text extracted from the PDF.
    """
    doc = fitz.open(file_name)
    return " ".join([page.get_text() for page in doc])


def interact_with_user(text, sentences, output_file):
    """
    Interactive mode where the user can choose words to process.

    Args:
    text (str): Full text of the PDF.
    sentences (list): List of sentences from the article.
    output_file (file object): File to write the output to.
    """
    words = set(text.replace('\n', ' ').split(' '))
    for raw_word in words:
        word = re.sub('[^a-zA-Z]+', '', raw_word)
        if not word:
            continue

        prompt = "\rDo you want to use the word \"{}\" (y/m - modify and use/n/q - quit): ".format(word)
        print(prompt, end="")
        key = getch.getch()
        if key == 'y':
            process_word(word, sentences, output_file)
        elif key == 'm':
            print("Enter the word you want to look up:")
            word = input()
            process_word(word, sentences, output_file)
        elif key == 'q':
            print("Quitting...")
            break
        print("\r" + " " * len(prompt), end='\r')


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print("USAGE: ./Vocab.py [-i] [-c] ARTICLE_NAME.pdf [-o OUTPUT_FILE] WORD_1 WORD_2 WORD_3...")
        print("\t-i is interactive mode")
        print("\t-c counts the number of definitions present in file. Useful when running the script several times")
        sys.exit(1)

    interactive = '-i' in sys.argv
    count_definitions = '-c' in sys.argv
    output_index = next((i for i, arg in enumerate(sys.argv) if arg == '-o'), None)
    output_file = None
    file_name = sys.argv[1]

    if output_index is not None:
        if len(sys.argv) < output_index + 2:
            print("ERROR: Output file should be specified after the -o flag")
            sys.exit(-1)
        output_file = open(sys.argv[output_index + 1], "a+")
        if count_definitions:
            output_file.seek(0)
            previous_text = output_file.read()
            print("Number of defined words: ", previous_text.count("Definition"))

    text = load_pdf_text(file_name)
    sentences = text.split('.')

    if interactive:
        interact_with_user(text, sentences, output_file)
    else:
        words = sys.argv[2:]
        for word in words:
            process_word(word, sentences, output_file)

    if output_file:
        output_file.close()
