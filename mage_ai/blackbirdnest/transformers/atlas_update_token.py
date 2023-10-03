if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
from blackbirdnest.utils import atlas
import slugify
from tenacity import retry, Retrying, stop_after_attempt, wait_fixed
import logging, sys
from typing import Dict, List
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


logger = logging.getLogger(__name__)

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
    client_in_atlas = data.get('tower_client_info',{}).get('in_atlas')
    if client_in_atlas != True:
        return {"error": "Client is not in atlas","client_info": data.get('tower_client_info')}
    rl_bot_token_info = data['new_token']['payload']['token']
    atlas_user = kwargs.get('atlas_user')
    atlas_pass = kwargs.get('atlas_pass')
    atlas_client_filters = kwargs.get('atlas_client_filters',{})
    rl_username = data['tower_client_info'].get('user_id')
    atlas_client_filters['userName']=rl_username

    atlas_bot = atlas.Atlas(username=atlas_user,password=atlas_pass)
    login_attempt = atlas_bot.login()
    print(login_attempt)
    clients_list = atlas_bot.get_clients(client_filters=atlas_client_filters)
    if len(clients_list) == 0:
        return {"error": "No matching client found","criteria": atlas_client_filters}
        
    return clients_list


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

@test
def test_error_response(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert 'error' not in output, output.get('error')