import argparse
import time
import pickle
import sys

from selenium import webdriver
from scrape_linkedin import Scraper


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="linkedin email")
    parser.add_argument("password", help="linkedin password")
    return parser.parse_args()


def open_incognito_window():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-fullscreen")

    return webdriver.Chrome(chrome_options=chrome_options)


def login(driver, link, args):
    driver.get(link)

    emailElement = driver.find_element_by_id("session_key-login")
    emailElement.send_keys(args.email)

    passwordElement = driver.find_element_by_id("session_password-login")
    passwordElement.send_keys(args.password)
    passwordElement.submit()

    # wait for loading
    time.sleep(4)


def scroll_to_bottom_infinitely(driver):
    scheight = .1
    while scheight < 9.9:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
        scheight += .01


def get_people_list(driver):
    scroll_to_bottom_infinitely(driver)
    time.sleep(2)
    return driver.find_elements_by_xpath("//a[@class='search-result__result-link ember-view']")


def scrape_page(driver):
    # get list of people
    people_list = get_people_list(driver)

    if len(people_list) < 20:
        people_list = get_people_list(driver)  # try again, yolo
    
    candidates = [] #TODO: might want to only look at people who were students and didn't just work for GT, as well as only software engineer interns
    with Scraper() as scraper:
        for i, person in enumerate(people_list):
            if i * 2 + 1 < len(people_list):
                url = people_list[i * 2 + 1].get_attribute("href")  # some hacky shit cause there are two of the same classes per profile
                candidate = scraper.get_profile(url)
                candidates.append(candidate)
    return candidates


def advance_page(driver):
    driver.find_element_by_xpath("//button[@class='next']").click()


def main():
    # pickling can't go more than certain sys requirements
    sys.setrecursionlimit(100000)

    # parse args
    args = parse_args()

    # open incognito window
    driver = open_incognito_window()

    # login
    login(driver, "https://www.linkedin.com/uas/login", args)

    # go to GT page
    driver.get("https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223558%22%5D")

    candidates = []
    page = 1
    for page_number in range(2):  # TODO: Change this to ~1100 if scraping for all GT students
        try:
            candidates += scrape_page(driver)
            with open("saves/save-page-{}.p".format(str(page)), "wb") as save_file:
                pickle.dump(candidates, save_file)
            page += 1
            advance_page(driver)
        except:
            # in case of failure, we'll at least recover some data.
            with open("saves/save-page-{}-error.p".format(str(page)), "wb") as error_file:
                pickle.dump(candidates, error_file)
            import ipdb;
            ipdb.set_trace()

    with open("saves/save-page-{}-complete.p".format(str(page)), "wb") as complete_file:
        pickle.dump(candidates, complete_file)

    import ipdb;
    ipdb.set_trace()
    driver.close()


if __name__ == '__main__':
    main()
