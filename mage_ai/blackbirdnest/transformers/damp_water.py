from blackbirdnest.utils import high_radius 
import datetime
from blackbirdnest.utils import fileops
import slugify
from tenacity import retry, Retrying, stop_after_attempt, wait_fixed
import logging, sys

from typing import Dict, List

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data: Dict, *args, **kwargs) -> List[Dict]:
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    cred=data
    logger.info(cred)
    time_for_file = datetime.datetime.now().replace(microsecond=0)
    dt_for_filename = time_for_file.strftime('%Y%m%d_%H%M%S')
    timestamp_for_file_int = int(time_for_file.timestamp()*1000)
    WAIT_FOR_DOWNLOADED_FILE = 10 # seconds to wait before checking downloaded file again
    DOWNLOAD_WAIT_STOP_LOOP_COUNT = 6 # number of times to loop the check for downloaded file task

    downloaded = {}
    if cred.get('is_active', False):
        # check to make sure there is a folder path to use
        client_name = cred.get('sourcefolderpathname',None)
        if client_name:
            user_id = cred.get('user_id',None)
            password = cred.get('password', None)
            hro = high_radius.HighRadius()
            hro.login(username=user_id,password=password)
            slug_client = slugify.slugify(client_name)
            export_name = f'auto{timestamp_for_file_int}{slug_client}'
            logger.info(f'{client_name} started...')
            try:
                login_error_check = hro.check_login_error()
                if login_error_check == 'OK':
                    downloaded = hro.download_all_closed_bills(export_name=export_name)
            except Exception as e:
                login_error_check = hro.check_login_error()
                if login_error_check == 'OK':
                    logger.error(e)
                else:
                    logger.error(f'{client_name} unable to login')
                hro.browser.quit()
                return f'{client_name} unable to login'
            
            if downloaded.get('status',None) == 'Success':
                if downloaded['record_count'] == 0:
                    hro.browser.quit()
                    logger.warning(f'{client_name} returned 0 records')
                    return f'{client_name} returned 0 records'
                retry_download_check = Retrying(reraise=True, wait=wait_fixed(WAIT_FOR_DOWNLOADED_FILE), stop=stop_after_attempt(DOWNLOAD_WAIT_STOP_LOOP_COUNT), before_sleep=high_radius.my_before_sleep)
                path_to_copy = retry_download_check(fileops.get_downloaded_file,file_name_to_find=export_name)
                hro.browser.quit()
                logger.info(path_to_copy)
                copied = fileops.copy_file_to_folder(path_to_copy=path_to_copy,destination_path=f'A:\\Mozenda\\High radius\\{client_name}',destination_name=f'Closed Bills {dt_for_filename}.xlsx')
                logger.info(f'{client_name} downloaded file and copied to {copied}')
            else:
                hro.browser.quit()
                logger.warning(f'{client_name} file not successful')
                logger.warning(f'{downloaded}')
        else:
            logger.warning(f"Client does not have a folder name to save to: user - {cred.get('user_id','')}")
    else:
        logger.warning(f"Client is not active: user - {cred.get('user_id','')}")



    return [data]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'