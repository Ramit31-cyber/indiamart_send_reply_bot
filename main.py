import logging
import os
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from difflib import SequenceMatcher

logging.basicConfig(filename='indiamart_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger('indiamart_bot')
service = Service('/home/ubuntu/chromedriver/chromedriver-linux64/chromedriver')
# service = Service(r"C:\Chrome Driver\chromedriver-win64\chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-dev-shm-usage')

prefs = {
    'safebrowsing.enabled': True
}

# Load .env variables
load_dotenv()

def get_new_key_dict():
    """Load NEW_KEY_DICT from the environment (JSON string).

    Expected format in .env:
    NEW_KEY_DICT='{"ot doors": ["Lead Lined Door", "Hospital OT Doors"], "pvc coving": ["pvc coving"]}'

    Returns a dict with lowercase keys. If parsing fails or env var missing,
    returns a fallback mapping (previous hardcoded mapping) and logs a warning.
    """
    new_key_dict_env = os.getenv('NEW_KEY_DICT')
    if new_key_dict_env:
        try:
            parsed = json.loads(new_key_dict_env)
            # Basic validation: must be a dict of lists of strings
            if not isinstance(parsed, dict):
                raise ValueError('NEW_KEY_DICT must be a JSON object mapping strings to lists')

            # Limits to avoid extremely large env payloads or accidental injection
            MAX_KEYS = 200
            MAX_TOTAL_VALUES = 2000
            MAX_STRING_LEN = 500

            if len(parsed) > MAX_KEYS:
                raise ValueError(f'NEW_KEY_DICT has too many keys ({len(parsed)})')

            total_values = 0
            validated = {}
            for k, v in parsed.items():
                if not isinstance(k, str):
                    raise ValueError('All NEW_KEY_DICT keys must be strings')
                if not isinstance(v, list):
                    raise ValueError(f'Value for key {k!r} must be a list')
                if len(k) > MAX_STRING_LEN:
                    raise ValueError(f'Key {k!r} too long')
                clean_vals = []
                for item in v:
                    if not isinstance(item, str):
                        raise ValueError('All items in NEW_KEY_DICT value lists must be strings')
                    if len(item) > MAX_STRING_LEN:
                        raise ValueError(f'Value string too long for key {k!r}')
                    clean_vals.append(item)
                total_values += len(clean_vals)
                validated[k.lower()] = clean_vals

            if total_values > MAX_TOTAL_VALUES:
                raise ValueError('NEW_KEY_DICT contains too many total values')

            return validated
        except Exception as e:
            logger.error(f'Failed to parse/validate NEW_KEY_DICT env var: {e}')


# Load mapping once (falls back to internal mapping inside function)
NEW_KEY_DICT = get_new_key_dict()
# Credentials from env (optional)
MOBILE_NUMBER = os.getenv('MOBILE_NUMBER', '9876543210')
PASSWORD = os.getenv('PASSWORD', 'abc@12345')

def extract_max_integer(item):
    digits = re.findall(r'\d+', item)
    if digits:
        return max(map(int, digits))
    else:
        return 0


def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def login():
    logger.info('Opening safebrowsing')
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.get('https://seller.indiamart.com/')
    user_id = driver.find_element(By.XPATH, '//*[@id="user_sign_in"]')
    user_id.click()
    mobile = driver.find_element(By.XPATH, '//*[@id="mobile"]')
    mobile.click()
    mobile.clear()
    mobile.send_keys(MOBILE_NUMBER)
    mob_submit = driver.find_element(By.XPATH, '//*[@id="logintoidentify"]')
    mob_submit.click()

    time.sleep(5)
    try:
        enter_pass = driver.find_element(By.XPATH, '//*[@id="passwordbtn1"]')
        enter_pass.click()
        time.sleep(2)
        enter_pass_txt = driver.find_element(By.XPATH, '//*[@id="usr_password"]')
        enter_pass_txt.click()
        time.sleep(2)
        enter_pass_txt.clear()
        enter_pass_txt.click()
        time.sleep(2)
        enter_pass_txt.send_keys(PASSWORD)

        submit_btn = driver.find_element(By.XPATH, '//*[@id="signWP"]')
        submit_btn.click()
    except Exception as err:
        print(f'Error2 is : {str(err)}')
        pass
    return driver

def main(driver, key_words, qnty):
    buy_leads = driver.find_element(By.XPATH, '//*[@id="lead_cen"]/a')
    buy_leads.click()
    time.sleep(10)

    try:
        allow_buy_leads = driver.find_element(By.XPATH, '//*[@id="optInText"]')
        logger.info('Allow detected')
    except:
        allow_buy_leads = None
        logger.info('Allow not detected')

    if allow_buy_leads:
        allow_buy_leads.click()
        logger.info('Allow clicked')

    buy_leads = driver.find_element(By.XPATH, '//*[@id="lead_cen"]/a')
    buy_leads.click()

    states = ["andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal", "andaman and nicobar islands", "chandigarh", "dadra and nagar haveli and daman and diu", "delhi", "jammu and kashmir", "ladakh", "lakshadweep", "puducherry" ]

    try:
        search_key_words = driver.find_element(By.XPATH, '//*[@id="search_string"]')
        search_key_words.click()
        search_key_words.clear()
        search_key_words.send_keys(key_words)
        search_key_words_enter = driver.find_element(By.XPATH, '//*[@id="btnSearch"]')
        search_key_words_enter.click()
        logger.info(f"Search for the '{key_words}'")
        time.sleep(10)
        try:
            suggest = driver.find_element(By.XPATH, "//span[@class='glob_sa_close']")
            suggest.click()
        except:
            pass

        leads = driver.find_elements(By.XPATH, '//*[@id="bl_listing"]')
        leads_list = []
        for l_txt in leads:
            leads_list.append(l_txt.text)
        count = leads_list[0].lower().count("contact buyer now")

        leads_xpaths = {}

        for j in range(1, count+1):
            lead_cur_xpath = f'//*[@id="list{j}"]/div[1]'
            lead_data = driver.find_element(By.XPATH, lead_cur_xpath).text
            leads_xpaths[lead_cur_xpath] = lead_data.split('\n')
        c = 0
        for xpath, lead in leads_xpaths.items():
            print(xpath)


            if any('Quantity' in item and extract_max_integer(item) >= qnty for item in lead) and \
                any(any(state.lower() in item.lower() for state in states) for item in lead[:4]) and \
                any(any(is_similar(key, word) for word in NEW_KEY_DICT.get(key_words.lower(), [])) for key in lead):

                logger.info(f'Lead data:\n{lead}')
                logger.info(f'Quantity in the leads is more than {qnty-1}')
                c+=1
                try:
                    cont_xpath = xpath.replace('/div[1]', '')
                    cont_buyer_xpath = f'{cont_xpath}/div[3]/div[2]/div/span'
                    contact_buyer = driver.find_element(By.XPATH, cont_buyer_xpath)
                    actions = ActionChains(driver)
                    actions.move_to_element(driver.find_element(By.XPATH, cont_buyer_xpath)).perform()
                    driver.execute_script("window.scrollBy(0, 200);")
                    contact_buyer.click()
                    logger.info(f"Lead XPATH: {xpath} and contact XPATH: {cont_buyer_xpath}")
                except:
                    cont_xpath = xpath.replace('/div[1]', '')
                    cont_buyer_xpath = f"{cont_xpath}//span[contains(text(),'Contact Buyer Now')]/ancestor::div[1]"
                    contact_buyer = driver.find_element(By.XPATH, cont_buyer_xpath)
                    actions = ActionChains(driver)
                    actions.move_to_element(driver.find_element(By.XPATH, cont_buyer_xpath)).perform()
                    driver.execute_script("window.scrollBy(0, 200);")
                    contact_buyer.click()
                    logger.info(f"Lead XPATH: {xpath} and contact XPATH: {cont_buyer_xpath}")

                try:
                    send_reply = driver.find_element(By.XPATH, "//*[text()='Send Reply']")
                    send_reply.click()
                    logger.info('Clicked on send reply')
                    try:
                        element_or_outer_popup = driver.find_element(By.XPATH, '//*[@id="cls_btn"]')
                        element_or_outer_popup.click()
                        logger.info('Closeing the popup')
                        pass
                    except:
                        logger.info('Unable to close the popup')
                        pass
                except:
                    send_reply = None
                    logger.info('Unable to click on send reply')
                if send_reply:
                    time.sleep(10)
                    try:
                        popup = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "rr_outer")))
                        element_inside_popup = popup.find_element(By.XPATH, "//div[@id='rr_outer']/div[1]")
                        element_inside_popup.click()
                        popup_2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="innerPopup_suggested_BL"]/span')))
                        element_inside_popup_2 = popup_2.find_element(By.XPATH, '//*[@id="innerPopup_suggested_BL"]/span')
                        element_inside_popup_2.click()
                    except:
                        pass

    except Exception as err:
        print(str(err))
        logger.info(f'Error at main function, Error: {str(err)}')


