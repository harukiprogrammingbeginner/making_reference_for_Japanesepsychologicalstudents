import streamlit as st
import requests
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 

book_title = st.text_input("引用したい翻訳本のタイトルを入力してください")
if "" != book_title:
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    #立命図書館にアクセス
    url_ritsumei = "https://runners.ritsumei.ac.jp/opac/opac_search/?lang=0"
    browser.get(url_ritsumei)
    sleep(4)
    elem_input = browser.find_element_by_id("text_kywd")
    elem_input.send_keys(book_title)
    elem_button = browser.find_elements_by_tag_name("button")[2]
    elem_button.click()
    sleep(10)
    url_searched = browser.current_url

    res = requests.get(url_searched)
    soup = BeautifulSoup(res.text, "html.parser")
    sleep(5)
    book_title1 = soup.find("p", attrs={"class": "result-book-title"})
    #book_title1 = browser.find_element_by_class_name("result-book-title")
    tag_a = book_title1.find("a")
    url2 = tag_a.get("href")

    sleep(5)
    url3 = "https://runners.ritsumei.ac.jp/" + url2
    res2 = requests.get(url3)
    soup2 = BeautifulSoup(res2.text, "html.parser")
    publisher_year = soup2.find_all("span", attrs={"class": "more"})
    title_foreign = publisher_year[3]
    title_foreign_complete = title_foreign.text.split("異")[0].strip("原タイトル:")
    # タイトルと著者の名前の取得(詳細ページに飛ぶ前で)
    title_names = tag_a.text
    title_names = tag_a.text.replace("\n", "")
    title_names = title_names.replace("\t", "")
    title_names = title_names.split("/")
    # タイトル、名前に分ける
    title = title_names[0]
    # タイトルをメインタイトルとサブタイトルに分ける。
    if ":" in title:
        title_split = title.split(" : ")
        main_title = title_split[0]
        sub_title = title_split[1]
    else:
        main_title = title

    # サブタイトルの後ろスペースを消す。
    sub_title = sub_title.replace(" ", "")
    # 著者名
    names = title_names[1]
    # 著者名を外国人と日本人に分ける。
    names = names.split(" ; ")
    names_foreign = names[0]
    # 外国人一人ずつ分ける。
    names_foreign = names_foreign.split(",")
    names_foreign = [name_foreign.strip("[著]") for name_foreign in names_foreign]
    #外国人の人数-1
    lf = len(names_foreign) - 1
    # 外国人一番後ろのやつを前に入れ替え（3つじゃない場合もあるからそれの対策も）
    if ":" in publisher_year[4].text:
        names_detail = publisher_year[5].find_all("a")
    else:
        names_detail = publisher_year[4].find_all("a")
    names_foreign_detail = names_detail[:len(names_foreign)]
    names_foreign_detail = [name_foreign_detail.text for name_foreign_detail in names_foreign_detail]
    names_foreign_complete = []
    for i, name_foreign in enumerate(names_foreign):
        if "." in name_foreign:
            name_foreign_split = name_foreign.split(".")
            l_split = len(name_foreign_split)
            if l_split == 2:
                name_foreign = name_foreign_split[1] + "," + name_foreign_split[0]
                names_foreign_complete.append(name_foreign)
            elif l_split == 3:
                name_foreign = name_foreign_split[2] + "," + name_foreign_split[0] + "." + name_foreign_split[1] + "."
                names_foreign_complete.append(name_foreign)
        elif "・" in name_foreign:
            name_foreign_split = name_foreign.split("・")
            if len(name_foreign_split) == 2:
                if "," in names_foreign_detail[i]:
                    #詳細ページの名前から、ファミリーネーム以外（名）の頭文字をとってくる。
                    name_except_family_initial = names_foreign_detail[i].split(", ")[1][0]
                    name_foreign = name_foreign_split[1] + ", " +name_except_family_initial + "."
                else:
                    name_except_family_initial = names_foreign_detail[i].split(" ")[1][0]
                    name_foreign = name_foreign_split[1] + ", " + name_except_family_initial + "."

            if len(name_foreign_split) == 3:
                if "," in names_foreign_detail[i]:
                    #詳細ページの名前から、ファミリーネーム以外（名）の頭文字をとってくる。
                    name_except_family_initial = [names[i].text.split(", ")[i][0] for i in range(1, 3)]
                    name_foreign = name_foreign_split[2] + ", " + name_except_family_initial[1] + "." + name_except_family_initial[2] + "."
                else:
                    name_except_family_initial = [names[i].text.split(" ")[i][0] for i in range(1, 3)]
                    name_foreign = name_foreign_split[2] + ", " + name_except_family_initial[1] + "." + name_except_family_initial[2] + "."

        names_foreign_complete.append(name_foreign)

    for i, name_foreign_complete in enumerate(names_foreign_complete):
        if i == 0:
            names_foreign_authors = name_foreign_complete
        elif i == lf:
            names_foreign_authors = names_foreign_authors + ", & " + name_foreign_complete
        else:
            names_foreign_authors = names_foreign_authors + " , " + name_foreign_complete
        # 日本人
    names_Japanese = []
    for i, name in enumerate(names_detail):
        if i <= lf:
            continue
        elif i > lf:
            name = name.text
            name = name.replace(",", "")
            names_Japanese.append(name)

    for i, name in enumerate(names_Japanese):
        if i == 0:
            names_Japanese_authors = name
        else:
            names_Japanese_authors = names_Japanese_authors + "・" + name
    # 出版社
    publisher = publisher_year[0].text
    publisher = publisher.split(" : ")[1]
    # 年
    year = publisher_year[1].text
    year = year.split(".")[0]
    year_j = int(year)
    # 日本語の本の引用
    if ":" in title:
        reference_Japanese = f"{names_foreign_authors} {names_Japanese_authors} (訳) ({year}). {main_title}──{sub_title}──　{publisher}"
    else:
        reference_Japanese = f"{names_foreign_authors} {names_Japanese_authors} (訳) ({year}). {main_title}　{publisher}"

    #スタンフォード大学図書館にアクセス
    url = "https://library.stanford.edu/"
    browser.get(url)
    sleep(4)
    #検索ボックスを探して、
    elem_input = browser.find_elements_by_class_name("form-text")[4]
    #検索したい本のタイトルを入れる
    elem_input.send_keys(title_foreign_complete)
    sleep(3)
    #検索
    elem_button = browser.find_element_by_id('edit-submit')
    elem_button.click()
    sleep(30)

    #年と出版地、出版社取得
    results = browser.find_elements_by_class_name("result")[0:3]
    print(results)
    years = []
    region_publishers = []
    for result in results:
        print(result)
        name_publisher1 = result.find_elements_by_tag_name("div")
        name_publisher1_text = name_publisher1[2].text
        name_publisher1_text_split = name_publisher1_text.split(" : ")
        year = name_publisher1_text_split[1].split(", ")[-1].strip("©c[]").replace(".", "")
        year_int = int(year)
        if year_int <= year_j:
            years.append(year)
            region = name_publisher1_text_split[0].split(" - ")[-1].strip(".") + ": "
            publisher = name_publisher1_text_split[1].split(",")[0]
            region_publisher = region + publisher
            #タイトル取得（name_publisher1と書いてあるけど、タイトルと詳細ページのURLも含まれている。）
            title = name_publisher1[0].text.split("\n")[0]
            #詳細ページのURLを特定、クリック
            result.find_elements_by_link_text(title)[0].click()
            sleep(5)

            #ファミリーネームを日本語から英語に置き換え
            names_foreign_complete_foreign = []
            for name_foreign_detail, name_foreign_initial in zip(names_foreign_detail, names_foreign_complete):
                name_family = name_foreign_detail.split(", ")[0]
                name_initial = name_foreign_initial.split(",")[1]
                name_foreign_complete_foreign = name_family + "," + name_initial
                names_foreign_complete_foreign.append(name_foreign_complete_foreign)
            lf = len(names_foreign_complete_foreign) - 1
            #リスト作り
            for i, name_foreign_complete_foreign in enumerate(names_foreign_complete_foreign):
                if i == 0:
                    names_foreign_authors = name_foreign_complete_foreign
                elif i == lf:
                    names_foreign_authors = names_foreign_authors + ", & " + name_foreign_complete_foreign
                else:
                    names_foreign_authors = names_foreign_authors + " , " + name_foreign_complete_foreign
            reference_foreign = f"{names_foreign_authors} ({year}). {title}. {region_publisher}"
            break
        else:
            continue

    reference_complete = f"{reference_foreign} ({reference_Japanese})"


    '翻訳本の引用文献リストが出来ました'
    '→',reference_complete,
    '英語のタイトルを斜体にするのを忘れずに'
