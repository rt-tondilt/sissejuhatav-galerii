#TODO:10)avaldada browseri addon, mis laseks tabis avatud lehekohta käivaid kommentaare lugeda ja kommentaari lisada
#TODO:6)Teha nee, et savestaks  kommentaarid samasse faili olenemata protokollist (http, https, ftp jne.).
#TODO:8)Määrama kommentaaride kuvamisele jäjekorra.
#TODO:9)Panna oma lehel reklaame ja sellega raha teenida.
#TODO:14)teha nii, et kui ühelt iplt on palju kommentaare, siis nende nägemiseks peab klikkama, et näita kõiki.
#TODO:15)tausta värvid õigeks teha.
from flask import Flask, request, redirect, Response,render_template
from datetime import datetime
from re import match
import os
from random import choice

app = Flask(__name__)

HTMLi_algus=["""<html>
    <head>
        <title>Universaalne kommentaarium</title>
    </head>
    <body>
        <div style="background-color:lightblue;border:4px solid black">
            <h1 style="display:inline">Universaalne Kommentaarium2</h1><a style="display:inline;float:right" href="/eng">english</a>
            <form method="GET">
                See veebiteenus võimaldab teil kommenteerida mistahes uudist mistahes veebiväljaandes või mistahes muud internetilehekülge.<br>Sisestage lehekülje, mida kommenteerida soovite, URL:<input type="text" name="kommenteeritava_URL">.
                Kuva all kommenteeritav lehekülg<input type="checkbox" name="kuva" checked>.
                <input type="submit" value="kommenteerima">
            </form>""","""<html>
    <head>
        <title>Universal commentary</title>
    </head>
    <body>
        <div style="background-color:lightblue;border:4px solid black">
            <h1 style="display:inline">Universal commentary</h1><a style="display:inline;float:right" href="/et">eesti keel</a>
            <form amethod="GET">
                This page offers you opportunity to comment any news in web or any other webpage.<br>Enter URL of the page you want to comment:<input type="text" name="URL_being_commented">.
                Show the page below<input type="checkbox" name="show" value="show" checked>.
                <input type="submit" value="to commenting">
            </form>"""]
parameeter_kommenteeriava_URL=["kommenteeritava_URL", "URL_being_commented"]
parameeter_kommentaar=["kommentaar","comment"]
parameeter_sisu_hinnang=["sisu","sisu"]
parameeter_kajastuse_hinnang=["kajastus","kajastus"]
kommentaare_ei_ole=["SELLE LEHE KOHTA KOMMENTAARE VEEL EI OLE","HERE ARE NO COMMENTS ABOUT THIS PAGE YET"]
browser_ei_toeta=["TEIE BROWSER EI TOETA HTML TAGi iframe´i","YOUR WEB BROWSER DOES NOT SUPORT HTML iframe TAG"]
HTMLi_postitamise_osa_1=['''
            <form method="POST">
                <textarea style="width:100%;height:120;resize:vertical" name="kommentaar" placeholder="Sinu kommentaar"></textarea>
                <label>Meeldib uudise sisu?</label> <input type="radio" name="sisu" value="meeldib"> Meeldib<input type="radio" name="sisu" value="ei meeldi"> Ei meeldi<br>
                <label>Meeldib kajastus ja juuresolevad kommentaarid?</label> <input type="radio" name="kajastus" value="meeldib"> Meeldib<input type="radio" name="kajastus" value="ei meeldi"> Ei meeldi <br>
                Postitad kommentaari ja annad hinnangu lehe <b>''','''
            <form method="POST">
                <textarea style="width:100%;height:120;resize:vertical" name="comment" placeholder="Your comment"></textarea>
                <label>Do you like the news?</label> <input type="radio" name="sisu" value="meeldib">Like<input type="radio" name="sisu" value="ei meeldi">Dislike<br>
                <label>Do you like presentation of the news?</label> <input type="radio" name="kajastus" value="meeldib">Like<input type="radio" name="kajastus" value="ei meeldi">Dislike<br>
                You are posting a comment and giving rating about page <b>''']
