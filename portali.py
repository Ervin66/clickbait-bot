from bs4 import BeautifulSoup
import requests
import re
import  meaningcloud
import nltk
import pdb
from markdownify import markdownify 
headers = {}
headers['User-agent'] = "HotJava/1.1.2 FCS"

#obrisat
#tportal
#index formating
#url="https://www.index.hr/vijesti/clanak/policija-za-index-muskarci-s-majicama-zds-nisu-privedeni-jer-je-padala-kisa/2179630.aspx"

license_key= "3668d6e355b00b38ff7d1b46c45c97de"
get_fibo = False

number_categories = 3
# @param topics_relevance - Relevance used for filtering entities and concepts
topics_relevance = 80

cluster_score_threshold = 50

# auxiliary variables to follow progress of the process
index_count = 1
total_files = None


# def getSummarization(text, sentences):
#     # We are going to make a request to the Summarization API
#     summary = ''
#     print("\tGetting automatic summarization...")
#     summarization_response = meaningcloud.SummarizationResponse(meaningcloud.SummarizationRequest(license_key, sentences=sentences, txt=text).sendReq())
#     if summarization_response.isSuccessful():
#         summary = summarization_response.getSummary()

#     else:
#         print("\tOops! Request to Summarization was not succesful: (" + summarization_response.getStatusCode() + ') ' + summarization_response.getStatusMsg())

#     return summary



