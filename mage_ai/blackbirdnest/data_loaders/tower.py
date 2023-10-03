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
    service_name = kwargs['service_name']
    scope_setting = kwargs['scope']
    tower = tower_api.Tower(scope=scope_setting)
    creds = tower.get_all_clients_for_service(service_name=service_name)
    for c in creds:
        metadata.append(dict(block_uuid=c['id']))
    return [
        creds,
        metadata,
    ]