from bs4 import BeautifulSoup
import requests
import re
import  meaningcloud
import nltk
import pdb
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



url="https://www.index.hr/vijesti/clanak/stozer-objavio-imamo-219-novih-slucajeva-2-osobe-umrle/2206278.aspx"
def index_parser(url):
    excluded=["Scribd"]
    r=requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for tag in soup.find_all("em"):
        tag.decompose()
    clanak= soup.find("div",{"class":"text"}).find_all(["p","h1","h2","h3","h4","h5"])


    for element in clanak:
        if not element.text.endswith("."):
            sadrzaj += f">{element.text}." +"\n\n"

        elif element.find("strong") is not None:

            sadrzaj+= f">**{element.text}**" +"\n\n"

        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


# vec_url="https://www.vecernji.hr/vijesti/ja-sad-idem-kazao-je-supruzi-ljerki-dvije-je-godina-tragala-za-njim-1398430"

def vecernji_parser(vec_url):
    r=requests.get(vec_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"class":"article__body--main_content"}).find_all("p")

    for element in clanak:
       #element = re.sub(">`","",element.text)

        sadrzaj += f">{element.text}" +"\n\n"

    return sadrzaj


jut_url= "https://www.jutarnji.hr/vijesti/hrvatska/beros-iznenaden-velikim-brojem-novozarazenih-trudimo-se-naci-nacin-kako-to-zaustaviti-15014576"

