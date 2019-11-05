import fnmatch
import os

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


def kkma_analysis_print_like_sejong_corpus(target_file_path, write_path):
    list_of_lines = get_lines_utf8(target_file_path)
    file = open(write_path, "w", encoding="utf-8")
    kkma = Kkma()
    for line in list_of_lines:
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
        else:
            new_string += char
    return new_string