HTMLi_postitamise_osa_2=['''</b> kohta. <input type="submit" value="Postita''','''</b> . <input type="submit" value="Post''']
aeg=["aeg:","time:"]
hiljuti_kommenteeritud_lehed_tekst=["hiljuti kommenteeritud lehed","recently commented pages"]
parameeter_meeldib=["meeldib","liked"]
parameeter_ei_meeldi=["ei meeldi","disliked"]
parameeter_sisu=["sisu","content"]
parameeter_kajastus=["kajastus","presentation"]
parameeter_lehe=["Lehe <b>","There are no comments about page <b>"]
parameeter_kohta=['</b> kohta pole kommentaare. Kuvatud kommentaarid on lehe </b>',"</b>sown comments are about <b>"]
parameeter_kohta_2=["</b> kohta.</p>","</b></p>"]

viited={"static/reklaamid/ekre":"https://ekre.ee/",
        "static/reklaamid/uueduudised":"https://uueduudised.ee/",
        "static/reklaamid/SÄ":"https://ekre.ee/noored/",
        "static/reklaamid/SÄ2":"https://www.facebook.com/Sinine2ratus/",
        "static/reklaamid/SÄ3":"https://steamcommunity.com/groups/SinineAratus#members",
        "static/reklaamid/SÄ4":"https://sininearatus.ee/yritused/"}
kuva_reklaami=True
betale_lubatud_ipd=set()

def vii_URL_oigele_kujule(url):
    if not match(r"^(?:f|ht)tps?://", url):
        url="http://"+url
    www_asukoht=match(r"^(?:f|ht)tps?://www.", url)
    if www_asukoht:#kui aadressis on www. algus
        return ((url[:www_asukoht.end()-4]+url[www_asukoht.end():]).lower())#eemaldab URList "www."i
    return url.lower()

def pole_faile(url):
    for kommentaari_fail in sorted(os.listdir(url)):#kui ei sisalda ühtegi faili.
        if os.path.isfile(url+"/"+kommentaari_fail):
            return False
    return True

def vali_suvaline_fail(p="static/reklaamid"):
    try:
        p+="/"+(choice(os.listdir(os.path.join(os.path.dirname(__file__), p))))
        if os.path.isfile(os.path.join(os.path.dirname(__file__), p)):
            return (p,viited[p[:p.rfind("/")]])
        else:
            return vali_suvaline_fail(p)
    except IndexError:
        return vali_suvaline_fail()

@app.route('/')#suunab eestikeelsele pealehele
def ainult_domeen():
    return(redirect("/et"))

@app.route('/et', methods=['GET', 'POST'])
def pealeht_et():
    return pealeht(0)

@app.route('/eng', methods=['GET', 'POST'])
def pealeht_eng():
    return pealeht(1)