def jutarnji_parser(jut_url):
    print(jut_url) # obrisat
    r=requests.get(jut_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")

    clanak= soup.find("div",{"class":"itemFullText"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.name=="h1":
            sadrzaj+=f"{element.text}." +"\n"
        if element.name=="h2":
            sadrzaj+=f"{element.text}."+ "\n"
        # if element.name == "h3":
        #     sadrzaj+=f"###{element.text}" +"\n"
        if element.name=="h4":
            sadrzaj+=f"{element.text}."+ "\n"
        else:
            element = element.text.strip("-")
            sadrzaj += f">{element}"+"\n\n"

    return sadrzaj

# clanak=jutarnji_parser(jut_url)
# print(clanak)



#rtl_url="https://www.rtl.hr/vijesti-hr/vijesti/3812727/onkoloska-pacijentica-ispred-rebra-ljudi-stoje-u-kilometarskim-redovima-bez-case-vode-na-hladnoci/"

def rtl_parser(rtl_url):
    r=requests.get(rtl_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for item in soup.findAll("p"):
        atag=item.find_all("a")
        for a in atag:
            a.decompose()

    sadrzaj=""
    clanak= soup.find("div",{"class":"Article-meteredContent"}).find_all(["p","h1","h3"])

    for element in clanak:
        if "(RTL)" in element.text:
            pass
        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return sadrzaj


_24sata_url="https://www.24sata.hr/sport/kakav-majstor-vlasic-u-derbiju-zabio-eurogol-lovrenu-i-zenitu-711833"
def d24sata_parser(_24sata_url):
    r=requests.get(_24sata_url)
    soup = BeautifulSoup(r.content, "html.parser")
    # print(soup.prettify())
    sadrzaj=""
    clanak= soup.find("div",{"class":"article__text"}).get_text()
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak = re.sub('<[^<]+?>', '', clanak)
    return clanak.strip()


n1_url="http://hr.n1info.com/Vijesti/a536658/Ministrica-Brnjac-Ne-mozemo-odmah-nakon-uvodjenja-mjera-ocekivati-pad-zarazenih.html"

def n1_parser(n1_url):
    r=requests.get(n1_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for item in soup.find_all("p",{"class":"time"}):
        item.decompose()
    
    clanak= soup.find("div",{"class":"single-article-content"}).find_all(["p","h1","h2","h3"])


    for element in clanak[1:-1]:
        if "OVDJE" not in element.text:
            sadrzaj += f">{element.text}" +"\n\n"
        sadrzaj=sadrzaj.split("N1 pratite",1)[0]
    return sadrzaj


telegram_url = "https://www.telegram.hr/politika-kriminal/upoznajte-bracu-macan-drzava-im-daje-13-milijuna-kuna-za-fake-news-portal-prodaju-lazne-ankete-i-ustaske-majice/"
def telegram_parser(telegram_url):
    r = requests.get(telegram_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find_all(["p", "h1", "h2", "h3"])

    for element in clanak[3:-9]:
        if element.name == "h1":
            sadrzaj += f"> **{element.text}.**" +"\n"
        if element.name == "h2":
            sadrzaj += f">{element.text}." +"\n"
        elif element.text in sadrzaj:
            pass
        else:
            sadrzaj += f">{element.text}" +"\n\n"
    return (sadrzaj)

 
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


#hr_danas_url="https://hrvatska-danas.com/2020/05/01/milanovic-u-okucanima-poznatom-hos-ovcu-rekao-mrs-u-policiju-privedeni-hrvatski-ratni-veterani/"

def hr_danas_parser(hr_danas_url):
    r=requests.get(hr_danas_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"class":"entry-content clearfix"}).find_all("p")

    for element in clanak[:-8]:

        sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


#dnevnik_url="https://dnevnik.hr/vijesti/hrvatska/davor-bernardic-o-incidentu-u-okucanima---603861.html"

def dnevnik_parser(dnevnik_url):
    r=requests.get(dnevnik_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"class":"article-body-in"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak[:-6]:

        sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


#novilist_url="http://www.novilist.hr/Vijesti/Svijet/SVEDSKI-EPIDEMIOLOG-JOHAN-GIESECKE-Europa-je-napravila-gresku-i-platit-ce-cijenu-cjepiva-ce-na-kraju-biti-uzaludna"

def novilist_parser(novilist_url):
    r=requests.get(novilist_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"id":"article-text"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        # if element.n>me=="h1":
        #     sadrzaj+=f"#{element.text}" +"\n"
        if element.name=="h3":
            sadrzaj+=f"{element.text}"+ "\n"
        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)

slobodna_url="https://slobodnadalmacija.hr/vijesti/hrvatska/ante-tomic-crvena-zvijezda-ima-svako-pravo-stajati-nad-rijekom-to-da-se-grad-ne-zove-fiume-iskljucivo-je-partizanska-zasluga-1045910"
def slobodna_parser(slobodna_url):
    r=requests.get(slobodna_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak= soup.find("div",{"class":"itemFullText"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:


        # if element.name=="h1":
        #     sadrzaj+=f"#{element.text}" +"\n"
        if element.name=="h3":
            sadrzaj+=f"**{element.text}**"+ "\n"

        else:
            sadrzaj += f"{element.text}" +"\n\n"

    return (sadrzaj)



#glasistre_url="https://www.glasistre.hr/svijet/bih-rusko-veleposlanstvo-zacudeno-odbijanjem-dolaska-njihovih-vojnika-640701"
def glasistre_parser(glasistre_url):
    r=requests.get(glasistre_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak= soup.find("div",{"id":"CloudHub_Element_Content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:


        # if element.name=="h1":
        #     sadrzaj+=f"#{element.text}" +"\n"
        if element.name=="h3":
            sadrzaj+=f">{element.text}"+ "\n"

        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


#nacional_url="https://www.nacional.hr/okrivljenici-za-palez-vikendice-radovana-ortynskog-izlaze-iz-pritvora/"
def nacional_parser(nacional_url):
    r=requests.get(nacional_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak= soup.find("div",{"class":"entry-content clearfix"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:


        # if element.name=="h1":
        #     sadrzaj+=f"#{element.text}" +"\n"
        if element.name=="h3":
            sadrzaj+=f">{element.text}"+ "\n"

        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj[:-12])


nethr_url = "https://net.hr/danas/hrvatska/grlic-radman-otvorio-restoran-u-svom-ministarstvu-posao-firmi-zanimljivo-povezanoj-s-megatvrtkom-u-vlasnistvu-obitelji-ministra/"


def nethr_parser(nethr_url):
    s = requests.session()
    r = s.get(nethr_url, headers=headers)
    # r=requests.get(nethr_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    clanak = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5"])

    for element in clanak[7:-75]:
        sadrzaj += f">{element.text}" + "\n\n"

    return (sadrzaj)



#tportal_url="https://www.tportal.hr/vijesti/clanak/detalji-nesrece-kod-zemunika-poginuo-clan-krila-oluje-i-kadet-koji-je-tek-poceo-s-letackom-obukom-20200507"
def tportal_parser(tportal_url):
    r=requests.get(tportal_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    for strong in soup.find_all("strong"):
        strong.replaceWith(f"**{strong.text}**")
    for item in soup.find_all("figcaption",{"class":"meta"}) or soup.find_all("figcaption",{"class":"meta"}):
        item.decompose()


    clanak=  soup.find_all("div",{"class":"introComponent"}) + soup.find("section",{"class":"articleComponents"}).find_all(["p","h1","h2","h3","h4","h5"])


    for element in clanak:


        # if element.name=="h1":
        #     sadrzaj+=f"#{element.text}" +"\n"
        if element.name=="h3":
            sadrzaj+=f">{element.text}"+ "\n"

        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)


#ampindex_url="https://amp.index.hr/article/2180444/stadion-maksimir-privremeno-neupotrebljiv-dobio-zutu-oznaku-urusava-se-godinama"
def ampindex_parser(ampindex_url):
    excluded=["Scribd"]
    r=requests.get(ampindex_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak= soup.find("div",{"class":"articleText"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:

        if element.find("strong") != None:

            sadrzaj+= f"> **{element.text}**" +"\n\n"

        else:
            sadrzaj += f">{element.text}" +"\n\n"

    return (sadrzaj)

#sportnet_url = "https://sportnet.rtl.hr/vijesti/541514/vodeni-sportovi-jedrenje/jedrilicari-i-skiperi-najtrazeniji-smjer-ovog-ljeta-na-kif-u/"
def sportnet_parser(sportnet_url):
    r=requests.get(sportnet_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak = soup.find("div", {"class":"st1"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak[1:-5]:
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

dal_danas_url = "https://www.dalmacijadanas.hr/turisti-gledali-u-soku-zena-razmazala-govna-po-kipu-grgura-to-je-sotona/"
def dal_danas_parser(dal_danas_url):
    s=requests.session()
    r=s.get(dal_danas_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj=""
    clanak = soup.find("div", {"class":"td-ss-main-content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        sadrzaj +=  f">{element.text}" +"\n\n"
    return sadrzaj

hrt_magazin_url = "https://magazin.hrt.hr/645384/price-iz-hrvatske/more-na-sest-dubrovackih-plaza-onecisceno-fekalijama"
def hrt_magazin_parser(hrt_magazin_url):
    r = requests.get(hrt_magazin_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class": "body"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj += f">{element.text}" +"\n\n"

    return sadrzaj

maxurl = "https://www.maxportal.hr/sport/mec-za-pamcenje-coric-spasio-sest-mec-lopti-za-osminu-finala-us-opena-video/"
def maxportal_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"post_content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

bug_url = "https://www.bug.hr/najava/new-world-azothara-na-aeternumu-mora-da-je-sala-16386"
def bug_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"post-full__content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

dalport_url = "https://dalmatinskiportal.hr/vijesti/festival/74323?fbclid=IwAR0EsUG3cGHByFUsh6WU5jj5G8sc1z5P_tXu5PavQvJze4jlAIV5_-sSNjM"
def dalportal_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"open_article_content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

poslovni_url = "https://www.poslovni.hr/europska-unija/uskoro-stize-europska-minimalna-placa-evo-o-cemu-je-zapravo-rijec-i-koliko-bi-trebao-porasti-minimalac-kod-nas-4251627"
def poslovni_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("article", {"class":"single__inner"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

kamenjar_url = "https://kamenjar.com/na-danasnji-dan-oba-su-pala-jedna-od-najpoznatijih-video-snimki-iz-domovinskog-rata/"
def kamenjar_parser(url):
    headers = {}
    headers['User-agent'] = "HotJava/1.1.2 FCS"
    s = requests.session()
    r = s.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"id":"mvp-content-main"}).find_all(["p","h1","h2","h3","h4","h5"])
    for element in clanak:
        if element.find("strong") is not None:
            sadrzaj += f"> **{element.text}**" +"\n\n"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj[:-57]

def direktno_parser(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    sadrzaj = ""
    clanak = soup.find("div", {"class":"main-content"}).find_all(["p","h1","h2","h3","h4","h5"])

    for element in clanak[0:2] + clanak[5:-3]:
        # if element.find("strong") is not None:
        #     sadrzaj += f"> **{element.text}**"
        sadrzaj +=  f">{element.text}" +"\n\n"

    return sadrzaj

