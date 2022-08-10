import os
import pandas as pd
import numpy as np
from gensim.models.fasttext import FastText
from .config import *
from .utils import *
from .tokenizer import Khaiii_lemma

pos_list = Filter.POS
stopwords_list = Filter.STOPWORDS
model_path = Path.model_path

tokenizer = Khaiii_lemma(pos_list, stopwords_list)

def keyword_count(token_vectors: np.array, keyword_vectors: np.array) -> int:
    """
    평가 토큰들의 벡터와 키워드 토큰들의 벡터를 비교해 threshold값이 넘어가는 수를 count해서 반환
    :param token_vectors:   평가 토큰의 벡터
    :param keyword_vectors:  키워드 토큰의 벡터
    :return: threshold 이상 count된 수
    """
    list_score = []
    for keyword_vector in keyword_vectors:
        similarity_scores = token_vectors.dot(keyword_vector) / (np.linalg.norm(token_vectors, axis=1) * np.linalg.norm(keyword_vector))
        scores_array = similarity_scores > 0.9
        scores = scores_array.tolist().count(True)
        list_score.append(scores)
    return sum(list_score)