def pealeht(keel):
    if parameeter_kommenteeriava_URL[keel] in request.args:#Juhul kui päringus on sees URL, mida klient kommenteerida tahab. näiteks "http://objektiiv.ee/"
        kommentaaride_kaust=vii_URL_oigele_kujule(request.args[parameeter_kommenteeriava_URL[keel]])
        if parameeter_kommentaar[keel] in request.form:#juhul kui päringus on kommentaar, mida klient postitada tahab.
            hiljuti_kommenteeritud_lehtede_fail=open("hiljuti kommenteeritud lehed")
            hiljuti_kommenteeritud_lehed="".join(hiljuti_kommenteeritud_lehtede_fail.readlines()[1:])
            hiljuti_kommenteeritud_lehtede_fail.close()
            hiljuti_kommenteeritud_lehtede_fail=open("hiljuti kommenteeritud lehed","w")
            hiljuti_kommenteeritud_lehtede_fail.write(hiljuti_kommenteeritud_lehed+"\n"+kommentaaride_kaust.replace("<","&lt").replace("\r","").replace("\n"," "))#paneb lehe hiljuti kommenteeritud lehtede hulka
            hiljuti_kommenteeritud_lehtede_fail.close()
            hinnang=0# kui sisu hindamata: 0,1,2 ;kui sisu meeldib: 6,7,8; kui sisu ei meeldi 3,4,5
            # kui kajastus hindamata: 0,3,6 ;kui kajastus meeldib: 2,5,8; kui kajastus ei meeldi 1,4,7
            if parameeter_sisu_hinnang[keel] in request.form:
                if request.form[parameeter_sisu_hinnang[keel]]=="meeldib":
                    hinnang=6
                elif request.form[parameeter_sisu_hinnang[keel]]=="ei meeldi":
                    hinnang=3
                    # print(request.form[parameeter_sisu_hinnang[keel]])
            if parameeter_kajastuse_hinnang[keel] in request.form:
                if request.form[parameeter_kajastuse_hinnang[keel]]=="meeldib":
                    hinnang+=2
                elif request.form[parameeter_kajastuse_hinnang[keel]]=="ei meeldi":
                    hinnang+=1
                    #print(request.form[parameeter_kajastuse_hinnang[keel]])
            if os.path.exists(kommentaaride_kaust):
                if os.path.isfile(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP'))):#on vaja faili enne kommentaari reavahetus vaja panna.
                    if hinnang:#!=0
                        vana_hinnang=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP'))).readline()#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                        if vana_hinnang==hinnang:
                            #print("ei muuda hinnangut.")
                            f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"a")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                            f.write("\n"+str(datetime.now())+request.form[parameeter_kommentaar[keel]].replace("<","&lt").replace("\r","").replace("\n"," "))
                        else:
                            #print("uus hinnang on",hinnang,"vana sisu:",vana_hinnang)
                            vana_sisu=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP'))).read()[1:]
                            f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"w")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                            f.write(str(hinnang)+"\n"+vana_sisu[1:]+"\n"+str(datetime.now())+request.form[parameeter_kommentaar[keel]].replace("<","&lt").replace("\r","").replace("\n"," "))
                            del vana_sisu
                    else:
                        f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"a")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                        f.write("\n"+str(datetime.now())+request.form[parameeter_kommentaar[keel]].replace("<","&lt").replace("\r","").replace("\n"," "))
                    #print("fail olemas")
                else:
                    f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"a")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                    f.write(str(hinnang)+"\n"+str(datetime.now())+request.form[parameeter_kommentaar[keel]].replace("<","&lt").replace("\r","").replace("\n"," "))
                    #print("faili pole")
            else:#kui selle lehe kohta veel kommentaare ei ole.#ei ole vaja faili algusesse reavahetust.
                os.makedirs(kommentaaride_kaust)#teeb vastava kausta
                f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"a")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
                f.write(str(hinnang)+"\n"+str(datetime.now())+request.form[parameeter_kommentaar[keel]].replace("<","&lt").replace("\r","").replace("\n"," "))
            f.close()
        html=HTMLi_algus[keel]+HTMLi_postitamise_osa_1[keel]+kommentaaride_kaust+HTMLi_postitamise_osa_2[keel]+"""!">
            </form>"""
        vähendatud_URL=kommentaaride_kaust
        on_algne_url=True
        while not os.path.exists(vähendatud_URL) or pole_faile(vähendatud_URL):#alamprogramm pole_faile on juhuks kui kaust olemas, aga selle sees on on ainult kaustad mitte failid(kommentaarid)
            #print("url:",vähendatud_URL)
            if vähendatud_URL.count("/")<3:
                html+='<div style="background-color:lightgreen ; overflow-y: scroll ; height:130 ; resize:vertical">'+"<h4>"+kommentaare_ei_ole[keel]+"</h4>"
                html_2=""
                break
            vähendatud_URL=vähendatud_URL[:vähendatud_URL.rfind("/")]
            on_algne_url=False
        else:
            if on_algne_url:
                html+='<div style="background-color:#00FF00;width:100%;position:relative'
                if "kuva" in request.args:
                    html += ";overflow-y:scroll;height:170;resize:vertical"
                html+='">'
            else:
                html+='<div style="background-color:#CCCCCC;width:100%;position:relative'
                if "kuva" in request.args:
                    html+=";overflow-y:scroll;height:170;resize:vertical"
                #print("vähendatud:",vähendatud_URL)
                html+='">\n\t\t\t<p  style="position:relative;z-index:1">'+parameeter_lehe[keel]+kommentaaride_kaust+parameeter_kohta[keel]+vähendatud_URL+parameeter_kohta_2[keel]#Lisab lehele märke, et kommentaarid pole täpse URLi kohta.
            sisu_meeldimisi=0
            sisu_mitte_meeldimisi=0
            kajastuse_meeldimisi=0
            kajastuse_mitte_meeldimisi=0
            html_2=""
            for kommentaari_fail in sorted(os.listdir(vähendatud_URL)):#loeb failidest kommentaare, et need html'i panna, mis kliendile saadetakse.
                if os.path.isfile(vähendatud_URL+"/"+kommentaari_fail):
                    html_2+="""
                <div style="background-color:#b3e7ff;border:1px solid blue;width:99%;margin:0 auto;position:relative;z-index:1;max-height: 100vh;overflow-y:auto">
                    <h4>ip:"""+kommentaari_fail+"</h4>"
                    fail=open(vähendatud_URL+"/"+kommentaari_fail)
                    #LIKEDE LOENDAMINE
                    hinnang=int(next(fail))
                    if hinnang//3==2:
                        sisu_meeldimisi+=1
                        html_2+='<p style="font-size:12px;display:inline;margin-left:25px;line-height:0">'+parameeter_sisu[keel]+':</p><p style="font-size:12px;color:green;display:inline;line-height:0">'+parameeter_meeldib[keel]+'</p>'
                    elif hinnang//3==1:
                        sisu_mitte_meeldimisi+=1
                        html_2+='<p style="font-size:12px;display:inline;margin-left:25px;line-height:0">'+parameeter_sisu[keel]+':</p><p style="font-size:12px;color:red;display:inline;line-height:0">'+parameeter_ei_meeldi[keel]+'</p>'
                    if hinnang%3==2:
                        kajastuse_meeldimisi+=1
                        html_2+='<p style="font-size:12px;display:inline;margin-left:25px;line-height:0">'+parameeter_kajastus[keel]+':</p><p style="font-size:12px;color:green;display:inline;line-height:0">'+parameeter_meeldib[keel]+'</p>'
                    elif hinnang%3==1:
                        kajastuse_mitte_meeldimisi+=1
                        html_2+='<p style="font-size:12px;display:inline;margin-left:25px;line-height:0">'+parameeter_kajastus[keel]+':</p><p style="font-size:12px;color:red;display:inline;line-height:0">'+parameeter_ei_meeldi[keel]+'</p>'
                    html_2+="\n\t\t\t\t\t<h5>"
                    for kommentaar in fail:#paneb tühjade postituste ajad samale reale.
                        html_2+=aeg[keel]+kommentaar[:19]
                        if kommentaar[26:].strip("\n"):
                            html_2+="""</h5>\n\t\t\t\t\t<p>"""+kommentaar[26:].strip("\n")+"</p>\n\t\t\t\t\t<h5>"#paneb tarbetu realõpu kui [26:]. jätab viimase kommentaari viimase tähe ära kui [26:-1]
                        else:
                            html_2+=" ; "
                    fail.close()
                    html_2=html_2[:-5]+"</div><br>\n"
            if on_algne_url:
                try:
                    html_2+='\t\t\t\t<div style="position:absolute;top:0px;left:0px;background-color:#FF0000;width:'+str(int(100*sisu_mitte_meeldimisi/(sisu_meeldimisi+sisu_mitte_meeldimisi)))+'%;height:100%;z-index:0"><b>'+str(sisu_mitte_meeldimisi)+'</b></div>'
                    html+='\n\n<b style="z-index: 1;float:right">'+str(sisu_meeldimisi)+'</b><br>'
                    #print("sisu keskmine hinnang:",sisu_meeldimisi)
                except ZeroDivisionError:
                    #print("sisu pole hinnatud")
                    try:
                        #print("kajastuse keskmine hinnang:",kajastuse_meeldimisi/(kajastuse_meeldimisi+kajastuse_mitte_meeldimisi))
                        html_2+='\t\t\t\t<div style="position:absolute;top:0px;left:0px;background-color:#FF0000;width:'+str(int(100*kajastuse_meeldimisi/(kajastuse_meeldimisi+kajastuse_mitte_meeldimisi)))+'%;height:100%;z-index:0"><b>'+str(kajastuse_mitte_meeldimisi)+'</b></div>'
                        html += '\n\n<b style="z-index: 1;float:right">'+str(kajastuse_meeldimisi) + '</b><br>'
                    except ZeroDivisionError:
                        #print("kajastust pole hinnatud")
                        html_2+='\t\t\t\t<div style="position:absolute;top:0px;left:0px;background-color:lightgreen;width:100%;height:100%;z-index:0"></div>'
        html_2+='''
            </div>
        </div>'''
        if "kuva" in request.args:
            html_2+='<iframe src="'+kommentaaride_kaust+'" name="targetframe" allowTransparency="true" scrolling="yes" frameborder="0" width=100% height=100%><h4 style="color:red">'+browser_ei_toeta[keel]+'</h4></iframe>'#TODO:4)panna iframes´is tehtud clickid muutma kommenteeritavat URLi
        return (html+html_2+'''
        <script>document.getElementsByTagName("TEXTAREA")[0].value=document.cookie;document.body.onunload=function(){document.cookie=document.getElementsByTagName("TEXTAREA")[0].value};</script>
    </body>
</html>''')
    html=HTMLi_algus[keel]+"""
            <div style="background-color:#55aaff;border:1px solid white">
                <h5>"""+hiljuti_kommenteeritud_lehed_tekst[keel]+":</h5>"
    for i in open("hiljuti kommenteeritud lehed"):
        i=i.strip()
        html+="\n                <li><a href=\"http://www.kommentaarid.ee/et?kommenteeritava_URL="+i+"&kuva=on\">"+i+"</a></li>"
    if False:#request.headers.get('X-Real-IP') in betale_lubatud_ipd:#kuva_reklaami:
        path,url=vali_suvaline_fail()
        html+="""
            </div>
        </div>
        <div style="border: 5px groove yellow;margin-top:10px;display: inline-block;background-color:#DDDDDD">
            <p>reklaam</p>
            <a href=\""""+url+"\"><img src=\""+path+"""" height="300"></a>
        """
    else:
        html+="""
            </div>
        """#pealeht
    print(html)
    return html+"""</div>
    </body>
</html>"""

