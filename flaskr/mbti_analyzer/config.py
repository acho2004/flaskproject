import os

class Filter:

    POS = ['NNG', 'NNB', 'NNP', 'SL', 'VV', 'VA', 'XSA', 'XR', 'MAG', 'XPN']
    STOPWORDS = ['이다', '대로', '만큼', '너무', '시다', '있다', '하다', '위하다', '되다', '같다', '없다', '르다', '많다', '드리다', '점', '아직', '지금', '대하다', '특별히']
    CAP = ['I', 'E', 'N', 'S', 'F', 'T', 'P', 'J']

class Path:

    model_path = os.path.join(os.path.abspath(''),'model/final_model')
    keyword_path = os.path.join(os.path.abspath(''), 'mbti_keyword.json')
    grade_path = os.path.join(os.path.abspath(''), 'grade.json')
    output_path = os.path.join(os.path.abspath(''), 'output')