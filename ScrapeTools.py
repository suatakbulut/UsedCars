import requests
from bs4 import BeautifulSoup
import re

def extract_msrp(text):
    """
    Finds subtexts that match the pattern, sorts it, and returns the middle value. 
    Otherwise, it returns None
    """
    pattern = re.compile(r"\$\d+[,]\d\d\d")
    try:
        result = pattern.findall(text)
        result = sorted(result)
        msrp = result[len(result)//2]
        MSRP = msrp.replace(",","")
        return MSRP[1:] 
    except:
        return None

def scrape_GoogleSearch(CarName, mobile=True): 
    """ 
    Takes a string formatted as maker-model-year.
    If google.com/search has the MSRP value in the first main div block called g.mnr-c.g-blk
    Returns a string: CarName, CarMSRP
    """
    try:
        car = CarName.replace("-", "+")
        car = car.replace(" ", "+")
        query = "+".join([car, "msrp"])
        url = "https://google.com/search?q=<{}>".format(query) 
        # desktop user-agent
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        # mobile user-agent
        MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36"
        
        if mobile:
            headers = {"user-agent" : MOBILE_USER_AGENT}
        else:
            headers = {"user-agent" : USER_AGENT}
            
        resp = requests.get(url, headers=headers)   
        soup = BeautifulSoup(resp.content, 'lxml')
        text = str(soup.find("div", attrs={"class":"xpdopen"})) 
        carMSRP = extract_msrp(text) 
        if carMSRP:
            line = ",".join([CarName, carMSRP]) + "\n"
            return line
    except:
        pass

def scrape_NewCarsTestDrive(CarName):
    """ 
    Takes a string formatted as maker-model-year.
    If newcartestdrive.com/reviews has the MSRP value, 
    Returns a line of string: CarName, CarMSRP
    """
    try:
        url = "https://www.newcartestdrive.com/reviews/{}/".format(CarName)
        response = requests.get(url)
        urlSoup = BeautifulSoup(response.content, "lxml")
        
        start = urlSoup.find(lambda tag: tag.name == 'h2' and 'model line' in tag.text.lower())
        end = start.findNext("h2")
        item = start.nextSibling
        text = ''
        while item != end: 
            text += str(item) 
            item = item.nextSibling
        
        carMSRP = extract_msrp(text)
        line = ",".join([CarName, carMSRP]) + "\n" 
        return line
    except:
        pass

if __name__ == '__main__': 
    car1 = '2018-toyota-camry'
    car2 = '2012-ford-focus'
    for car in (car1, car2):
        print(scrape_NewCarsTestDrive(car))
        print(scrape_GoogleSearch(car))
    
    