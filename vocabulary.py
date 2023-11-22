import argparse
import re
import fitz  # pip install PyMuPDF
import requests
from bs4 import BeautifulSoup


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
    result = fetch_definition(word.strip().capitalize())
    if not result:
        print("Word {} not found in the dictionary!".format(word.strip().capitalize()))
        return

    definition, example = result
    print("\n\"{}\":\nDefinition:\n\t{}\nDictionary example:\n\t{}".format(word.strip().capitalize(), definition,
                                                                           example), file=output_file)

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
    (Modified to use input() instead of getch.getch())
    """
    words = set(text.replace('\n', ' ').split(' '))
    for raw_word in words:
        word = re.sub('[^a-zA-Z]+', '', raw_word)
        if not word:
            continue

        prompt = "Do you want to use the word \"{}\" (y/m - use/modify, r - next word, n/q - quit): ".format(word.strip().capitalize())
        print(prompt, end="")
        key = input("Choose option: ")[0].lower()  # Get the first character of input
        if key == 'y':
            process_word(word, sentences, output_file)
        elif key == 'm':
            word = input("Enter the word you want to look up: ")
            process_word(word, sentences, output_file)
        elif key == 'r':
            continue
        elif key == 'q' or key == 'n':
            print("Quitting...")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process words from a PDF file.')
    parser.add_argument('file', help='PDF file to process')
    parser.add_argument('-o', '--output', default='output.txt', help='Output file name (default: output.txt)')

    args = parser.parse_args()

    output_file = open(args.output, "a+", encoding='utf-8')
    text = load_pdf_text(args.file)
    sentences = text.split('.')
    interact_with_user(text, sentences, output_file)
    output_file.seek(0)
    previous_text = output_file.read()
    print("Number of defined words: ", previous_text.count("Definition"))

    output_file.close()
