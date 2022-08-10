import pandas as pd
from khaiii import KhaiiiApi

class Khaiii_lemma():
    def __init__(self, filter_pos, stopwords):
        self.filter_pos = filter_pos
        self.stopwords = stopwords
        self.khaiii = KhaiiiApi()

    def filtering_noise(self, words, tag):
        """
        토큰화 진행시 노이즈 단어를 제거하기 위한 함수
        :param words: 검사할 단어
        :return: 검사 결과
        """
        first_char = words[0]
        word_len = len(words)
        repeat_count = 0
        for loop in range(word_len):  # 같은 글자가 반복되는 noise를 제거하기 위해
            if (words[loop] == first_char):
                repeat_count = repeat_count + 1
            else:
                repeat_count = 0
        if len(words) == 1:  # 단 한 글자로 이루어진 단어를 제거
            if tag == 'XPN':  # 단 체언 접두사는 제외
                return True
            else:
                return False
        if len(words) == 0:
            return False
        elif (repeat_count > 3):
            return False
        else:
            return True

    def filter_one_char(self, target_list: list) -> list:
        """
        한글자 단어를 제거하기 위한 함수
        :param target_list:
        :return:
        """
        return_list = []
        for word in target_list:
            if len(word) != 1:
                return_list.append(word)
            else:
                continue
        return return_list

    def filter_noun(self, prev_tag: str, pres_tag: str) -> bool:  # 복합 명사 처리를 위한 부분
        """
        명사가 연속되는것을 확인하기 위한 함수
        :param prev_tag: 이전 품사의 종류
        :param pres_tag: 현재 품사의 종류
        :return:
        """

        if prev_tag == 'NNG' and pres_tag == 'NNG':
            return True

        elif prev_tag == 'NNG' and pres_tag == 'NNB':
            return True

    def filter_predicate(self, tag: str) -> bool:  # 용언에 대한 필터링 부분
        """
        동사와 형용사를 찾는 함수
        :param tag: 판별 대상 품사
        :return:
        """
        if tag in ['VV', 'VA']:
            return True
        else:
            return False

    def filter_xpn(self, pres_tag):  # 체언 접두사를 위한 부분
        if pres_tag == 'NNG':
            return True
        else:
            return False

    def filter_xsa(self, pres_tag):  # 형용사 파생접미사에 대한 처리
        if pres_tag == 'XSA':
            return True
        else:
            return False

    # 우직하지만	우/XR + 직/MAG + 하/XSA + 지만/EC
    def khaiii_tokenizer(self, sent):
        """
        khaiii기반 표제어 추출기입니다.
        :param sent: 추출 대상 문
        :return:
        """
        analyzed = self.khaiii.analyze(sent)
        result_token_list = []
        for eojeol in analyzed:
            try:
                pos_list = ['empty']
                lex_list = ['empty']
                for morph in eojeol.morphs:
                    if morph.tag in self.filter_pos:
                        prev_tag = pos_list[-1]  # 이전 품사 정보
                        prev_lex = lex_list[-1]  # 이전 형태소 정보
                        pres_tag = morph.tag  # 현재 품사 정보
                        pres_lex = morph.lex  # 현재 형태소 정보

                        lex_list.append(pres_lex)  # 형태소 리스트에 추가
                        pos_list.append(pres_tag)  # 품사 리스트에 추가

                        if self.filter_noun(prev_tag, pres_tag):  # 복합명사 부분
                            word = prev_lex + pres_lex  # 명사 두 가지가 하나의 어절에서 등장하면 묶음
                            result_token_list.pop()  # 중복을 제거하기 위한 부분
                            result_token_list.append(word)

                        elif self.filter_predicate(pres_tag):  # 규칙활용 용언에 대한 부분
                            word = pres_lex + '다'
                            result_token_list.append(word)

                        elif self.filter_xpn(pres_tag):  # 체언 접두사 처리
                            if prev_tag == 'XPN':  # 체언 접두사가 등장한다면
                                word = prev_lex + pres_lex  # 체언 접두사 + 체언
                                result_token_list.pop()
                                result_token_list.append(word)
                            else:
                                word = pres_lex
                                result_token_list.append(word)

                        elif self.filter_xsa(pres_tag):  # 형용사 파생접미사에 대한 처리
                            if prev_tag == 'NNG':  # 만약 이전 품사에 명사가 등장했다면
                                if pos_list[1] == 'XPN':  # 그리고 어절의 첫 품사가 xpn이라면
                                    word = lex_list[1] + prev_lex + pres_lex + '다'  # 전부 합해줍니다.
                                    result_token_list.pop()
                                    result_token_list.append(word)
                                else:  # 그렇지 않다면
                                    word = prev_lex + pres_lex + '다'  # NNG + XSA + '다'
                                    result_token_list.pop()
                                    result_token_list.append(word)
                            else:  # 이전 픔사가 명사가 아닌 경우
                                word = prev_lex + pres_lex + '다'
                                result_token_list.pop()
                                result_token_list.append(word)


                        else:  # 모든 경우가 아닌 경우 노이즈 처리를 해줍니다.
                            if self.filtering_noise(pres_lex, pres_tag):
                                #                             print(pres_lex,'8')
                                result_token_list.append(pres_lex)
                            else:
                                continue
            except:

                continue

        result_token_list = self.filter_one_char(result_token_list)
        stopwords_removed_sentence = [word for word in result_token_list if not word in self.stopwords]
        return stopwords_removed_sentence