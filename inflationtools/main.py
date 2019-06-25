import requests
import datetime as dt

bcb_urls = {
    'IPCA-Serviços': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10844/dados?formato=json',
    'IPCA-Bens não-duráveis': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10841/dados?formato=json',
    'IPCA-Bens semi-duráveis': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10842/dados?formato=json',
    'IPCA-Bens duráveis': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10842/dados?formato=json',
}  # URLs from the Brazilian Central Bank (BCB)
quandl_urls = {
    'IGP-M': 'https://www.quandl.com/api/v3/datasets/BCB/189.json?api_key=sJMP4nxHHWCYEg23jBfp',
    'INPC': 'https://www.quandl.com/api/v3/datasets/BCB/188.json?api_key=sJMP4nxHHWCYEg23jBfp',
    'IPCA': 'https://www.quandl.com/api/v3/datasets/BCB/433.json?api_key=sJMP4nxHHWCYEg23jBfp',
    'IPA': 'https://www.quandl.com/api/v3/datasets/BCB/225.json?api_key=sJMP4nxHHWCYEg23jBfp',
    'IGP-DI': 'https://www.quandl.com/api/v3/datasets/BCB/190.json?api_key=sJMP4nxHHWCYEg23jBfp'
} # URLs from Quandl data marketplace


def parse_quandl_json(url, ignore_day=True):
    """
    Returns a list of dictionaries using the 'date':'value' schema using the Quandl's API.
    :param url: a url referenced as a value in quandl_urls dict
    :param ignore_day: ignores the day when parsing data. IGP usually is delivered in the last day of the month.
    :return:
    :rtype: list

    >>> parse_quandl_json(quandl_urls['IGP-M'], ignore_day=False)[0]
    {'date': datetime.datetime(1989, 6, 30, 0, 0), 'value': 19.68}
    """
    global quandl_urls
    assert url in quandl_urls.values(), f'{url} is not a quandl url'
    data = requests.get(url).json()
    output = list()
    for item in data['dataset']['data']:
        date, rate = item
        date = dt.datetime.strptime(date, '%Y-%m-%d') #Quandl uses '2009-09-30' date style
        if ignore_day:
            date = dt.datetime(date.year, date.month, 1) #Sets day to 1
        new_item = {'date': date, 'value': float(rate)}
        output.append(new_item)
    output = sorted(output, key=lambda k: k['date']) #Sorts the list. Newest date first.
    return output


def parse_bcb_json(url):
    """
    Returns a list of dictionaries using the 'date':'value' schema using Brazil Central Bank API.
    :param url: A string pointing to BCB's JSON API
    :type url: str
    :return: Sorted list of dicts
    :rtype: list

    >>> parse_bcb_json(bcb_urls['IPCA-Serviços'])[0]
    {'date': datetime.datetime(1992, 1, 1, 0, 0), 'value': '25.84'}
    """
    global bcb_urls
    assert url in bcb_urls.values(), f'{url} is not a Central Bank url'
    data = requests.get(url).json()
    output = list()
    for item in data:
        date, rate = item['data'], item['valor']
        date = dt.datetime.strptime(date, '%d/%m/%Y')#BCB uses '30/09/2009' date style
        new_item = {'date': date, 'value': float(rate)}
        output.append(new_item)
    output = sorted(output, key=lambda k: k['date']) #Sorts the list. Newest date first.
    return output


def get_cumulative_inflation(inflation_index, start_date, end_date=None, ignore_day=True):
    """
    Returns the cumulative inflation as float, using the chosen inflation_index.
    If no end_date is defined, returns month's inflation.
    :param inflation_index: Name of the Inflation Index.
    :type inflation_index: str
    :param start_date: Starting date, which is included.
    :type start_date: dt.datetime
    :param end_date: Ending date, which is included.
    :type end_date: dt.datetime
    :param ignore_day: Ignores days when parsing the data. Choose this if you want monthly results.
    :type ignore_day: bool
    :return: The total inflation of time.
    :rtype: float

    :Examples:
    >>> get_cumulative_inflation('IPCA-Serviços', dt.datetime(1995,1,1), dt.datetime(2000,1,1))
    2.0355712526263328
    >>> get_cumulative_inflation('IGP-M' , dt.datetime(1997,1,1), dt.datetime(1997,1,1))
    1.0177
    """
    if (end_date is None) or (end_date == start_date):
        end_date = start_date # Defaults to the same date
    else:
        assert start_date < end_date, f'{start_date} must be equal or earlier then {end_date}.'
    assert (type(start_date) is dt.datetime) and (type(end_date) is dt.datetime), 'Dates must be datetime datatype.'
    value = 1
    if inflation_index in bcb_urls.keys():
        inflation_data = parse_bcb_json(bcb_urls[inflation_index])
    elif inflation_index in quandl_urls.keys():
        inflation_data = parse_quandl_json(quandl_urls[inflation_index], ignore_day)
    else:
        indexes_names = ', '.join(list(bcb_urls.keys())) + ', ' + ', '.join(list(quandl_urls.keys()))
        raise ValueError(f'{inflation_index} is not a valid option. Try the following instead:\n{indexes_names}')
    for rate in inflation_data:
        if (rate['date'] >= start_date) and (rate['date'] <= end_date):
            new_value = rate['value'] / 100 + 1  # Turns the value into a percentile
            value *= new_value
        else:
            pass
    if value == 1:
        if (not ignore_day) and (inflation_index in quandl_urls.keys()):
            raise ValueError(f'Invalid output {value}. Probably should pass True to ignore_day.')
        raise ValueError(f'Unknown error error. Try other dates or indexes.')
    return value