@app.route("/et/info")
def info_et():
    return """<html>
        <head>
            <title>Info universaalse kommentaariumi kohta</title>
        </head>
        <body>
            <div style="background-color:lightblue;border:4px solid black">
                <h1 style="display:inline">Info universaalse kommentaariumi kohta</h1><a style="display:inline;float:right" href="/eng/info">english</a>
                <p>Lehe www.kommentaarium.ee loomise eesmärk on pakkuda võimalust kommenteerida teisi internetilehekülgi(eelkõige mõeldud uudiste kommenteerimiseks). Teatavasti mitmed internetiportaalid ei paku endapoolt võimalust enda uudiste kommenteerimiseks, mõnedes neist peab kommenteerimiseks sisse logima, mõnedes kustutatakse anonüümsed kommentaarid automaatselt mingi aja möödudes(postimehes näiteks) ja mõnedes väidetavalt kustutakse kommentaare lähtuvalt nendes väljendatavast poliitilisest vaatest.</p>
            </div>
        </body>
        </html>"""
@app.route("/eng/info")
def info_eng():
    return """<html>
        <head>
            <title>About Universal commentary</title>
        </head>
        <body>
            <div style="background-color:lightblue;border:4px solid black">
                <h1 style="display:inline">About Universal commentary</h1><a style="display:inline;float:right" href="/et/info">eesti keel</a>
                <p>Purpous of creating webpage www.kommentaarium.ee is to offer oppurtunity to comment other webpages(especialy news). Many news portals do not offer commentary on theyr own page and on some you have to login to comment.</p>
            </div>
        </body>
        </html>"""

