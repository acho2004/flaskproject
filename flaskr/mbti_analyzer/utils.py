import json
import bisect
from collections import Counter
import pandas as pd
import numpy as np
from gensim.models.fasttext import FastText
from .config import *


model_path = Path.model_path
model_path = model_path.replace("/model/final_model", "/mbti_analyzer/model/final_model")
fastext_model = FastText.load(model_path)

def read_json(file_name):
    with open(file_name, 'r', encoding='UTF8') as fp:
        json_data = json.load(fp) 
    return json_data

def token_to_vector(tokens: list) -> np.array:
    """
    단어 토큰 리스트를 입력으로 받아 사전 훈련된 fasttext를 사용해 벡터로 변환된 numpy array를 반환
    :param tokens: 단어 토큰 시퀀스
    :return: 벡터로 변환된 numpy array
    """
    wv_list = []
    for token in tokens:
        wv_list.append(fastext_model.wv[token])

    return np.array(wv_list)


def standardization(data_df: pd.DataFrame, grade_dict: dict) -> pd.DataFrame:
    """
    등급으로 변환 시키는 함수를 적용, dict 형태로 입력을 받고 리스트로 반환
    :param df:  등급으로 변환 시킬 DataFrame
    :return: 변환된 DataFrame을 반환
    """
    df = data_df
    for key, value in grade_dict.items():
        score_list = value
        df[key[0]] = df[key[0]].apply(lambda x: determine_grade(x, score_list)) # 앞글자

    return df

def load_key_vector(json_dict: dict):
    """
    각 키워드의 세부 키워드 벡터를 반환하는 함수
    :param json_path: 증강된 세부 키워드가 있는 파일 경로
    :return: 세부 키워드들의 벡터
    """

    keyword_dict = json_dict

    I_cap = keyword_dict['I']
    E_cap = keyword_dict['E']
    N_cap = keyword_dict['N']
    S_cap = keyword_dict['S']
    F_cap = keyword_dict['F']
    T_cap = keyword_dict['T']
    P_cap = keyword_dict['P']
    J_cap = keyword_dict['J']

    I_vectors = token_to_vector(I_cap)
    E_vectors = token_to_vector(E_cap)
    N_vectors = token_to_vector(N_cap)
    S_vectors = token_to_vector(S_cap)
    F_vectors = token_to_vector(F_cap)
    T_vectors = token_to_vector(T_cap)
    P_vectors = token_to_vector(P_cap)
    J_vectors = token_to_vector(J_cap)


    return I_vectors, E_vectors, N_vectors, S_vectors, F_vectors, T_vectors, P_vectors, J_vectors


def determine_grade(scores: int, breakpoints: list, grades: list = [0, 1, 2, 3, 4, 5]) -> int:
    """
    점수가 들어오면 변환된 등급을 반환해주는 함수
    :param scores: 변환 될 점수
    :param breakpoints: 변환 될 기준 등급 리스트
    :param grades: 변환 될 리스트
    :return: 등급으로 변환된 점
    """
    i = bisect.bisect(breakpoints, scores)
    return int(grades[i])