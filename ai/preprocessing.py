import string
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


def parse_out_text(text):
    translator = text.maketrans('', '', string.punctuation)
    text_string = text.translate(translator)

    text_string = " ".join(text_string.split())

    text_array = text_string.split(' ')
    stemmed_array = []
    stemmer = SnowballStemmer('english', ignore_stopwords=True)

    for word in text_array:
        stemmed_array.append(stemmer.stem(word))

    # remove stopwords
    stop_words = set(stopwords.words('english'))
    stemmed_array = [word for word in stemmed_array if word not in stop_words]

    return (' '.join(stemmed_array)).strip()


def remove_digits(text):
    translator = text.maketrans('', '', string.digits)
    text_string = text.translate(translator)

    return text_string


def preprocess(utterance):
    # removing numbers
    utterance = remove_digits(utterance)

    # removing punctuation and stemming
    parsed_utterance = parse_out_text(utterance)

    return parsed_utterance
