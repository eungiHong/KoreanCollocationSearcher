import fnmatch
import operator
import os
import re

import Tools

'''
KoreanCollocationSearcher

    # 연어 추출
    find_collocation_at_once_with_examples
    find_collocation_with_variable_window_at_once
    get_pos_statistics
    collect_examples_at_once_different_allocation // deprecated
    collect_examples_at_once // deprecated
    collect_examples // deprecated
    
    # 연어 추출 보조
    find_duplication
    build_tag_dictionary
    find_tagging_error
    
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

    def __init__(self, corpus_directory_path, write_path):
        self.corpus_directory_path = corpus_directory_path
        self.write_path = write_path

        self.bibl = ".*<bibl>$"
        self.title = "^\t\t\t\t<title>.*"
        self.sentence_marker = "^B"
        # 태그 정보 - <head>: 제목, <p>: 본문, <l>: 시
        # author를 추가한 이유 - 기자/NNG + 짧/VA + 은/ETM + 소식/NNG
        self.end_of_sentence_marker = "^</head>$|^</p>$|^</l>$|^</author>$"

        self.tag_dict = dict()

    # 가변 윈도우로 한 번에 collocation 추출 및 examples 추출
    # word_list_path: 추출하고자 하는 품사의 출현빈도 파일 (POS_출현빈도.txt)
    # example_path: 각 단어의 연어에 대한 예시를 담을 폴더
    # pos_setting: 추출하고자 하는 품사
    # freq_setting: 설정 빈도수 이상으로만 추출
    # tag_conversion: 태그 변환 여부 (NNG -> 명사) 설정, tag_conversion == 1이면 변환
    # self.corpus_directory_path: preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)
    # self.write_path: results/POS (빈도수 n 이상)
    def find_collocation_at_once_with_examples(self, word_list_path, example_path, pos_setting, freq_setting, tag_conversion):

        every_sentence = []
        reserved_for_left = []
        reserved_for_right = []

        if pos_setting == "NNG":
            # NNG 추출용: 동사, 형용사, 보조 동사, 동사 파생 접미사, 긍정 지정사, 부정 지정사
            # todo: VCP, VCN을 exclude에 넣는 게 나으려나? 날.txt 참조 // 아니면 VCN 말고 VCP만 // 지금.txt 참조
            pos_criteria_include = ["VV", "VA", "VX", "XSV", "VCP", "VCN"]  # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            right_pos_criteria_exclude = ["SS"]

        elif pos_setting == "VV" or pos_setting == "VA":
            # VV, VA 추출용: 일반 명사, 고유 명사, 의존 명사
            # pos_criteria_include = ["NNG", "NNP", "NNB"] # 세종용
            pos_criteria_include = ["NNG", "NNP", "NNB", "NNM"]  # 꼬꼬마용 # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            # EF(종결어미)도 추가? ~ㄴ다, ~다 없앨 수 있으나, '가자'에 '자' 날아감
            # todo: SW도 추가해야 할 듯
            # right_pos_criteria_exclude = ["SS", "SF", "EP", "EF"] # 세종용
            right_pos_criteria_exclude = ["SS", "SF", "EPH", "EPT", "EPP", "EFN", "EFQ", "EFO", "EFA", "EFI", "EFR"] # 꼬꼬마용

        else:
            pos_criteria_include = None
            left_pos_criteria_exclude = None
            right_pos_criteria_exclude = None

        # 전처리된 모든 코퍼스를 읽어서 every_sentence 리스트에 담기
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                every_sentence.append(line_list)

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
            col_hash = dict()
            for each_file in every_sentence:
                title = "ITDaily"
                for line_number, line in enumerate(each_file):
                    # if line_number == 0:
                    #    title = line
                    # else:
                    raw = line.split("\t")[0]
                    analyzed = line.split("\t")[1]
                    morphemes = analyzed.split(" ")
                    for index, morpheme in enumerate(morphemes):
                        if flag == 1:
                            flag = 0
                            break
                        if morpheme == pair:

                            # 형태소 기준 왼쪽 윈도우 탐색
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

                            # 형태소 기준 오른쪽 윈도우 탐색
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

                            # 태그 변환  ex) NNG -> 명사
                            if tag_conversion == 1:
                                self.build_tag_dictionary()
                                for idx, value in enumerate(reserved_for_left):
                                    tag = get_pos(value)
                                    try:
                                        tag = self.tag_dict[tag]
                                        reserved_for_left[idx] = get_morph(value) + "/" + tag
                                    except KeyError:
                                        print(value + "\n---")

                                for idx, value in enumerate(reserved_for_right):
                                    tag = get_pos(value)
                                    try:
                                        tag = self.tag_dict[tag]
                                        reserved_for_right[idx] = get_morph(value) + "/" + tag
                                    except KeyError:
                                        print(value + "\n---")

                                tag = get_pos(morpheme)
                                tag = self.tag_dict[tag]
                                morpheme = get_morph(morpheme) + "/" + tag

                            # 스트링 만들기  ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                            if len(reserved_for_left) > 0 or len(reserved_for_right) > 0:
                                var_gram = ""  # variable-gram, derived from bi-gram or tri-gram
                                for morph in reversed(reserved_for_left):
                                    var_gram += morph + " + "  # ex) 꿀/NNG +
                                if len(reserved_for_right) == 0:
                                    var_gram += morpheme  # ex) 꿀/NNG + 먹/VV
                                else:
                                    var_gram += morpheme + " + "  # ex) 꿀/NNG + 먹/VV +
                                for idx, morph in enumerate(reserved_for_right):
                                    if idx == len(reserved_for_right) - 1:
                                        var_gram += morph  # ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                                    else:
                                        var_gram += morph + " + "  # ex) 꿀/NNG + 먹/VV + 은/ETM +

                                if var_gram in col_hash:
                                    # key: 스트링 유형의 var_gram = 특정 연어
                                    # value: 리스트 유형 [빈도수, 원문1, 원문2, 원문3...]
                                    col_hash.get(var_gram)[0] += 1
                                    col_hash.get(var_gram).append(raw + " <출처: " + title + ">")
                                else:
                                    col_hash[var_gram] = [1, raw + " <출처: " + title + ">"]

                            reserved_for_left.clear()
                            reserved_for_right.clear()

            # 빈도 수가 높은 순서로 정렬
            sorted_hash = sorted(col_hash.items(), key=operator.itemgetter(1))

            # 특정 형태소에 대하여 추출된 연어 쓰기
            if pos_setting == "VV" or pos_setting == "VA":
                word = word + "다"

            col_writing_file = open(self.write_path + "/" + word + ".txt", "w", encoding="utf-8")

            example_dir = example_path + "/" + word
            if os.path.isdir(example_dir) is False:
                os.mkdir(example_dir)

            flag = 0
            for idx, collocation in enumerate(reversed(sorted_hash)):

                if collocation[1][0] == 1:  # 빈도수 1인 경우 쓰지 않음
                    break
                if idx >= 100:
                    flag = 1

                col_writing_file.write(str(collocation[0]) + "\t" + str(collocation[1][0]) + "\n")

                if flag == 0:
                    example_writing_file = open(example_dir + "/" + str(idx + 1) + ".txt", "w", encoding="utf-8")
                    for i, example in enumerate(collocation[1]):  # collocation[1] = [frequency, example1, example2...]
                        if i == 0:
                            continue  # collocation[1]이 빈도수이기 때문
                        else:
                            example_writing_file.write(example + "\n")
                    example_writing_file.close()

            col_writing_file.close()

    # 가변 윈도우로 한 번에 collocation 추출
    # word_list_path: 추출하고자 하는 품사의 출현빈도 파일 (POS_출현빈도.txt)
    # pos_setting: 추출하고자 하는 품사
    # freq_setting: 설정 빈도수 이상으로만 추출
    # tag_conversion: 태그 변환 여부 (NNG -> 명사) 설정, tag_conversion == 1이면 변환
    # self.corpus_directory_path: preprocessed/현대문어_형태분석_전처리(형태소만 추출)
    # self.write_path: results/POS (빈도수 n 이상)
    def find_collocation_with_variable_window_at_once(self, word_list_path, pos_setting, freq_setting, tag_conversion):

        col_hash = dict()
        every_sentence = []
        reserved_for_left = []
        reserved_for_right = []
        self.build_tag_dictionary()

        if pos_setting == "NNG":
            # NNG 추출용: 동사, 형용사, 보조 동사, 동사 파생 접미사, 긍정 지정사, 부정 지정사
            # todo: VCP, VCN을 exclude에 넣는 게 나으려나? 날.txt 참조 // 아니면 VCN 말고 VCP만 // 지금.txt 참조
            pos_criteria_include = ["VV", "VA", "VX", "XSV", "VCP", "VCN"]  # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            right_pos_criteria_exclude = ["SS"]

        elif pos_setting == "VV" or pos_setting == "VA":
            # VV, VA 추출용: 일반 명사, 고유 명사, 의존 명사
            pos_criteria_include = ["NNG", "NNP", "NNB"]  # 해당 품사를 스트링에 추가한 후 윈도우 탐색 정지
            left_pos_criteria_exclude = ["SS"]  # 해당 품사를 스트링에 추가하지 않고 윈도우 탐색 정지
            # EF(종결어미)도 추가? ~ㄴ다, ~다 없앨 수 있으나, '가자'에 '자' 날아감
            # todo: SW도 추가해야 할 듯
            right_pos_criteria_exclude = ["SS", "SF", "EP", "EF"]

        else:
            pos_criteria_include = None
            left_pos_criteria_exclude = None
            right_pos_criteria_exclude = None

        # 전처리된 모든 코퍼스를 읽어서 every_sentence 리스트에 담기
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                every_sentence.append(line_list)

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
            for each_file in every_sentence:
                for line in each_file:
                    morphemes = line.split(" ")
                    for index, morpheme in enumerate(morphemes):
                        if flag == 1:
                            flag = 0
                            break
                        if morpheme == pair:

                            # 형태소 기준 왼쪽 윈도우 탐색
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

                            # 형태소 기준 오른쪽 윈도우 탐색
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

                            # 태그 변환  ex) NNG -> 명사
                            if tag_conversion == 1:
                                for idx, value in enumerate(reserved_for_left):
                                    tag = get_pos(value)
                                    try:
                                        tag = self.tag_dict[tag]
                                        reserved_for_left[idx] = get_morph(value) + "/" + tag
                                    except KeyError:
                                        print(value + "\n---")

                                for idx, value in enumerate(reserved_for_right):
                                    tag = get_pos(value)
                                    try:
                                        tag = self.tag_dict[tag]
                                        reserved_for_right[idx] = get_morph(value) + "/" + tag
                                    except KeyError:
                                        print(value + "\n---")

                                tag = get_pos(morpheme)
                                tag = self.tag_dict[tag]
                                morpheme = get_morph(morpheme) + "/" + tag

                            # 스트링 만들기  ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                            if len(reserved_for_left) > 0 or len(reserved_for_right) > 0:
                                var_gram = ""  # variable-gram, derived from bi-gram or tri-gram
                                for morph in reversed(reserved_for_left):
                                    var_gram += morph + " + "  # ex) 꿀/NNG +
                                if len(reserved_for_right) == 0:
                                    var_gram += morpheme  # ex) 꿀/NNG + 먹/VV
                                else:
                                    var_gram += morpheme + " + "  # ex) 꿀/NNG + 먹/VV +
                                for idx, morph in enumerate(reserved_for_right):
                                    if idx == len(reserved_for_right) - 1:
                                        var_gram += morph  # ex) 꿀/NNG + 먹/VV + 은/ETM + 벙어리/NNG
                                    else:
                                        var_gram += morph + " + "  # ex) 꿀/NNG + 먹/VV + 은/ETM +

                                if var_gram in col_hash:
                                    # todo: col_hash에다 원문 담은 리스트 추가?
                                    col_hash[var_gram] += 1
                                else:
                                    col_hash[var_gram] = 1

                            reserved_for_left.clear()
                            reserved_for_right.clear()

            # 빈도 수가 높은 순서로 정렬
            sorted_hash = sorted(col_hash.items(), key=operator.itemgetter(1))

            if pos_setting == "VV" or pos_setting == "VA":
                w_file = open(self.write_path + "/" + word + "다.txt", "w", encoding="utf-8")
            else:
                w_file = open(self.write_path + "/" + word + ".txt", "w", encoding="utf-8")

            for term in reversed(sorted_hash):
                if term[1] == 1:
                    break
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
                        split_morpheme_and_tag = pair.rsplit("/", 1)

                        try:  # 빈 라인 때문에 삽입
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

    def collect_examples_at_once_different_allocation(self, collocation_path):

        every_sentence = []

        # 모든 문장 준비
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                every_sentence.append(line_list)

        list_of_files = os.listdir(collocation_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                file = open(collocation_path + "/" + entry, "r", encoding="utf-8")
                list_of_collocations = []

                for idx, line in enumerate(file):
                    if idx == 50:
                        break
                    if line.endswith("\n"):
                        line = line.strip("\n")
                    collocation = line.split("\t")[0]
                    list_of_collocations.append(collocation)
                file.close()

                write_dir = self.write_path + "/" + entry.rstrip(".txt")
                if os.path.isdir(write_dir) is True:
                    continue
                os.mkdir(write_dir)

                for idx, collocation in enumerate(list_of_collocations):
                    collocation = Tools.add_backslash(collocation)
                    # r"(.* 악/NNG \+ 을/JKO \+ 쓰/VV|^악/NNG \+ 을/JKO \+ 쓰/VV).*"
                    # 위처럼 안 하면 '악/NNG'에 '음악/NNG'이 걸리는 사례 발생!
                    re_string = r"(.* " + collocation + "|^" + collocation + ").*"

                    try:
                        regex = re.compile(re_string)
                        examples = []

                        for each_file in every_sentence:
                            for line in each_file:
                                line_pair = line.split("\t")
                                raw_text = line_pair[0]
                                analyzed_text = line_pair[1]
                                if regex.match(analyzed_text):
                                    examples.append(raw_text)

                        write_path = write_dir + "/" + str(idx + 1) + ".txt"
                        w_file = open(write_path, "w", encoding="utf-8")

                        for example in examples:
                            w_file.write(example + "\n")
                        w_file.close()

                    except:
                        print(entry + ": " + str(idx + 1))

    def collect_examples_at_once(self, collocation_path):

        examples = []
        every_sentence = []
        list_of_collocations = []

        # 모든 문장 준비
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                every_sentence.append(line_list)

        list_of_files = os.listdir(collocation_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                file = open(collocation_path + "/" + entry, "r", encoding="utf-8")
                for idx, line in enumerate(file):
                    if idx == 50:
                        break
                    if line.endswith("\n"):
                        line = line.strip("\n")
                    collocation = line.split("\t")[0]
                    list_of_collocations.append(collocation)
                file.close()

                write_dir = self.write_path + "/" + entry.rstrip(".txt")
                if os.path.isdir(write_dir) is True:
                    continue
                os.mkdir(write_dir)

                for idx, collocation in enumerate(list_of_collocations):
                    collocation = Tools.add_backslash(collocation)
                    # r"(.* 악/NNG \+ 을/JKO \+ 쓰/VV|^악/NNG \+ 을/JKO \+ 쓰/VV).*"
                    # 위처럼 안 하면 '악/NNG'에 '음악/NNG'이 걸리는 사례 발생!
                    re_string = r"(.* " + collocation + "|^" + collocation + ").*"

                    try:  # 정규표현식 전용 기호 때문에 오류 발생
                        regex = re.compile(re_string)
                        for each_file in every_sentence:
                            for line in each_file:
                                line_pair = line.split("\t")
                                raw_text = line_pair[0]
                                analyzed_text = line_pair[1]
                                if regex.match(analyzed_text):
                                    examples.append(raw_text)

                        write_path = write_dir + "/" + str(idx + 1) + ".txt"
                        w_file = open(write_path, "w", encoding="utf-8")

                        for example in examples:
                            w_file.write(example + "\n")
                        w_file.close()

                    except:
                        print(entry)

                    examples.clear()
                list_of_collocations.clear()

    # 특정 연어가 등장하는 예문 수집
    # self.corpus_directory_path: preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)
    # query_path
    # write_path: data/examples
    def collect_examples(self, query_path):

        examples = []
        every_sentence = []
        list_of_collocations = []

        # 모든 문장 준비
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                every_sentence.append(line_list)

        # 연어 목록 준비
        file = open(query_path, "r", encoding="utf-8")
        for idx, line in enumerate(file):
            if idx == 50:
                break
            if line.endswith("\n"):
                line = line.strip("\n")
            collocation = line.split("\t")[0]
            list_of_collocations.append(collocation)
        file.close()

        for idx, collocation in enumerate(list_of_collocations):
            collocation = Tools.add_backslash(collocation)
            # r"(.* 악/NNG \+ 을/JKO \+ 쓰/VV|^악/NNG \+ 을/JKO \+ 쓰/VV).*"
            # 위처럼 안 하면 '악/NNG'에 '음악/NNG'이 걸리는 사례 발생!
            re_string = r"(.* " + collocation + "|^" + collocation + ").*"
            regex = re.compile(re_string)

            for each_file in every_sentence:
                for line in each_file:
                    line_pair = line.split("\t")
                    raw_text = line_pair[0]
                    analyzed_text = line_pair[1]
                    if regex.match(analyzed_text):
                        examples.append(raw_text)

            write_path = self.write_path + "/" + str(idx) + ".txt"
            w_file = open(write_path, "w", encoding="utf-8")

            for example in examples:
                w_file.write(example + "\n")
            w_file.close()

            examples.clear()

    # 문장이 중복되는 세종 코퍼스 원본 파일 찾기 - 예를 들어, BTJO0443에서는 같은 글이 4번이나 반복됨
    # 입력 파일: 현대문어_형태분석_전처리(원문만 추출)
    # target_sentence: 중복 여부를 알고 있는 문장
    def find_duplication(self, target_sentence):

        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    if line == target_sentence:
                        print(entry)

    # 태그 변환(NNG -> 명사)용 리스트 업
    def build_tag_dictionary(self):

        tag_path = "../data/태그 변환용 파일.txt"
        lines = Tools.get_lines_utf8(tag_path)
        for line in lines:
            tag_pair = line.split("\t")
            self.tag_dict[tag_pair[0]] = tag_pair[1]

    # 세종 코퍼스 태깅 오류 찾기
    # 입력 파일: 현대문어_형태분석_전처리(형태소만 추출)
    def find_tagging_error(self):

        error_list = ["의/JG", "鳥)나", "杖子)를"]
        error_list2 = ["NG", "NNGG", "EEC", "JKSS"]
        list_of_files = os.listdir(self.corpus_directory_path)
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):
                line_list = Tools.get_lines_utf8(self.corpus_directory_path + "/" + entry)
                for line in line_list:
                    morphemes = line.split(" ")
                    for morpheme in morphemes:
                        for element in error_list:
                            if morpheme == element:
                                print(element + " -> " + entry)
                        for element in error_list2:
                            if get_pos(morpheme) == element:
                                print(element + " -> " + entry)

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
        flag = 0

        list_of_files = os.listdir(self.corpus_directory_path)

        for entry in list_of_files:
            if fnmatch.fnmatch(entry, "*.txt"):

                w_file = open(self.write_path + "/" + entry, "w", encoding="utf-8")
                line_list = Tools.get_lines_utf16(self.corpus_directory_path + "/" + entry)
                for line in line_list:

                    # 출처(title) 추출
                    if re.match(self.bibl, line):
                        flag = 1
                    if re.match(self.title, line) and flag == 1:
                        line = line.strip("\t\t\t\t<title>")
                        line = line.strip("</title>")
                        w_file.write(line + "\n")

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
                        w_file.write("\t")

                        for i in range(0, len(whole_sentence_analyzed)):
                            w_file.write(whole_sentence_analyzed[i])
                            if i < len(whole_sentence_analyzed) - 1:
                                w_file.write(" ")
                        w_file.write("\n")

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
        # split_morpheme_and_tag = morpheme.rsplit("/", 1)
        # morph = split_morpheme_and_tag[0]
        morph = morpheme.rsplit("/", 1)[0]
    except IndexError:
        return morph

    return morph


# 형태소/품사 쌍에서 품사만 가져오기
def get_pos(morpheme):
    pos = ""
    try:
        # split_morpheme_and_tag = morpheme.rsplit("/", 1)
        # pos = split_morpheme_and_tag[1]
        pos = morpheme.rsplit("/", 1)[1]
    except IndexError:
        return pos

    return pos


# 리스트에 포함된 항목 중에 쿼리와 일치하는 항목 있는지 알아보기
def find_match(query, item_list):
    for item in item_list:
        if query == item:
            return True
    return False
