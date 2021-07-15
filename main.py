from selenium.webdriver import Chrome
from selenium import webdriver

from datetime import datetime
from time import sleep

import pymysql
import pandas

##########################################################################################################

####################################
###          Constants           ###
####################################

file    = ".config"
content = open(file).read()
config  = eval(content)

DB_HOST                 = config['DB_HOST']
DB_PORT                 = int(config['DB_PORT'])
DB_USER                 = config['DB_USER']
DB_PASSWORD             = config['DB_PASSWORD']
DB_NAME                 = config['DB_NAME']
DB_TABLE_NAME           = config['DB_TABLE_NAME']
MAX_NUM_LINKS_BY_ONE    = int(config['MAX_NUM_LINKS_BY_ONE'])

HEAD_COLUMN_NAME        = config['HEAD_COLUMN_NAME']
HEAD_COLUMN_DESCRIPTION = config['HEAD_COLUMN_DESCRIPTION']
HEAD_COLUMN_LINK        = config['HEAD_COLUMN_LINK']
HEAD_COLUMN_PREVIEW     = config['HEAD_COLUMN_PREVIEW']

URL = 'https://tv.ivideon.com/'

##########################################################################################################

###########################################
###          Global variables           ###
###########################################

LINKS_ALREADY_IN_DB = set()

NEW_NAME_ITEMS          = []
NEW_DESCRIPTION_ITEMS   = []
NEW_LINKS_ITEMS         = []
NEW_PREVIEW_ITEMS       = []

##########################################################################################################

####################################################
###          Functions working with DB           ###
####################################################

def db_connect():
    try:
        connection = pymysql.connect(
            host        = DB_HOST,
            port        = DB_PORT,
            user        = DB_USER,
            password    = DB_PASSWORD,
            database    = DB_NAME,
            cursorclass = pymysql.cursors.DictCursor
            )

        print('Log info: [Connected to DB]')

    except Exception as ex:
        print(f'Error connect DB - [{ex}]')

    return connection

def db_get_links(connection):
    try:
        connection.commit()

        with connection.cursor() as cursor:
            show_query = "SELECT * FROM " + DB_TABLE_NAME + ";"
            cursor.execute(show_query)
            items = cursor.fetchall()
            for item in items:
                LINKS_ALREADY_IN_DB.add(item[HEAD_COLUMN_LINK])

    except Exception as ex:
        print(f'Error connect DB - [{ex}]')

def get_insert_query():
    query = "INSERT INTO " + DB_TABLE_NAME + f" ({HEAD_COLUMN_NAME}, {HEAD_COLUMN_DESCRIPTION}, {HEAD_COLUMN_LINK}, {HEAD_COLUMN_PREVIEW}) VALUES"

    for i in range(len(NEW_LINKS_ITEMS)):
        buff = " ("

        buff += "'" + str(NEW_NAME_ITEMS[i]).replace("'", "").replace('"', "")           + "', "
        buff += "'" + str(NEW_DESCRIPTION_ITEMS[i]).replace("'", "").replace('"', "")    + "', "
        buff += "'" + str(NEW_LINKS_ITEMS[i]).replace("'", "").replace('"', "")          + "', "
        buff += "'" + str(NEW_PREVIEW_ITEMS[i]).replace("'", "").replace('"', "")        + "')"

        if i != len(NEW_LINKS_ITEMS) - 1: buff += ","

        query += buff

    query += ";"
    return query

def db_add_links(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(get_insert_query())
            connection.commit()

    except Exception as ex:
        print(f'Error connect DB - [{ex}]')

def db_disconnect(connection):
    connection.close()

##########################################################################################################

##############################################
###          Main work functions           ###
##############################################

def log_info(text):
    currentTime = datetime.now().strftime('%H:%M:%S')
    print(f'Log info: [{text}] - Time: [{currentTime}]')

def connect():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    driver = Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(10)
    return driver

def go_to_url(url, driver):
    driver.get(url)
    return driver

def get_content_from_page(url):
    driver = connect()
    driver = go_to_url(url, driver)
    sleep(1)
    NEW_NAME_ITEMS.append(driver.find_element_by_class_name('b-video-title').text)
    NEW_DESCRIPTION_ITEMS.append(driver.find_element_by_class_name('b-video-description').text)
    driver.close()
    log_info(f'NAME - {NEW_NAME_ITEMS[-1]}')

def get_content(driver):
    sleep(5)
    items = driver.find_elements_by_class_name('b-camera-button')

    for item in items:
        link = item.get_attribute('href')
        if link not in NEW_LINKS_ITEMS and link not in LINKS_ALREADY_IN_DB: 
            NEW_LINKS_ITEMS.append(link)
            NEW_PREVIEW_ITEMS.append(item.find_element_by_class_name('b-image').find_elements_by_tag_name('img')[-1].get_attribute('src'))
            get_content_from_page(link)

    driver.find_element_by_class_name('b-right-button').click()
    if len(NEW_LINKS_ITEMS) >= 20: return
    get_content(driver)
    

##########################################################################################################


def main():
    db_conn = db_connect()
    db_get_links(db_conn)

    numBefore = len(LINKS_ALREADY_IN_DB)
    print(f"Log info: Links in DB - [{numBefore}]")

    driver = connect()
    driver = go_to_url(URL, driver)
    get_content(driver)


    db_add_links(db_conn)

    db_get_links(db_conn)
    numAfter = len(LINKS_ALREADY_IN_DB)

    db_disconnect(db_conn)

    driver.close()
    print('Log info: [End of parsing.]')
    print(f'Log info: [Loaded {len(NEW_LINKS_ITEMS)} items.]')
    print(f'Log info: [Links before: {numBefore}]')
    print(f'Log info: [Links after: {numAfter}]')
    
main()






