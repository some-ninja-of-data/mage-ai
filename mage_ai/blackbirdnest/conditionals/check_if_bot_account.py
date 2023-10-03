if 'condition' not in globals():
    from mage_ai.data_preparation.decorators import condition


@condition
def evaluate_condition(*args, **kwargs) -> bool:
    print(args[0][0][0])
    if not args[0][0][0].get('rl_bot_token'):
        return False
    return True
