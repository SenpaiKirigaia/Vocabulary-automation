import argparse
import re
import fitz  # PyMuPDF for reading PDF files
import requests
from bs4 import BeautifulSoup


def fetch_definition(word):
    """
    Fetch the definition and example of a word from the Cambridge Dictionary.
    Args:
    word (str): The word to search for.
    Returns:
    tuple: Definition and example sentence of the word, or None if not found.
    """
    # Form the URL for the dictionary page of the word
    url = 'https://dictionary.cambridge.org/dictionary/english/{}'.format(word)
    # Define the user agent for HTTP request header
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    # Perform the HTTP request to fetch the webpage
    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code != 200:
        return None

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")
    # Find the definition and example elements in the HTML
    definition = soup.find("div", {"class": "def ddef_d db"})
    examples = soup.find_all("div", {"class": "examp dexamp"})

    # Check if the definition and examples are found
    if not definition or not examples:
        return None

    # Return the text content of the definition and the first example
    return definition.get_text().strip(), examples[0].get_text().strip()


def process_word(word, sentences, output_file):
    """
    Process a word by fetching its definition and finding an example in the article.
    Args:
    word (str): The word to process.
    sentences (list): List of sentences from the article.
    output_file (file object): File to write the output to.
    """
    # Fetch the definition and example sentence of the word
    result = fetch_definition(word)
    if result:
        definition, example = result
        # Find an example sentence in the article that contains the word
        article_example = next((sentence for sentence in sentences if word.lower() in sentence.lower()), None)
        if article_example:
            # Format and clean the article example sentence
            sentence_formatted = re.sub(r'[\n-]', ' ', article_example).strip() + '.'
            # Write the formatted information to the output file
            output_file.write("\n\"{}\":\nDefinition:\n\t{}\nDictionary example:\n\t{}\nExample from article:\n\t{}\n"
                              .format(word.capitalize(), definition.capitalize(), example.capitalize(), sentence_formatted))
        else:
            print("Word \"{}\" not found in article.".format(word.capitalize()))
    else:
        print("Word {} not found in the dictionary!".format(word.capitalize()))


def load_pdf_text(file_name):
    """
    Load and extract text from a PDF file.
    Args:
    file_name (str): Path to the PDF file.
    Returns:
    str: Text extracted from the PDF file.
    """
    # Open the PDF file
    doc = fitz.open(file_name)
    # Extract and concatenate text from each page
    return " ".join(page.get_text() for page in doc)


def interact_with_user(sentences, output_file):
    """
    Interactive mode where the user can choose words to process.
    Args:
    sentences (list): List of sentences from the article.
    output_file (file object): File to write the output to.
    """
    # Create a set of unique words from the article
    words = set(re.sub('[^a-zA-Z\s]', '', ' '.join(sentences)).split())
    for word in words:
        if len(word) < 3:
            continue  # Skip words shorter than 3 letters

        prompt = "Do you want to use the word \"{}\"? (y - use, m - modify, r -next word, n/q - quit): ".format(
            word.capitalize())
        print(prompt, end="")
        key = input().lower().strip()

        if key == 'y':
            # Process the word if chosen
            process_word(word, sentences, output_file)
        elif key == 'm':
            # Allow user to modify the word
            modified_word = input("Enter the modified word: ")
            process_word(modified_word, sentences, output_file)
        elif key == 'r':
            continue  # Skip to the next word
        elif key in ('n', 'q'):
            # Quit the program
            print("Quitting...")
            break


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Process words from a PDF file.')
    parser.add_argument('file', help='PDF file to process')
    parser.add_argument('-o', '--output', default='output.txt', help='Output file name (default: output.txt)')

    args = parser.parse_args()

    # Open the output file and process the PDF text
    with open(args.output, "a+", encoding='utf-8') as output_file:
        text = load_pdf_text(args.file)
        sentences = [sentence.strip() for sentence in text.split('.') if sentence]
        interact_with_user(sentences, output_file)
        output_file.seek(0)
        # Count and print the number of defined words
        print("Number of defined words: ", output_file.read().count("Definition"))
