
import logging
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from tenacity import retry, Retrying, stop_after_attempt, wait_fixed
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

REPORT_CHECK_LOOP_ERROR_COUNT = 3 # number of tries to find the report
REPORT_CHECK_LOOP_INTERVAL = 5 # seconds
REPORT_CHECK_MAX_WAIT = 600  # max time to wait for report to finish in seconds
REPORT_WAIT_LOOP_COUNT = int(REPORT_CHECK_MAX_WAIT/REPORT_CHECK_LOOP_INTERVAL)
LOAD_CLOSED_BILLS_WAIT = 2
LOAD_CLOSED_BILLS_RETRY = 5



class ReportNotFound(Exception):
    if hasattr(Exception,'message'):
        error_message = Exception.message
    else:
        error_message = Exception
    logger.error('Report not found: {}'.format(error_message))

class ReportNotCompleted(Exception):
    if hasattr(Exception,'message'):
        error_message = Exception.message
    else:
        error_message = Exception
    logger.error('Report not found: {}'.format(error_message))

class LoginError(Exception):
    if hasattr(Exception,'message'):
        error_message = Exception.message
    else:
        error_message = Exception
    logger.error('Login error: {}'.format(error_message))

def my_before_sleep(retry_state):
    if retry_state.attempt_number < 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING
    logger.log(
        loglevel, 'Retrying %s: attempt %s ended with: %s',
        retry_state.fn, retry_state.attempt_number, retry_state.outcome)