def run_bot():
    # Try to load keywords and quantities from environment. Support JSON arrays or comma-separated values.
    def _parse_env_list(var_name, cast=None, default=None):
        raw = os.getenv(var_name)
        if not raw:
            return default
        # Try JSON first
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                if cast:
                    return [cast(x) for x in parsed]
                return parsed
        except Exception:
            # Fall back to comma-separated
            parts = [p.strip() for p in raw.split(',') if p.strip()]
            if cast:
                try:
                    return [cast(p) for p in parts]
                except Exception as e:
                    logger.error(f'Failed to cast items in {var_name}: {e}')
                    return default
            return parts

    keywords_list = _parse_env_list('KEYWORDS_LIST', cast=str, default=[])
    quantities_list = _parse_env_list('QUANTITIES_LIST', cast=int, default=[])

    if not keywords_list or not quantities_list:
        logger.warning('KEYWORDS_LIST or QUANTITIES_LIST is empty; using defaults where necessary')

    if len(keywords_list) != len(quantities_list):
        logger.warning(f'KEYWORDS_LIST length ({len(keywords_list)}) != QUANTITIES_LIST length ({len(quantities_list)}). The zip will use the shorter length.')
    driver = login()
    logger.info('Log in to indiamart portal')
    time.sleep(5)
    for i in range(1,151):
        logger.info(f"Main cycle no: '{i}'")
        print(f"Main cycle no: '{i}'")
        for keywords, quantities in zip(keywords_list, quantities_list):
            print(keywords)
            time.sleep(10)
            main(driver=driver, key_words=keywords, qnty=quantities)
        time.sleep(60)
    try:
        try:
            driver.close()
        except:
            driver.quit()
    except:
        pass


while True:
    try:
        run_bot()
    except Exception as er:
        logger.info(str(er))
        print('Please check logger')
