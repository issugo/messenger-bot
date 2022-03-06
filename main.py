from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from bs4.element import ResultSet as bs4ResultSet
from fbchat.models import *
from datetime import datetime
import os
import time


load_dotenv()

my_thread_id = 100013619768121
conv_thread_id = 2602345713216132

previous_message = ""
previous_sender = ""
victor_pseudo = "pd"


def xpath_soup(_element):
    """
    Generate xpath from BeautifulSoup4 element.
    :param element: BeautifulSoup4 element.
    :type element: bs4.element.Tag or bs4.element.NavigableString
    :return: xpath as string
    :rtype: str
    Usage
    -----
    >>> import bs4
    >>> html = (
    ...     '<html><head><title>title</title></head>'
    ...     '<body><p>p <i>1</i></p><p>p <i>2</i></p></body></html>'
    ...     )
    >>> soup = bs4.BeautifulSoup(html, 'html.parser')
    >>> xpath_soup(soup.html.body.p.i)
    '/html/body/p[1]/i'
    >>> import bs4
    >>> xml = '<doc><elm/><elm/></doc>'
    >>> soup = bs4.BeautifulSoup(xml, 'lxml-xml')
    >>> xpath_soup(soup.doc.elm.next_sibling)
    '/doc/elm[2]'
    """
    components = []
    child = _element if _element.name else _element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def check_pseudo_change():
    global victor_pseudo
    rows = previous_soup.find_all("div", {"role": "row"})
    actual_row = rows[len(rows) - 1]
    if len(list(actual_row.descendants)) == 5:
        print("new pseudo detected")
        if victor_pseudo in actual_row.text or "Victor" in actual_row.text:
            print("victor changed pseudo")
            txt = actual_row.text.split()
            new_pseudo = []
            new_pseudo_start = False
            for word in txt:
                if new_pseudo_start:
                    new_pseudo.append(word)
                if word == "sur":
                    new_pseudo_start = True
            victor_pseudo = " ".join(new_pseudo)[:-1]
            print("victor new pseudo :", victor_pseudo)
        return True
    else:
        return False


def check_new_message():
    global previous_message
    message = previous_soup.find_all("div", {"data-testid": "message-container"})
    if message[len(message) - 1].parent.previous_sibling.text != "Vous avez envoyé":
        if previous_message == message[len(message) - 1].text:
            previous_message = message[len(message) - 1].text
            return False
        else:
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "new message")
            previous_message = message[len(message) - 1].text
            return True


def check_sender():
    global previous_sender
    sender = previous_soup.find_all("div", {"data-testid": "mw_message_sender_name"})
    sender_name = sender[len(sender) - 1].text
    
    if sender_name == previous_sender:
        previous_sender = sender_name
        return False
    else:
        previous_sender = sender_name
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sender_name)
        return True


def check_html_change():
    html = wd.page_source
    soup = BeautifulSoup(html, features="html.parser")
    global previous_soup
    if (previous_soup == soup):
        previous_soup = soup
        return False
    else:
        previous_soup = soup
        return True


def send_message(_message):
    time.sleep(5)
    html = wd.page_source
    soup = BeautifulSoup(html, features="html.parser")
    input_message = soup.find("div", {"aria-label": "Écrire un message"})
    #wd.find_element(By.XPATH, xpath_soup(input_message)).click()
    webdriver.ActionChains(wd).send_keys(_message).perform()
    webdriver.ActionChains(wd).send_keys(Keys.ENTER).perform()


def get_conv(_threadId):
    if type(_threadId) is not int:
        wd.close()
        raise TypeError("_threadId is not un valid number")
    wd.get("https://www.messenger.com/t/%s" % (str(_threadId)))
    time.sleep(5)


def connect(_username, _password):
    '''
    connect user to GlobalExam

            Parameters:
                    username (string): username to connect to global exam
                    password (string): password to connect to global exam

            Returns:
                    None
    '''
    if type(_username) is not str:
        wd.close()
        raise TypeError("username is not a string")
    if type(_password) is not str:
        wd.close()
        raise TypeError("password is not a string")
    html = wd.page_source
    soup = BeautifulSoup(html, features="html.parser")
    accept_CGU = soup.find("button", text="Tout accepter")
    wd.find_element(By.XPATH, xpath_soup(accept_CGU)).click()
    wd.find_element(By.XPATH, '//input[@id="email"]').send_keys(_username)
    wd.find_element(By.XPATH, '//input[@id="pass"]').send_keys(_password)
    WebDriverWait(wd, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="loginbutton"]')))
    wd.find_element(By.XPATH, '//*[@id="loginbutton"]').click()
    WebDriverWait(wd, 30).until(EC.url_contains("https://www.messenger.com/t/"))


def launch_firefox():
    """
    launch firefox through webdriver

            Returns:
                    None
    """
    global wd
    wd = webdriver.Firefox()
    wd.get('https://www.messenger.com/login/')


def run():
    launch_firefox()
    connect(os.getenv('FACEBOOK_USERNAME'), os.getenv('FACEBOOK_PASSWORD'))
    get_conv(conv_thread_id)
    global previous_soup
    global previous_message
    global previous_sender
    global victor_pseudo
    html = wd.page_source
    previous_soup = BeautifulSoup(html, features="html.parser")
    while True:
        if check_html_change():
            check_pseudo_change()
            if check_new_message() and check_sender():
                print(previous_message)
                if previous_sender == victor_pseudo:
                    send_message("tu es nul victor")
                if ("pd" in previous_message) or ("Pd" in previous_message) or ("pD" in previous_message) or ("PD" in previous_message):
                    print("voila")
                    send_message("c'est toi t'es PD")
                if ("null" in previous_message) or ("Null" in previous_message):
                    send_message("c'est toi t'es null")
        time.sleep(1)


def debug():
    print(os.getenv('FACEBOOK_USERNAME'))
    print(os.getenv('FACEBOOK_PASSWORD'))


if __name__ == '__main__':
    run()