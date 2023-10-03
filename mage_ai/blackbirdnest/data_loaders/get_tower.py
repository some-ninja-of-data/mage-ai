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


@data_loader
def get_tower_creds(**kwargs) -> List[List[Dict]]:
    metadata = []
    print(kwargs)
    service_name = kwargs['service_name']
    scope_name = kwargs['scope']
    filters = kwargs.get('client_filters')
    if filters == None or filters == {}:
        return [[{"error": "no filters provided"}],[]]
    tower = tower_api.Tower(scope=scope_name)
    creds = tower.get_clients_for_service(service_name=service_name,client_filters=filters)
    for c in creds:
        logger.debug(c)
        metadata.append(dict(block_uuid=c['id']))
    return [
        creds,
        metadata,
    ]

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    

@test
def test_only_one(output, *args) -> None:
    
    assert len(output) > 0, 'Filters returned 0 clients'
    assert len(output) == 1 , f"Filters returned more than one client - {output}"
    