@app.route("/et/plugin/info")#/info võib URLi lopust ära võtta.
def plugina_info_et():
    return """<html>
    <head>
        <title>Universaalse kommentaariumi plugina kohta</title>
    </head>
    <body>
        <div style="background-color:lightblue;border:4px solid black">
            <h1 style="display:inline">Universaalse kommentaariumi plugina kohta</h1><a style="display:inline;float:right" href="/en/plugin/info">english</a>
            <p>plugin võimaldab www.kommentaarid.ee teenust mugavamini kasutada.</p>
        </div>
        <img src="/static/postimehe ja kommentaariumi plugina screenshot.png" alt="plugina kuvatommis" style="width:800px;height:500px;" border="2px">
        <img src="/static/youtube plugin eng screenshot.png" alt="plugina kuvatommis" style="width:900px;height:550px;" border="2px">
    </body>
</html>"""
@app.route("/en/plugin/info")#/info võib URLi lopust ära võtta.
def plugina_info_en():
    return """<html>
    <head>
        <title>About add-on of www.kommentaarid.ee</title>
    </head>
    <body>
        <div style="background-color:lightblue;border:4px solid black">
            <h1 style="display:inline">About add-on of www.kommentaarid.ee</h1><a style="display:inline;float:right" href="/et/plugin/info">eesti keel</a>
            <p>The add-on offers you a interface to post and read comments about pages, that you are visiting.</p>
        </div>
        <img src="/static/youtube plugin screenshot et.png" alt="screenshot of add-on" style="width:900px;height:550px;" border="2px">
    </body>
</html>"""

