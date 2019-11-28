import fnmatch
import os
import re

from konlpy.tag import Kkma


def kkma_analysis(target_file_path, write_path):
    list_of_lines = get_lines_utf8(target_file_path)
    file = open(write_path, "w", encoding="utf-8")
    kkma = Kkma()
    for line in list_of_lines:
        file.write(line + "\n")
        try:
            analyzed_morphemes = kkma.pos(line)
            for morpheme in analyzed_morphemes:
                file.write(str(morpheme) + " ")
            file.write("\n")
        except:
            continue
        file.write("\n")
    file.close()


def kkma_analysis_at_once_for_sejong(corpus_path, raw_and_tagged_directory, tagged_only_directory):
    kkma = Kkma()
    list_of_files = os.listdir(corpus_path)
    for entry in sorted(list_of_files):
        if fnmatch.fnmatch(entry, "*.txt"):
            list_of_lines = get_lines_utf8(corpus_path + "/" + entry)
            raw_and_tagged_path = raw_and_tagged_directory + "/" + entry + ".txt"
            tagged_only_path = tagged_only_directory + "/" + entry + ".txt"
            raw_and_tagged_file = open(raw_and_tagged_path, "w", encoding="utf-8")
            tagged_only_file = open(tagged_only_path, "w", encoding="utf-8")
            for line in list_of_lines:
                if len(line) > 0:
                    raw_and_tagged_file.write(line + "\t")
                    try:
                        analyzed_morphemes = kkma.pos(line)
                        for idx, pair in enumerate(analyzed_morphemes):
                            if idx == len(analyzed_morphemes) - 1:
                                raw_and_tagged_file.write(pair[0] + "/" + pair[1])
                                tagged_only_file.write(pair[0] + "/" + pair[1])
                            else:
                                raw_and_tagged_file.write(pair[0] + "/" + pair[1] + " ")
                                tagged_only_file.write(pair[0] + "/" + pair[1] + " ")
                        raw_and_tagged_file.write("\n")
                        tagged_only_file.write("\n")
                    except:
                        continue
            raw_and_tagged_file.close()
            tagged_only_file.close()


def kkma_analysis_at_once_for_itdaily(corpus_path, raw_and_tagged_directory, tagged_only_directory):
    kkma = Kkma()
    list_of_files = os.listdir(corpus_path)
    for entry in sorted(list_of_files):
        number = entry.split("-")[0]
        if 800 < int(number) < 1901:
            if fnmatch.fnmatch(entry, "*.txt"):
                list_of_lines = get_lines_utf8(corpus_path + "/" + entry)
                raw_and_tagged_path = raw_and_tagged_directory + "/" + number + ".txt"
                tagged_only_path = tagged_only_directory + "/" + number + ".txt"
                raw_and_tagged_file = open(raw_and_tagged_path, "a", encoding="utf-8")
                tagged_only_file = open(tagged_only_path, "a", encoding="utf-8")
                for line in list_of_lines:
                    if len(line) > 0:
                        raw_and_tagged_file.write(line + "\t")
                        try:
                            analyzed_morphemes = kkma.pos(line)
                            for idx, pair in enumerate(analyzed_morphemes):
                                if idx == len(analyzed_morphemes) - 1:
                                    raw_and_tagged_file.write(pair[0] + "/" + pair[1])
                                    tagged_only_file.write(pair[0] + "/" + pair[1])
                                else:
                                    raw_and_tagged_file.write(pair[0] + "/" + pair[1] + " ")
                                    tagged_only_file.write(pair[0] + "/" + pair[1] + " ")
                            raw_and_tagged_file.write("\n")
                            tagged_only_file.write("\n")
                        except:
                            continue
                raw_and_tagged_file.close()
                tagged_only_file.close()


def kkma_analysis_with_raw_text(corpus_path, output_path):
    kkma = Kkma()
    list_of_files = os.listdir(corpus_path)
    for entry in list_of_files:
        print(entry)
        if fnmatch.fnmatch(entry, "*.txt"):
            list_of_lines = get_lines_utf8(corpus_path + "/" + entry)
            write_path = output_path + "/" + entry.split("-")[0] + ".txt"
            file = open(write_path, "a", encoding="utf-8")
            for line in list_of_lines:
                if len(line) > 0:
                    file.write(line + "\t")
                    try:
                        analyzed_morphemes = kkma.pos(line)
                        for idx, pair in enumerate(analyzed_morphemes):
                            if idx == len(analyzed_morphemes) - 1:
                                file.write(pair[0] + "/" + pair[1])
                            else:
                                file.write(pair[0] + "/" + pair[1] + " ")
                        file.write("\n")
                    except:
                        continue
            file.close()


def kkma_analysis_only(corpus_path, output_path):
    kkma = Kkma()
    list_of_files = os.listdir(corpus_path)
    for entry in list_of_files:
        print(entry)
        if fnmatch.fnmatch(entry, "*.txt"):
            list_of_lines = get_lines_utf8(corpus_path + "/" + entry)
            write_path = output_path + "/" + entry.split("-")[0] + ".txt"
            file = open(write_path, "a", encoding="utf-8")
            for line in list_of_lines:
                if len(line) > 0:
                    try:
                        analyzed_morphemes = kkma.pos(line)
                        for idx, pair in enumerate(analyzed_morphemes):
                            if idx == len(analyzed_morphemes) - 1:
                                file.write(pair[0] + "/" + pair[1])
                            else:
                                file.write(pair[0] + "/" + pair[1] + " ")
                        file.write("\n")
                    except:
                        continue
            file.close()


def get_docx_files(dir_path):
    list_of_file_names = []
    for path, dirs, files in os.walk(dir_path):
        for f in fnmatch.filter(files, "*.docx"):
            fullname = os.path.abspath(os.path.join(path, f))
            list_of_file_names.append(fullname)
    return list_of_file_names


# 파일 경로를 받아서 '\n' 단위로 파일을 읽은 결과를 담은 리스트를 반환
def get_lines_utf8(file_path):
    file = open(file_path, "r", encoding="utf-8")
    line_list = []
    for line in file:
        if line.endswith("\n"):
            line = line.strip("\n")
        line_list.append(line)
    file.close()
    return line_list


def get_lines_utf16(file_path):
    file = open(file_path, "r", encoding="utf-16")
    line_list = []
    for line in file:
        if line.endswith("\n"):
            line = line.strip("\n")
        line_list.append(line)
    file.close()
    return line_list


def write_lines_utf8(file_path, list_of_lines):
    file = open(file_path, "w", encoding="utf-8")
    for line in list_of_lines:
        file.write(line + "\n")
    file.close()


def write_lines_utf16(file_path, list_of_lines):
    file = open(file_path, "w", encoding="utf-16")
    for line in list_of_lines:
        file.write(line + "\n")
    file.close()


def write_again_in_reverse_order(file_path, write_path):
    line_list = get_lines_utf8(file_path)
    file = open(write_path, "w", encoding="utf-8")
    for line in reversed(line_list):
        file.write(line + "\n")
    file.close()


def write_again_in_reverse_order_at_once(dir_path):
    list_of_files = os.listdir(dir_path)
    for entry in list_of_files:
        if fnmatch.fnmatch(entry, "*.txt"):
            temp = entry.rstrip(".txt")
            write_again_in_reverse_order(dir_path + "/" + entry, dir_path + "/" + temp + "_new.txt")


# python string은 immutable하므로 새로운 스트링 생성해야.
def add_backslash(string):
    new_string = ""
    for char in string:
        if char == '+':
            new_string += r"\+"
        elif char == '*':
            new_string += r"\*"
        else:
            new_string += char
    return new_string
