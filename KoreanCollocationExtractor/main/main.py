import timeit
import KoreanCollocationExtractor as Kce
import re

start = timeit.default_timer()
print("The process is ongoing...")

'''
corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(형태소만 추출)"
write_path = "../data/results/test_2"

pos = "VV"
word_statistics = "../data/sejong_statistics/" + pos + "_출현빈도.txt"

extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
extractor.find_collocation_with_variable_window_at_once(word_statistics, pos, 5000, 1)
'''

flag = 2

if flag == 1:
    corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)"
    write_path = "../data/examples/쓰다2"
    query_path = "../data/results/VV (빈도수 5000 이상)/쓰다.txt"

    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.collect_examples(query_path)

elif flag == 2:
    corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(원문 및 형태소 추출)"
    write_path = "../data/examples"
    collocation_path = "../data/results/VV (빈도수 5000 이상)"

    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    # extractor.collect_examples_at_once(collocation_path)
    extractor.collect_examples_at_once_different_allocation(collocation_path)

elif flag == 3:
    corpus_path = "../data/preprocessed/현대문어_형태분석_전처리(원문만 추출)"
    write_path = None

    extractor = Kce.KoreanCollocationExtractor(corpus_path, write_path)
    extractor.find_duplication("음악 소리가 너무 커서 우린 이런 말들을 거의 악을 쓰며 싸우듯이 나누어야 했다.")

elif flag == 4:
    str1 = "/NNG 악/NNG + 을/JKO + 쓰/VV"
    str2 = "악/NNG + 을/JKO + 쓰/VV"
    test = r"(.* 악/NNG \+ 을/JKO \+ 쓰/VV|^악/NNG \+ 을/JKO \+ 쓰/VV).*"
    regex = re.compile(test)
    if regex.match(str2):
        print("matched")
    else:
        print("not matched")


stop = timeit.default_timer()
print("소요 시간: ", stop - start)


