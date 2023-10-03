from blackbirdnest.utils import tower_api
import slugify
from tenacity import retry, Retrying, stop_after_attempt, wait_fixed
import logging, sys
from typing import Dict, List
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test




@transformer
def transform(data, *args, **kwargs):
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
    # Specify your transformation logic here
    metadata = []
    service_name = kwargs.get('service_name',"retail_link")
    scope_name = kwargs.get('scope',"retail_link")
    rl_bot_token_info = data['new_token']['payload']['token']
    tower_client_info = data.get('tower_client_info')
    tower_update_response = 'Not updated'
    print(data)
    update_params = {
        "service_name": service_name,
        "tower_id": tower_client_info["id"],
        "client_id":tower_client_info['client_id'],
        "rl_bot_token": rl_bot_token_info
        }
    if kwargs.get('debug_mode') == "true":
        return 'no action'
    tower = tower_api.Tower(scope=scope_name,service_name='retail_link')
    tower_update_respone = tower.update_client(update_params = update_params)
    print(tower_update_respone)
    

    return tower_update_respone


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'