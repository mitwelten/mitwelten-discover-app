import logging
logger = logging.getLogger(__name__)

def cleanup_timeseries(dict_data, lower_boundary, upper_boundary, key1="time", key2="value") -> dict:
    assert len(dict_data[key1]) == len(dict_data[key2])

    if not dict_data[key1]:  # list is empty
        return dict_data

    zipped = zip(dict_data[key1], dict_data[key2])
    zipped = filter(lambda pair:
                    pair[0] is not None and
                    pair[1] is not None and
                    upper_boundary > pair[1] > lower_boundary,
                    zipped)

    try:
        l1, l2 = zip(*zipped)
        return {key1: list(l1), key2: list(l2)}
    except ValueError:
        logger.warning("Validation of timeseries with empty collection result!")

    return {key1: [], key2: []}
