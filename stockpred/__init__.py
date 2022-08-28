
from flask import Flask ,render_template ,request
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pickle
import os 


PATH  = os.path.join(os.path.dirname(__file__), 'model.pkl')
CPATH = os.path.join(os.path.dirname(__file__), 'chromedriver')
print(PATH)
app = Flask(__name__)
model = None
with open(PATH,'rb') as pickle_file:
    model = pickle.load(pickle_file)

@app.route('/')
def index():
    """
    index 함수에서는 'simple_flask_app/templates' 폴더에 있는 'index.html'
    파일을 렌더링 해줘야 합니다!
    """
    return render_template("main/main.html"), 200

@app.route("/predict")
def predict () : 
    driver = webdriver.Chrome(CPATH)
    driver.get(f"https://finance.naver.com/item/frgn.naver?code=122630&page=1")
    html =driver.page_source
 
    soup = BeautifulSoup( html , 'html.parser')
    soup = soup.select_one("#content > div.section.inner_sub > table.type2 > tbody")
    newlist = []
    for ind, contents in  enumerate(soup.find_all("span") ): 
        newlist.append(contents.text.strip())
        if ind == 8 : 
            break 
    day = newlist.pop(0)
    del newlist[1]
    del newlist[1]
    
    ss ="*".join(newlist) 
    ss = ss.replace(",","")
    ss = ss.replace("%","")
    ss = ss.replace("+","")
    newlist = ss.split("*")
    
    for i, con  in enumerate(newlist ): 
        if  i==5  : 
            newlist[i] = float(newlist[i])
        else : 
            newlist[i] = int(newlist[i])


    url = f"https://finance.naver.com/sise/sise_deposit.naver?&page=1"
    
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    page1 = []

    for i in  soup.find("table").find_all("tr") : 
        
        for j in i.find_all("td") :
            if j["class"][0] == "rate_down" : 
                page1.append(("-"+j.text).replace(",",""))
            else : 
                page1.append((j.text).replace(",",""))
    
    p = "/".join(page1)     # 음수 조정 필요  (증시자금 동향 )
    p = p.split("/")[1:12]
    

    ex_p = list(map(int, p[1:]))
    ex_p.insert(0, p[0])

    for  i in range(1,10,2) : 
        ex_p[i] = ex_p[i] * -1
    del ex_p[0] 

    newlist.extend(ex_p)
    
    if model.predict([newlist])[0] == 1 : 
        result = "오늘은 빨간불의 기운이 강합니다." 
    else : 
        result = "오늘은 파란불의 기운이 강합니다. "
    
    return  render_template("main/predict.html" , result = result, day =day ) , 200 


@app.route("/manual", methods = ["POST","GET"])
def manual_pred () :
    if request.method == 'POST':
        formdata = request.form
        input1 = [list(formdata.values())]
        if model.predict(input1)[0] == 1 : 
            result = "입력값은 빨간불의 기운이 강합니다." 
        else : 
            result = "입렵값은 파란불의 기운이 강합니다. "
        
    return result




         
if __name__ == "__main__":
    app.run(debug=True)

