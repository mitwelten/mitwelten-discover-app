def cleanup_timeseries(dict_data, lower_boundary, upper_boundary, key1="time", key2="value") -> dict:
    assert len(dict_data[key1]) == len(dict_data[key2])

    if not dict_data[key1]:  # list is empty
        return dict_data

    zipped = zip(dict_data[key1], dict_data[key2])
    zipped = filter(lambda pair: upper_boundary > pair[1] > lower_boundary, zipped)
    l1, l2 = zip(*zipped)
    result = {key1: list(l1), key2: list(l2)}
    return result