@app.route('/reklaam')
def miski():
    return render_template('reklaam/reklaam.html')

@app.route('/en/derivation')
def suvaline_pilt():
    return "<img src=\"/static/images/Figure1.jpg\" height=\"100%\">\n<img src=\"/static/images/Figure2.jpg\" height=\"100%\">"

@app.route('/portfelio')
def portfelio():
    return render_template('portfoolio/e-portfoolio.html')

"""@app.route('/betale',methods=["GET","POST"])
def render_static():
    global betale_lubatud_ipd
    if request.headers.get('X-Real-IP') in betale_lubatud_ipd:
        return(redirect("/"))
    if "salasona" in request.form:
        if request.form["salasona"]=="cdlijwdedwq":
            betale_lubatud_ipd.add(request.headers.get('X-Real-IP'))
            return (redirect("/"))
        else:
            return "vale salasõna"
    return render_template('/betale vorm.html')"""


@app.route("/plugin",methods=["GET"])
def plugina_data():
    if b"\n" in request.data:
        kommentaaride_kaust=vii_URL_oigele_kujule(request.data.split(b"\n",1)[0].decode("utf-8"))
        if os.path.exists(kommentaaride_kaust):
            f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')),"a")#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serveris on vaja str funktsiooni kasutatda?
            if os.path.isfile(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP'))):#on vaja faili enne kommentaari reavahetus vaja panna.
                f.write("\n"+str(datetime.now())+request.data.split(b"\n",1)[1].decode("utf-8").replace("<", "&lt").replace("\r","").replace("\n"," "))
            else:
                f.write(str(datetime.now())+request.data.split(b"\n",1)[1].decode("utf-8").replace("<", "&lt").replace("\r","").replace("\n"," "))
        else:#kui selle lehe kohta veel kommentaare ei ole.#ei ole vaja faili algusesse reavahetust.
            os.makedirs(kommentaaride_kaust)#teeb vastava kausta
            f=open(kommentaaride_kaust+"/"+str(request.headers.get('X-Real-IP')))#request.environ["REMOTE_ADDR"],jsonify({'ip': request.remote_addr},request.remote_addr,request.headers.get('X-Real-IP')#kas serceris on vaja str funktsiooni kasutatda?
            f.write(str(datetime.now())+request.data.split(b"\n",1)[1].decode("utf-8").replace("<", "&lt").replace("\r","").replace("\n"," "))
        f.close()
        return "1"
    else:
        kommentaarid=""
        kommentaaride_kaust=vii_URL_oigele_kujule(request.data.decode("utf-8"))
        if os.path.exists(kommentaaride_kaust):#kui selle lehe kohta on kommentaare.
            for kommentaari_fail in os.listdir(kommentaaride_kaust):#loeb failidest kommentaare, et need html'i panna, mis kliendile saadetakse.
                if os.path.isfile(kommentaaride_kaust+"/"+kommentaari_fail):
                    fail=open(kommentaaride_kaust+"/"+kommentaari_fail)
                    kommentaarid+=kommentaari_fail+"\n"+fail.read()+"\n\n"
                    fail.close()
        return Response(kommentaarid[:-1], mimetype='text/plain')

@app.route("/sissejuhatuse-projekt",methods=["GET","POST"])
def galerii():
    return render_template('index.html')
@app.route("/sissejuhatuse-projekt2",methods=["GET","POST"])
def galerii2():
    return render_template('galerii2.html')

if __name__ == '__main__':
    app.run()