if 'condition' not in globals():
    from mage_ai.data_preparation.decorators import condition


@condition
def evaluate_condition(*args, **kwargs) -> bool:
    data = args[0]
    print(data)
    if not data.get('tower_client_info',{}).get('in_atlas'):
        return False
    return True
