import os
import pandas as pd
from .analyzer import *
from .radar_chart import *
from .utils import *
from .config import *
from .tokenizer import Khaiii_lemma


pos_list = Filter.POS # 사용할 품사
stopwords_list = Filter.STOPWORDS # 불용어 처리
keyword_path = Path.keyword_path # 세부 키워드
keyword_path = keyword_path.replace("/mbti_keyword.json", "/mbti_analyzer/mbti_keyword.json")
grade_path = Path.grade_path
grade_path = grade_path.replace("/grade.json", "/mbti_analyzer/grade.json")
output_path = Path.output_path
output_path = output_path.replace("/output", "/static/output")

tokenizer = Khaiii_lemma(pos_list, stopwords_list) # 토크나이저 생성
keyword_dict = read_json(keyword_path)
grade_dict = read_json(grade_path)
I_vectors, E_vectors, N_vectors, S_vectors, F_vectors, T_vectors, P_vectors, J_vectors = load_key_vector(keyword_dict) # 세부 키워드 벡터 반환

def main(feedback, employee_num):

    user_name = ""
    sentence = feedback
    token_list = tokenizer.khaiii_tokenizer(sentence)
    scale_value = len(sentence.splitlines()) / 2
    token_vectors = token_to_vector(token_list)

    I_score = keyword_count(token_vectors, I_vectors) / scale_value
    E_score = keyword_count(token_vectors, E_vectors) / scale_value
    N_score = keyword_count(token_vectors, N_vectors) / scale_value
    S_score = keyword_count(token_vectors, S_vectors) / scale_value
    F_score = keyword_count(token_vectors, F_vectors) / scale_value
    T_score = keyword_count(token_vectors, T_vectors) / scale_value
    P_score = keyword_count(token_vectors, P_vectors) / scale_value
    J_score = keyword_count(token_vectors, J_vectors) / scale_value

    tmp = [user_name, I_score, E_score, N_score, S_score, F_score, T_score, P_score, J_score]

    mapping_df = pd.DataFrame(columns=['ID', 'I', 'E', 'N', 'S', 'F', 'T', 'P', 'J'])
    mapping_df.loc[0] = tmp
    result = standardization(mapping_df, grade_dict)
    get_radarchart_one(result.iloc[0], employee_num, output_path)
    result_dict = result.iloc[0][1:].to_dict()

    return result_dict
