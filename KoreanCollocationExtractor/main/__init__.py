import timeit
import KoreanCollocationExtractor as Kce


start = timeit.default_timer()


corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(형태소만 추출)"
write_path = "../data/results/test_2"

pos = "VV"
word_statistics = "../data/sejong_statistics/" + pos + "_출현빈도.txt"

extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
extractor.find_collocation_with_variable_window_at_once(word_statistics, pos, 5000, 1)

stop = timeit.default_timer()
print("소요 시간: ", stop - start)
