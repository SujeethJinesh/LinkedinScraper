import argparse, time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from Internship import Internship


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="linkedin email")
    parser.add_argument("password", help="linkedin password")
    return parser.parse_args()


def open_incognito_window():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

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


def get_people_list(driver):
    import ipdb; ipdb.set_trace()
    return driver.find_element_by_xpath("//ul[@class='results-list ember-view']/li*") #.find_elements_by_tag_name("li")


def main():
    # parse args
    args = parse_args()

    # open incognito window
    driver = open_incognito_window()

    # login
    login(driver, "https://www.linkedin.com/uas/login", args)

    # go to GT page
    driver.get("https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223558%22%5D")

    # get list of people from page
    people_list = get_people_list(driver)
    actions = ActionChains(driver)

    # open each member in a new tab
    for person_profile in people_list:
        person_element = person_profile.find_element_by_xpath("//a[@class='search-result__result-link ember-view']")  # Error is here, for some reason it won't click on the <a> tag attached to that class
        actions.key_down(Keys.COMMAND).click(person_element).key_up(Keys.CONTROL).perform()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(5)

        experience_list = driver.find_elements_by_xpath(
            "//ul[@class='pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more']")

        software_internships_list = []
        for experience in experience_list:
            print("in experience list")
            list_elements = experience.find_elements_by_tgag_name("li")
            for list_element in list_elements:
                job_title, _, company, _, date, _, _ = list_element.find_element_by_class_name('pv-entity__summary-info').text.split("\n")
                if "software" in job_title.lower() and ("intern" in job_title.lower() or "internship" in job_title.lower()):
                    start_date = date.split("–")[0].strip()
                    end_date = date.split("–")[1].strip()
                    internship = Internship(job_title, company, start_date, end_date)
                    software_internships_list.append(internship)
                    print("Job title: ", job_title, ", Company: ", company)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(5)
    # import ipdb;
    # ipdb.set_trace()
    driver.close()


if __name__ == '__main__':
    main()
