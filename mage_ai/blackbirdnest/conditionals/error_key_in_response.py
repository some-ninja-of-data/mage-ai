if 'condition' not in globals():
    from mage_ai.data_preparation.decorators import condition

def contains_error_key(data):
    if isinstance(data, dict):
        if "error" in data:
            return True
        return any(contains_error_key(value) for value in data.values())
    elif isinstance(data, list):
        return any(contains_error_key(item) for item in data)
    return False

@condition
def evaluate_condition(*args, **kwargs) -> bool:
    has_error = contains_error_key(args)
    return not has_error
