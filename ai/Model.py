import pickle
from typing import Dict

from ai.preprocessing import preprocess
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences


class Model:

    def __init__(self):
        self.model = load_model('ai/model.h5')

        with open('ai/tokenizer.pickle', 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def predict(self, utterance):

        preprocessed_utterance = preprocess(utterance)
        transformed_utterance = self.tokenizer.texts_to_sequences([preprocessed_utterance])
        transformed_utterance = pad_sequences(transformed_utterance, padding='post', maxlen=200)

        result = self.model.predict(transformed_utterance)

        return result[0]

    @staticmethod
    def get_emotion(percentages):
        emotion_codes: Dict[str, str] = {
            'neutral': '0',
            'joyful': '1',
            'peaceful': '2',
            'powerful': '3',
            'scared': '4',
            'mad': '5',
            'sad': '6'
        }
        percentages = list(percentages)

        emotion_index = percentages.index(max(percentages))

        for emotion, idx in emotion_codes.items():
            if int(idx) == emotion_index:
                return emotion
