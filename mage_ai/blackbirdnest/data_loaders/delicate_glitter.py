from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def search_google(query):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")

    # Connect to the remote web driver
    driver = webdriver.Remote(
        command_executor="http://host.docker.internal:4444", 
        options=chrome_options
    )

    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    
    sessionid =driver.session_id
    print(sessionid)
    
    # driver.quit()
    return sesionid

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here
    query = 'Chat GPT 4'
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")

    # Connect to the remote web driver
    driver = webdriver.Remote(
        command_executor="http://host.docker.internal:4444", 
        options=chrome_options
    )

    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    
    sessionid =driver.session_id
    print(sessionid)
    
    
    print(f"http://host.docker.internal:4444/grid/api/testsession?session={sessionid}")
    return {'gpt': sessionid}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'