import fnmatch
import operator
import os
import re

import Tools

'''
KoreanCollocationSearcher

    # 연어 추출
    find_collocation_with_variable_window_at_once
    get_pos_statistics
    
    # 전처리
    pre_process
    pre_process_with_raw_text
    pre_process_only_raw_text
    sejong_to_kkma
    
# Tools    
get_morph
get_pos
find_match
'''


class KoreanCollocationExtractor:

    # corpus_directory_path: preprocessed/현대문어_형태분석_전처리(형태소만 추출)
    # write_path: results/POS (빈도수 n 이상)
    def __init__(self, corpus_directory_path, write_path):
        self.corpus_directory_path = corpus_directory_path
        self.write_path = write_path

        self.sentence_marker = "^B"

        # 태그 정보 - <head>: 제목, <p>: 본문, <l>: 시
        # 추가하지 않은 태그: <author>
        self.end_of_sentence_marker = "^</head>$|^</p>$|^</l>$"

    # 가변 윈도우로 한 번에 collocation 추출
    # word_list_path: 추출하고자 하는 품사의 출현빈도 파일 (POS_출현빈도.txt)
    # pos_setting: 추출하고자 하는 품사
    # freq_setting: 설정 빈도수 이상으로만 추출
    def find_collocation_with_variable_window_at_once(self, word_list_path, pos_setting, freq_setting):

        print("The process is ongoing...")
        col_hash = dict()
        reserved_for_left = []
        reserved_for_right = []

        if pos_setting == "NNG":
            # NNG 추출용: 동사, 형용사, 보조 동사, 동사 파생 접미사, 긍정 지정사, 부정 지정사
            pos_criteria_include = ["VV", "VA", "VX", "XSV", "VCP", "VCN"]  # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            right_pos_criteria_exclude = ["SS"]

        elif pos_setting == "VV" or pos_setting == "VA":
            # VV, VA 추출용: 일반 명사, 고유 명사, 의존 명사
            pos_criteria_include = ["NNG", "NNP", "NNB"]  # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            right_pos_criteria_exclude = ["SS", "SF", "EP", "EF"]  # todo: EF(종결어미)도 추가? ~ㄴ다, ~다 없앨 수 있으나, '가자'에 '자' 날아감

        else:
            pos_criteria_include = None
            left_pos_criteria_exclude = None
            right_pos_criteria_exclude = None

        list_of_files = os.listdir(self.corpus_directory_path)

        word_list = Tools.get_lines_utf8(word_list_path)
        for item in word_list:
            word_and_frequency = item.split("\t")
            word = word_and_frequency[0]
            frequency = word_and_frequency[1]
            pair = word + "/" + pos_setting  # 형태소/품사 pair
            if int(frequency) < freq_setting:
                break

            # 각각의 형태소마다 전처리된 코퍼스 전체를 순회하면서 해당 형태소가 등장하는 문맥 추출
            flag = 0
            for entry in list_of_files:
                if fnmatch.fnmatch(entry, "*.txt"):
                    line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                    for line in line_list:
                        morphemes = line.split(" ")
                        for index, morpheme in enumerate(morphemes):
                            if flag == 1:
                                flag = 0
                                break
                            if morpheme == pair:
                                # 단어 기준 왼쪽 윈도우 탐색
                                mover = index - 1
                                while mover >= 0:
                                    pre_morpheme_pos = get_pos(morphemes[mover])
                                    if find_match(pre_morpheme_pos, left_pos_criteria_exclude) is True:
                                        break
                                    if find_match(pre_morpheme_pos, pos_criteria_include) is False:
                                        reserved_for_left.append(morphemes[mover])

                                        # 한 문장에 목표 단어가 2회 이상 등장하는 경우, 빈도수가 중복으로 쌓이는 것을 방지하기 위함
                                        # ex) 는/JX + 국민/NNG + 주권/NNG + ·/SP + 국민/NNG + 경제/NNG + ·/SP + 국민/NNG.. 3
                                        if get_morph(pair) == get_morph(morphemes[mover]):
                                            flag = 1
                                    else:
                                        reserved_for_left.append(morphemes[mover])
                                        break
                                    mover -= 1

                                # 단어 기준 오른쪽 윈도우 탐색
                                mover = index + 1
                                while mover <= len(morphemes) - 1:
                                    post_morpheme_pos = get_pos(morphemes[mover])
                                    if find_match(post_morpheme_pos, right_pos_criteria_exclude) is True:
                                        break
                                    if find_match(post_morpheme_pos, pos_criteria_include) is False:
                                        reserved_for_right.append(morphemes[mover])

                                        # 한 문장에 목표 단어가 2회 이상 등장하는 경우, 빈도수가 중복으로 쌓이는 것을 방지하기 위함
                                        # ex) 는/JX + 국민/NNG + 주권/NNG + ·/SP + 국민/NNG + 경제/NNG + ·/SP + 국민/NNG.. 3
                                        if get_morph(pair) == get_morph(morphemes[mover]):
                                            flag = 1
                                    else:
                                        reserved_for_right.append(morphemes[mover])
                                        break
                                    mover += 1

                                # 스트링 만들기  ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                                if len(reserved_for_left) > 0 or len(reserved_for_right) > 0:
                                    var_gram = ""  # variable-gram, derived from bi-gram or tri-gram
                                    for morph in reversed(reserved_for_left):
                                        var_gram += morph + " + "  # ex) 꿀/NNG +
                                    if len(reserved_for_right) == 0:
                                        var_gram += pair  # ex) 꿀/NNG + 먹/VV
                                    else:
                                        var_gram += pair + " + "  # ex) 꿀/NNG + 먹/VV +
                                    for idx, morph in enumerate(reserved_for_right):
                                        if idx == len(reserved_for_right) - 1:
                                            var_gram += morph  # ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                                        else:
                                            var_gram += morph + " + "  # ex) 꿀/NNG + 먹/VV + 은/ETM +

                                    if var_gram in col_hash:
                                        col_hash[var_gram] += 1
                                    else:
                                        col_hash[var_gram] = 1

                                reserved_for_left.clear()
                                reserved_for_right.clear()

            # 빈도 수 기준으로 소팅
            sorted_hash = sorted(col_hash.items(), key=operator.itemgetter(1))

            if pos_setting == "VV" or pos_setting == "VA":
                w_file = open(self.write_path + "/" + word + "다.txt", "w", encoding="utf-8")
            else:
                w_file = open(self.write_path + "/" + word + ".txt", "w", encoding="utf-8")

            for term in reversed(sorted_hash):
                w_file.write(str(term[0]) + "\t" + str(term[1]) + "\n")

            w_file.close()
            col_hash.clear()

    # 입력 파일: preprocessed/현대문어_형태분석_전처리(형태소만 추출) / 출력 파일: sejong_statistics/POS_출현빈도.txt
    def get_pos_statistics(self, pos):

        morpheme_hash = dict()
        count = 0
        w_file = open(self.write_path, "w", encoding="utf-8")
        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    morphemes = line.split(" ")
                    for index, pair in enumerate(morphemes):
                        split_morpheme_and_tag = pair.split("/")

                        try:  # 빈 라인, 코퍼스 자체 오류 (예: /SF) 때문에 삽입
                            if split_morpheme_and_tag[1] == pos:
                                count += 1
                                morpheme = split_morpheme_and_tag[0]
                                if morpheme in morpheme_hash:
                                    morpheme_hash[morpheme] += 1
                                else:
                                    morpheme_hash[morpheme] = 1
                        except IndexError:
                            continue

        sorted_hash = sorted(morpheme_hash.items(), key=operator.itemgetter(1))
        for term in reversed(sorted_hash):
            w_file.write(str(term[0]) + "\t" + str(term[1]) + "\n")
        w_file.close()

    # 입력 파일: raw_data/세종_현대문어_형태분석_말뭉치 / 출력 파일: preprocessed/현대문어_형태분석_전처리(형태소만 추출)
    def pre_process(self):

        whole_sentence_analyzed = []

        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):

                w_file = open(self.write_path + "/" + entry, "w", encoding="utf-8")
                line_list = Tools.get_lines_utf16(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    if re.match(self.sentence_marker, line):  # 세종 말뭉치의 특성상, 모든 문장 라인은 B로 시작함
                        elements = line.split()  # [0]은 식별번호, [1]은 어절, [2] 이하는 형태소 분석 결과 및 '+' 기호

                        for i in range(2, len(elements)):
                            if elements[i] != "+":
                                whole_sentence_analyzed.append(elements[i])  # 추출한 형태소 분석을 list에 모아 놓음

                    elif re.match(self.end_of_sentence_marker, line):

                        for i in range(0, len(whole_sentence_analyzed)):
                            w_file.write(whole_sentence_analyzed[i])
                            if i < len(whole_sentence_analyzed) - 1:
                                w_file.write(" ")
                        w_file.write("\n")

                        whole_sentence_analyzed.clear()  # 형태소 분석 정보용 리스트 초기화

                w_file.close()

    # pre_process는 형태소만 추출하지만, 이건 원문도 함께 추출
    # 입력 파일: raw_data/세종_현대문어_형태분석_말뭉치 / 출력 파일: preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)
    def pre_process_with_raw_text(self):

        whole_sentence_raw = []
        whole_sentence_analyzed = []

        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):

                w_file = open(self.write_path + "/" + entry, "w", encoding="utf-8")
                line_list = Tools.get_lines_utf16(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    if re.match(self.sentence_marker, line):  # 세종 말뭉치의 특성상, 모든 문장 라인은 B로 시작함
                        elements = line.split()  # [0]은 식별번호, [1]은 어절, [2] 이하는 형태소 분석 결과 및 '+' 기호

                        whole_sentence_raw.append(elements[1])  # 원문을 list에 모아 놓음

                        for i in range(2, len(elements)):
                            if elements[i] != "+":
                                whole_sentence_analyzed.append(elements[i])  # 추출한 형태소 분석을 list에 모아 놓음

                    elif re.match(self.end_of_sentence_marker, line):

                        for i in range(0, len(whole_sentence_raw)):
                            w_file.write(whole_sentence_raw[i])
                            if i < len(whole_sentence_raw) - 1:
                                w_file.write(" ")
                        w_file.write("\n")

                        for i in range(0, len(whole_sentence_analyzed)):
                            w_file.write(whole_sentence_analyzed[i])
                            if i < len(whole_sentence_analyzed) - 1:
                                w_file.write(" ")
                        w_file.write("\n\n")

                        whole_sentence_raw.clear()
                        whole_sentence_analyzed.clear()  # 형태소 분석 정보용 리스트 초기화

                w_file.close()

    # 형태소 빼고 원문만 추출
    # 입력 파일: raw_data/세종_현대문어_형태분석_말뭉치 / 출력 파일: preprocessed/현대문어_형태분석_전처리(원문만 추출)
    def pre_process_only_raw_text(self):

        whole_sentence_raw = []

        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):

                w_file = open(self.write_path + "/" + entry, "w", encoding="utf-8")
                line_list = Tools.get_lines_utf16(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    if re.match(self.sentence_marker, line):  # 세종 말뭉치의 특성상, 모든 문장 라인은 B로 시작함
                        elements = line.split()  # [0]은 식별번호, [1]은 어절, [2] 이하는 형태소 분석 결과 및 '+' 기호

                        whole_sentence_raw.append(elements[1])  # 원문을 list에 모아 놓음

                    elif re.match(self.end_of_sentence_marker, line):

                        for i in range(0, len(whole_sentence_raw)):
                            w_file.write(whole_sentence_raw[i])
                            if i < len(whole_sentence_raw) - 1:
                                w_file.write(" ")
                        w_file.write("\n")

                        whole_sentence_raw.clear()

                w_file.close()

    # 전처리된 세종 코퍼스 원문을 kkma로 분석하여 출력
    # 입력 파일: preprocessed/현대문어_형태분석_전처리(원문만 추출) / 출력 파일: preprocessed/현대문어_형태분석_전처리(형태소만 추출_꼬꼬마)
    def sejong_to_kkma(self):

        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                read_path = self.corpus_directory_path + "/" + entry
                write_path = self.write_path + "/" + entry
                Tools.kkma_analysis_print_like_sejong_corpus(read_path, write_path)


# 형태소/품사 쌍에서 형태소만 가져오기
def get_morph(morpheme):
    morph = ""
    try:
        split_morpheme_and_tag = morpheme.split("/")
        morph = split_morpheme_and_tag[0]
    except IndexError:
        return morph

    return morph


# 형태소/품사 쌍에서 품사만 가져오기
def get_pos(morpheme):
    pos = ""
    try:
        split_morpheme_and_tag = morpheme.split("/")
        pos = split_morpheme_and_tag[1]
    except IndexError:
        return pos

    return pos


# 리스트에 포함된 항목 중에 쿼리와 일치하는 항목 있는지 알아보기
def find_match(query, item_list):
    for item in item_list:
        if query == item:
            return True
    return False
