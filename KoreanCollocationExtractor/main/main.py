import timeit
import KoreanCollocationExtractor as Kce
import Tools


start = timeit.default_timer()
print("The process is ongoing...")

flag = 3
corpus = "Sejong"

if flag == 1:  # 전처리 - 세종에서 형태소만 추출
    corpus_path = "../data/raw_data/세종_현대문어_형태분석_말뭉치"
    write_path = "../data/preprocessed/현대문어_형태분석_전처리(형태소만 추출)"
    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.pre_process()  # 65s

if flag == 2:  # 전처리 - 세종에서 원문 및 형태소 + 출처 추출
    corpus_path = "../data/raw_data/세종_현대문어_형태분석_말뭉치"
    write_path = "../data/preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)"
    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.pre_process_with_raw_text()  # 97s

elif flag == 3:  # kkma로 형태소만 + 원문/형태소 한꺼번에 추출
    corpus_path = "../data/" + corpus + "/preprocessed/현대문어_형태분석_전처리(원문만 추출)"
    raw_and_tag_directory = "../data/" + corpus + "/preprocessed/원문 및 형태소 추출 (꼬꼬마)"
    tag_only_directory = "../data/" + corpus + "/preprocessed/형태소만 추출 (꼬꼬마)"
    Tools.kkma_analysis_at_once_for_sejong(corpus_path, raw_and_tag_directory, tag_only_directory)

elif flag == 4:  # kkma로 원문 + 형태소 추출
    corpus_path = "../data/ITDaily/raw_data"
    write_path = "../data/ITDaily/preprocessed/원문 및 형태소 추출"
    Tools.kkma_analysis_with_raw_text(corpus_path, write_path)

elif flag == 5:  # 통계 정보 추출
    pos = "VV"
    corpus_path = "../data/ITDaily/preprocessed/형태소만 추출"
    write_path = "../data/ITDaily/statistics/" + pos +"_출현빈도.txt"
    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.get_pos_statistics(pos)

elif flag == 6:  # 예문과 함께 연어 추출
    pos = "NNG"
    word_statistics = "../data/" + corpus + "/statistics/" + pos + "_출현빈도.txt"
    corpus_path = "../data/" + corpus + "/preprocessed/원문 및 형태소 추출"
    write_path = "../data/" + corpus + "/results/" + pos
    example_path = "../data/" + corpus + "/examples/" + pos
    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.find_collocation_at_once_with_examples(word_statistics, example_path, pos, 2500, 0)
    # 동사(1000, 272 items): 1,344초 // 형용사(10, 580 items): 2,781초 // 명사(1500, 634 items): 3,100초

stop = timeit.default_timer()
print("소요 시간: ", stop - start)


