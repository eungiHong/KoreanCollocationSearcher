import requests
from bs4 import BeautifulSoup

print("on progress...")

page_number = 505
while True:
    page_number += 1
    article_number = 0
    address = "http://www.itdaily.kr/news/articleList.html?page=" + str(page_number) + "&total=74711&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=I&view_type="
    req = requests.get(address)
    if req.status_code != 200:
        break
    req.encoding = 'euc-kr'
    soup = BeautifulSoup(req.text, 'html.parser')
    titles = soup.select('h3 > a')

    for title in titles:
        article_number += 1
        url = "http://www.itdaily.kr/" + title.get('href')
        request = requests.get(url)
        request.encoding = 'euc-kr'
        soup = BeautifulSoup(request.text, 'html.parser')
        contents = soup.select('p')
        content_array = []
        for content in contents:
            content_array.append(content.get_text())

        file_path = "../data/ITDaily/raw_data/" + str(page_number) + "-" + str(article_number) + ".txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(title.text) + "\n")
            for content in content_array:
                file.write(content + "\n")