url="https://www.index.hr/vijesti/clanak/tip-uhicen-zbog-hrpe-droge-slikao-se-zagrljen-s-plenkovicem-hdz-obrisao-sliku/2259862.aspx"
def index_parser(url):
    excluded=["Scribd"]
    r=requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for tag in soup.find_all(["em", "img"]):
        tag.decompose()
    clanak= soup.find("div",{"class":"text"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        if element.text != "":
            sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"

        # if not element.text.endswith("."):
        #     sadrzaj += f">{element.text}." +"\n\n"

        # elif element.find("strong") is not None:

        #     sadrzaj+= f">**{element.text}**" +"\n\n"

        # else:
        #     sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


# vec_url="https://www.vecernji.hr/vijesti/nezapamcena-dragovoljna-predaja-oruzja-u-sisku-sve-ovo-predao-je-jedan-gradanin-1474677"

def vecernji_parser(vec_url):
    r = requests.get(vec_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class": "article__body--main_content"}).find_all("p")
    soup.find("span", {"class": "ck_image_in_article ck_image_in_article--left100"}).decompose()
    for element in clanak:
        print(element)
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


def jutarnji_parser(jut_url):
    r = requests.get(jut_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div",{"class":"itemFullText"}).find_all(["p","h1","h2","h3","h4","h5"])
    soup.find("p", {"class": "Related-article-title fw-700 h-4"}).decompose()
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj

# rtl_url="https://www.rtl.hr/vijesti-hr/novosti/svijet/3994744/osobe-koje-su-se-cijepile-imaju-antitijela-ili-negativan-nalaz-ovog-ljeta-mogu-ljetovati-u-jednoj-europskoj-zemlji-3994744/"

def rtl_parser(rtl_url):
    r = requests.get(rtl_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for item in soup.findAll("p"):
        atag=item.find_all("a")
        if "VEZANA" in item.text:
            item.decompose()
        for a in atag:
            a.decompose()
    sadrzaj=""
    clanak= soup.find("div",{"class":"Article-meteredContent"}).find_all(["p","h1","h3"])
    soup.find("div",{"class":"Related-article Article-related"}).decompose()
    for element in clanak:
        if "(RTL)" in element.text:
            pass
        else:
            if element.text != " ":
                sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


# _24sata_url="https://www.24sata.hr/sport/ajmo-po-tokio-evo-gdje-gledati-pravi-klasik-hrvata-i-francuza-750260"
def d24sata_parser(_24sata_url):
    r = requests.get(_24sata_url)
    soup = BeautifulSoup(r.content, "html.parser")
    # print(soup.prettify())
    sadrzaj = ""
    clanak = soup.find("div",{"class":"article__text"}).get_text()
    sadrzaj = ">" + markdownify(str(clanak), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


n1_url = "https://hr.n1info.com/vijesti/tihana-jendricko-zbog-pandemije-i-potresa-sve-vise-ljudi-sa-psihickim-smetnjama/"
def n1_parser(n1_url):
    r=requests.get(n1_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for item in soup.find_all("p",{"class":"time"}):
        item.decompose()
    for item in soup.find_all("section"):
        item.decompose()

    clanak= soup.find("div",{"class":"entry-content"}).find_all(["p"])
    

    for element in clanak[:-2]:
        if "OVDJE" not in element.text and element.text != "":
            sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
        sadrzaj=sadrzaj.split("N1 pratite",1)[0]
    return sadrzaj


# telegram_url = "https://www.telegram.hr/politika-kriminal/upoznajte-bracu-macan-drzava-im-daje-13-milijuna-kuna-za-fake-news-portal-prodaju-lazne-ankete-i-ustaske-majice/"
# def telegram_parser(telegram_url):
#     r = requests.get(telegram_url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     sadrzaj = ""
#     clanak = soup.find("div",{"class":"full relative single-article-body"}).find_all(["p", "h1", "h2", "h3"])
#     print(soup)
#     for element in clanak:
#         sadrzaj += markdownify(element)
        
#     return (sadrzaj)

# print(telegram_parser(telegram_url))
#net.hr

# narod_url="https://narod.hr/kultura/video-1-svibnja-1995-operacija-bljesak-svanulo-sunce-hrvatske-slobode-koju-su-sanjale-generacije-hrvata"
# def narod_parser(narod_url):
#     s=requests.session()
#     r=s.get(narod_url, headers=headers)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     sadrzaj=""
#     clanak= soup.find("div",{"class":"td-ss-main-content"})#.find_all("p")
#     print(soup.pretti>y())

#     # for element in clanak:

#     #     sadrzaj += {element}.text +"\n"

#     # print (sadrzaj)

# narod_parser(narod_url)


# hr_danas_url="https://hrvatska-danas.com/2021/03/13/milanovic-sluti-odluku-dva-profesora-prava-za-njegovo-tumacenje-a-osam-je-protiv/"

# def hr_danas_parser(hr_danas_url):
#     r=requests.get(hr_danas_url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     sadrzaj=""
#     clanak= soup.find("div",{"class":"tdb-block-inner td-fix-index"}).find_all("p")
#     print(clanak)
#     with open("output1.html", "w", encoding="utf8") as file:
#         file.write(str(soup))
#     for element in clanak:
#         sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
#     return (sadrzaj)
# print(hr_danas_parser(hr_danas_url))

# dnevnik_url="https://dnevnik.hr/vijesti/koronavirus/u-bih-u-subotu-vise-od-tisucu-zarazenih-u-sarajevu-stroga-ogranicenja---643745.html"

def dnevnik_parser(dnevnik_url):
    r=requests.get(dnevnik_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    soup.find("div",{"class":"banner-holder inarticle-2"}).decompose()
    clanak= soup.find("div",{"class":"article-body-in"}).find_all(["p","h1","h2","h3","h4","h5"])
    for item in soup.find_all("span"):
        item.decompose()
    for element in clanak[:-3]:
        if element.text != "\n":
            sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"

    return (sadrzaj)

# novilist_url="https://www.novilist.hr/rijeka-regija/https-www-novilist-hr-wp-admin-post-phppost493688actionedit/"

def novilist_parser(novilist_url):
    r=requests.get(novilist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup.find("div",{"class":"linked-news"}).decompose()
    soup.find("div",{"class":"imageCopyright"}).decompose()
    sadrzaj=""
    clanak= soup.find("div",{"class":"article-content"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return (sadrzaj)



# slobodna_url="https://slobodnadalmacija.hr/split/vrhovni-sud-presudom-je-spasio-obitelj-kovacevic-u-splitskoj-radunici-odvjetnik-banovac-da-su-delozirali-slavicu-deset-tisuca-ljudi-letjelo-bi-na-ulicu-1083743"
def slobodna_parser(slobodna_url):
    r=requests.get(slobodna_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"class":"itemFullText"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return (sadrzaj)



# glasistre_url="https://www.glasistre.hr/hrvatska/plenkovic-kurz-i-jos-4-premijera-pisali-eu-zbog-debaklas-s-cjepivom-evo-sto-traze-od-celnika-unije-706723"
# def glasistre_parser(glasistre_url):
#     headers = {}
#     headers['User-agent'] = "HotJava/1.1.2 FCS"
#     s = requests.session()
#     r = s.get(glasistre_url, headers=headers)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     sadrzaj=""
#     clanak= soup.find("div",{"id":"CloudHub_Element_Content"}).find_all(["p","h1","h2","h3","h4","h5"])
#     for element in clanak:
#         sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
#     return (sadrzaj)
# print(glasistre_parser(glasistre_url))


# nacional_url="https://www.nacional.hr/tisuce-prosvjednika-i-protivnika-cijepljenja-diljem-njemackih-gradova/"
def nacional_parser(nacional_url):
    r = requests.get(nacional_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak= soup.find("div", {"class": "entry-content clearfix"}).find_all(["p", "h1", "h2", "h3", "h4", "h5"])
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return (sadrzaj[:-12])



# nethr_url = "https://net.hr/sport/rukomet/ispricavam-se-gledateljima-vjerojatno-su-naviknuli-na-ovakve-utakmice-hrvoje-horvat-pod-dojmom-nakon-infarktne-zavrsnice-kauboja/"
def nethr_parser(nethr_url):
    s = requests.session()
    r = s.get(nethr_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div",{"class":"article-content"}).find_all(["p", "h1", "h2", "h3", "h4", "h5"])
    for element in clanak[:-1]:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return (sadrzaj)



# tportal_url="https://www.tportal.hr/vijesti/clanak/potreban-je-opravdani-zdravstveni-okidac-da-bi-hrvatska-suspendira-cijepljenje-astrazenecinim-cjepivom-foto-20210313"
def tportal_parser(tportal_url):
    r = requests.get(tportal_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    soup.find("div", {"class": "listComponentType2 alignCenter columns2"}).decompose()
    for item in soup.find_all("figcaption",{"class":"meta"}) or soup.find_all("figcaption",{"class":"meta"}):
        item.decompose()
    clanak = soup.find_all("div",{"class":"introComponent"}) + soup.find("section",{"class":"articleComponents"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return (sadrzaj)


# ampindex_url="https://amp.index.hr/article/2180444/stadion-maksimir-privremeno-neupotrebljiv-dobio-zutu-oznaku-urusava-se-godinama"
# def ampindex_parser(ampindex_url):
#     excluded=["Scribd"]
#     r=requests.get(ampindex_url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     sadrzaj=""
#     clanak= soup.find("div",{"class":"articleText"}).find_all(["p","h1","h2","h3","h4","h5"])

#     for element in clanak:

#         if element.find("strong") != None:

#             sadrzaj+= f"> **{element.text}**" +"\n\n"

#         else:
#             sadrzaj += f">{element.text}" +"\n\n"

#     return (sadrzaj)

# sportnet_url = "https://sportnet.rtl.hr/vijesti/548907/rukomet-reprezentacija/hrvatska-se-podigla-s-dna-i-velikim-preokretom-svladala-portugal/"
def sportnet_parser(sportnet_url):
    r=requests.get(sportnet_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup.find("div", {"class":"st2emulation onlymobile"}).decompose()
    sadrzaj=""
    clanak = soup.find("div", {"class":"st1"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak[1:-5]:
        if "FOTO" not in element.text:
            sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj



# dal_danas_url = "https://www.dalmacijadanas.hr/plenkovic-i-jos-pet-europskih-lidera-pisali-celnicima-eu-a-traze-hitan-sastanak/"
def dal_danas_parser(dal_danas_url):
    s = requests.session()
    r = s.get(dal_danas_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    soup.find("div", {"class":"comments"}).decompose()
    sadrzaj = ""
    clanak = soup.find("div", {"class":"td-ss-main-content"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


# hrt_magazin_url = "https://magazin.hrt.hr/zabava/zivot-na-visokoj-sapi-1049076"
# def hrt_magazin_parser(hrt_magazin_url):
#     r = requests.get(hrt_magazin_url)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     for item in soup:
#         item.find("div", {"class": "text-white py-3 px-3 xl:pl-6 xl:pr-12 flex flex-col xl:flex-row justify-between imageDesc"}).decompose()
#     sadrzaj = ""
#     clanak = soup.find("div", {"class": "w-full xl:w-7/12 px-0.2 xl:px-4 text-lg a-body"}).find_all(["p","h1","h2","h3","h4","h5"])
#     for element in clanak:
#         sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
#     return sadrzaj
# print(hrt_magazin_parser(hrt_magazin_url))


# maxurl = "https://www.maxportal.hr/vijesti/u-kamionu-iz-srbije-4-migranta-mrtva-19-u-bolnici-ima-i-djece-neki-su-ispali-kroz-krov/"
def maxportal_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"post_content"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak[:-5]:
        if "Foto" not in element.text:
            sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj



# bug_url = "https://www.bug.hr/istrazivanja/nove-karte-nadzemne-biomase-za-bolje-razumijevanje-globalnih-kretanja-ugljicnog-19770"
def bug_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"post-full__content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


# dalport_url = "https://dalmatinskiportal.hr/sport/roko-leni-ukic-je-mvp-22--kola-aba-lige/92631"
def dalportal_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"open_article_content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj


# poslovni_url = "https://www.poslovni.hr/hrvatska/uvodenje-eura-nije-cilj-po-sebi-to-je-dobar-alat-za-razvoj-4278791"
def poslovni_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("article", {"class":"single__inner"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak[:-5]:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj



# kamenjar_url = "https://kamenjar.com/predsjednik-osjeckog-suda-zatrazio-razrjesenje-dvojice-sudaca-zbog-druzenja-s-mamicem/"
# def kamenjar_parser(url):
#     headers = {}
#     headers['User-agent'] = "HotJava/1.1.2 FCS"
#     s = requests.session()
#     r = s.get(url, headers=headers)
#     soup = BeautifulSoup(r.content, 'html.parser')
#     print(soup.prettify())
#     sadrzaj = ""
#     clanak = soup.find("div", {"id":"mvp-content-main"}).find_all(["p","h1","h2","h3","h4","h5"])
#     for element in clanak:
#         sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
#     return sadrzaj[:-57]

direkt_url = "https://direktno.hr/direkt/baric-mladi-direktno-grad-zagreb-apsolutno-nista-nije-poduzeo-pitanju-obnove-nema-dovoljno-gradevins-227240/"
def direktno_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"main-content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak[0:2] + clanak[5:-2]:
        sadrzaj += ">" + markdownify(str(element), strip=['a'], heading_style="ATX") + "\n\n"
    return sadrzaj

