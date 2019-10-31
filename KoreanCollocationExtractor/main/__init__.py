import timeit
import KoreanCollocationExtractor as Kcs

start = timeit.default_timer()

corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(형태소만 추출)"
write_path = "../data/results/NNG (빈도수 8000 이상)_test"

pos = "NNG"
word_statistics = "../data/sejong_statistics/" + pos + "_출현빈도.txt"

extractor = Kcs.KoreanCollocationExtractor(corpus_path, write_path)
extractor.find_collocation_with_variable_window_at_once(word_statistics, pos, 8000)


stop = timeit.default_timer()
print("소요 시간: ", stop - start)