class HighRadius(object):
    def __init__(self, username=None,  password=None, **kwargs):
        self.browser = webdriver.Remote("http://localhost:4444/wd/hub",options=set_chrome_options())
        self.report_check_loop_error_count = kwargs.get('report_check_loop_error_count', REPORT_CHECK_LOOP_ERROR_COUNT)
        self.report_check_loop_interval = kwargs.get('report_check_loop_error_count', REPORT_CHECK_LOOP_INTERVAL)
        self.report_check_max_wait = kwargs.get('report_check_loop_error_count', REPORT_CHECK_MAX_WAIT)
        self.report_check_loop_error_count = kwargs.get('report_check_loop_error_count', int(self.report_check_max_wait/self.report_check_loop_interval))
        self.load_closed_bills_wait = kwargs.get('load_closed_bills_wait',LOAD_CLOSED_BILLS_WAIT)
        self.load_closed_bills_retry = kwargs.get('load_closed_bills_retry',LOAD_CLOSED_BILLS_RETRY)
        self.browser.get("https://walmart.highradius.com")
        if not username==None and not password==None:
            self.login(username=username,password=password)
    def login(self,username=None, password=None):
        self.browser.get("https://walmart.highradius.com")
        username_field = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.NAME,"username"))
        self.browser.execute_script(f"arguments[0].value='{username}';", username_field)
        # username_field.send_keys(username)
        password_field = self.browser.find_element(By.NAME,"password")
        self.browser.execute_script(f"arguments[0].value='{password}';", password_field)
        password_field.click()
        # password_field.send_keys(password)
        signin_button = self.browser.find_element(By.XPATH,"//a[.//span[@signin='Sign In']]")
        signin_button.click()
    def check_login_error(self):
        login_error = ''
        if self.browser.current_url == 'https://walmart.highradius.com/RRDMSProject/signin.do':
            login_error = self.browser.find_elements(By.XPATH,'//div[contains(@class,"formdiv-errorTip")]')
            login_error = ' '.join([l.text.removeprefix('Error').strip() for l in login_error])
            if login_error == '':
                alert_box = self.browser.find_elements(By.XPATH,'//div[contains(@class,"x-message-box")][@role="alertdialog"]')
                login_error = ' '.join([l.text.removeprefix('Error').strip() for l in alert_box])
        if len(login_error)>0:
            return login_error
        else:
            return 'OK'

    def download_all_closed_bills(self,export_name=None):
        retryer_load_closed_bills = Retrying(reraise=True, wait=wait_fixed(self.load_closed_bills_wait), stop=stop_after_attempt(self.load_closed_bills_retry), before_sleep=my_before_sleep)
        records_found = retryer_load_closed_bills(self._load_closed_bills)
        if records_found == "No":
            logger.warning('No records loaded')
            report_status = {'status': 'No Records', 'record_count':"0"}

        else:
            self._closed_bills_export_submit(export_name=export_name)
            report_status = {'status': 'Pending'}
            retryer = Retrying(reraise=True, wait=wait_fixed(self.report_check_loop_interval), stop=stop_after_attempt(self.report_check_loop_error_count), before_sleep=my_before_sleep)
            try:
                report_status = retryer(self.check_report_status,export_name=export_name)
                if report_status['status'] != 'Success':
                    retryer_found_report = Retrying(reraise=True, wait=wait_fixed(self.report_check_loop_interval), stop=stop_after_attempt(self.report_wait_loop_count), before_sleep=my_before_sleep)
                    report_status = retryer_found_report(self.check_report_status, export_name=export_name)            
            except Exception as e:
                logger.log(e)
                pass

        return report_status


        
    def _load_closed_bills(self):
        # wait for the EIPP tab to show up
        if self.browser.current_url == 'https://walmart.highradius.com/RRDMSProject/signin.do':
            login_error = self.check_login_error()
            if login_error != 'OK':
                raise LoginError(login_error)
        eipp = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//a//span//span//span[contains(text(),'EIPP')]"))
        eipp.click()

        closedbills = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//a//span//span//span[contains(text(),'Closed Bills')]"))
        # closedbills = e.find_element(By.ID,"tab-1528")
        closedbills.click()
        # wait for loading div to hide
        status_mask = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[contains(@autoid,'IDClosedBills')]//div[@role='status'][@style='display: none;']"))
        try:
            first_record = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[contains(@autoid,'IDClosedBills')]//table[@data-recordindex='0']"))
            return "Ok"
        except:
            return "No"

    def _closed_bills_export_submit(self,  export_name=None):

        closed_bills_div = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[contains(@autoid,'IDClosedBills')]"))        

        export_drop = closed_bills_div.find_element(By.XPATH,".//*[contains(@aria-label,'Export')]")
        export_drop.click()

        export_all_divs =  WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[@autoid='802:4237:exportAll']"))
        export_all_divs.click()

        export_all_form =  WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[@aria-hidden='false'][@role='dialog']"))
        export_name_field = export_all_form.find_element(By.NAME, "exportName")        
        self.browser.execute_script(f"arguments[0].value='{export_name}';", export_name_field)
        export_name_field.click()
        # export_name_field.send_keys(f"{export_name}")

        xlsx_radio = export_all_form.find_element(By.XPATH,".//div/label[text()='EXCEL (XLSX)']")
        xlsx_radio.click()

        xlsx_submit = export_all_form.find_element(By.XPATH,".//a[@aria-label='Submit']")
        xlsx_submit.click()

    
    def check_report_status(self,export_name=None, report_filters=None):
        """
        Allowed  report filters dict would be in this format:
        {
            "Export Id":  "131232",  
            "Export Name": "Some Report Name",  
            "Export Time After": "2023-08-01 02:27:48",  
            "Export Time Before": "2023-08-08 02:27:48",  
            "File Type": ["xlsx","xls"],  
            "Record Count GT": 0,  
            "Status": ["Success", "Job  Submitted"]  
        }
        """
        jobs_panel = WebDriverWait(self.browser,20).until(lambda x: x.find_element(By.XPATH,"//div[@autoid='IDExports']"))
        table_headers = jobs_panel.find_elements(By.XPATH, ".//span[@class='x-column-header-text-inner']")
        table_header_names = [x.text for x in table_headers]

        # exports_table = WebDriverWait(jobs_panel,20).until(lambda x: x.find_element(By.TAG_NAME,"table"))
        table_rows = WebDriverWait(jobs_panel,20).until(lambda x: x.find_elements(By.XPATH,".//table//tr"))
        
        export_name_column_index = table_header_names.index("Export Name")
        existing_reports = []
        for table_row in table_rows:
            row_cells = table_row.find_elements(By.TAG_NAME,"td")
            if row_cells[export_name_column_index].text == str(export_name):
                if row_cells[table_header_names.index("Status")].text.strip() == "Success":
                    report_record_count = row_cells[table_header_names.index("Record Count")].text
                    if int(report_record_count) == 0:
                        self.report_status = {
                            "status": "Success",
                            "record_count": 0,
                        }
                        return self.report_status
                    row_cells[table_header_names.index("File Path")].find_element(By.TAG_NAME,"a").click()
                    self.report_status = {
                        "status": "Success",
                        "record_count": report_record_count
                    }
                    return self.report_status
                else:
                    return row_cells[table_header_names.index("Status")].text.strip()
            existing_reports.append(
                {
                    "report_name": row_cells[export_name_column_index].text,
                    "report_date": row_cells[table_header_names.index("Export Time")].text,
                    "record_count": row_cells[table_header_names.index("Record Count")].text,
                    "status": row_cells[table_header_names.index("Status")].text
                })
        raise ReportNotFound({"status": "Report not found", "report_name": export_name, "existing_reports": existing_reports})