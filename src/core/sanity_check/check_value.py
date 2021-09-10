def is_dust(num_tokens, token_decimal):
    """Check if num_tokens is dust. It should be above 1e10
    at the very least (in Wei)

    :param num_tokens:
    :param token_decimal:
    :return:
    """
    if num_tokens / 10 ** token_decimal < 1e-5:
        return True
    return False
