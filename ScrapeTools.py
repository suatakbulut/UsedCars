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
        MSRP = msrp.replace(",", "")
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
            headers = {"user-agent": MOBILE_USER_AGENT}
        else:
            headers = {"user-agent": USER_AGENT}

        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, 'lxml')
        text = str(soup.find("div", attrs={"class": "xpdopen"}))
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

        start = urlSoup.find(lambda tag: tag.name ==
                             'h2' and 'model line' in tag.text.lower())
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


def scrape_reviews(car_name):
    # format should be 'make-model-year', e.g. 'honda-accord-2014'
    url = f'https://www.cars.com/research/{car_name}/consumer-reviews/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, "lxml")
    # focus on the summary div
    summary = soup.find("div", attrs={"class": "summary-container"})

    # overall star score
    score = summary.find("span", attrs={"class": "sds-rating__count"}).text

    # number reviews
    rev_count = summary.find(
        "a", attrs={"class": "sds-rating__link sds-button-link"}).text
    num_reviews = "".join([ch for ch in rev_count if ch.isdigit()])

    # Recommendation rate, e.g. '65% of drivers recommend this car'
    recommendation_rate = summary.find(text=re.compile('recommend'))

    # Recommendation Breakdown
    breakdown = summary.find(
        "ul", attrs={"class": "sds-definition-list review-breakdown--list"})
    breakdown_map = {}
    details = [det for det in breakdown.text.split("\n") if det]
    for i in range(len(details)//2):
        breakdown_map[details[2*i]] = details[2*i+1]

    reviews = {
        "score": score,
        "num_reviews": num_reviews,
        "recommendation_rate": recommendation_rate,
        "breakdown_map": breakdown_map
    }
    return reviews


def scrape_complaints(manufacturer, model, year, numComplaints=6):
    manufacturer = manufacturer.title() 
    model = model.title() 
    try:
        url = f'https://www.carcomplaints.com/{manufacturer}/{model}/{year}/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        urlSoup = BeautifulSoup(response.content, "lxml")
        container = urlSoup.find("div", attrs={"id": "graph"})
        complaints_list = container.ul.findAll('li')
        return [complaints_list[ind].strong.text.capitalize() for ind in range(min(len(complaints_list), numComplaints))]

    except:
        print('Could not retreive complaints. . Error with Car.complaints() method.')
        return ['No mechanical issues retrieved']


if __name__ == '__main__':
    car1 = '2018-toyota-camry'
    car2 = '2012-ford-focus'
    for car in (car1, car2):
        print(scrape_NewCarsTestDrive(car))
        print(scrape_GoogleSearch(car))
