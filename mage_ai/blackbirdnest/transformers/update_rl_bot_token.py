from blackbirdnest.utils import wm_retail_slinky
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
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
    client_info = data[0][0]
    print(args)
    if kwargs.get('debug_mode') == "true":
        return client_info
    client_info = data[0][0]
    logger.info(client_info)
    if not client_info.get('rl_bot_token'):
        return {"error": "no bot token passed into function","client_info": client_info}
    rl_auto = wm_retail_slinky.RetailLink(
        username=client_info['user_id'],
        password=client_info['password'],
        rl_bot_token=client_info['rl_bot_token'])
    bot_info = rl_auto.login()
    logger.info(bot_info)
    print(bot_info)
    
    new_token = rl_auto.reset_bot_token()
    print(new_token)
    # new_token.update({"tower_id": client_info['id'],"tower_client_id": client_info['client_id']})
    
    returning_json = {
        "new_token": new_token,
        "tower_client_info": client_info
    }
    return returning_json


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'