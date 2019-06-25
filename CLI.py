# Command Line Interface
import argparse as ap
import datetime as dt
import inflationtools.main as main
from argparse import RawTextHelpFormatter # Allows to use newline in help text

# Prepares indexes list.
indexes = {}
indexes.update(main.bcb_urls)
indexes.update(main.quandl_urls)
indexes = list(indexes.keys())
indexes.sort()

# Date parser
def parse_dates(date_string):
    assert type(date_string) is str, f'date_string is a {type(date_string)}'
    date_string = '01-' + date_string
    new_date = dt.datetime.strptime(date_string, '%d-%m-%Y')  # Quandl uses '2009-09-30' date style
    return new_date


def CLI():
    """
    Implements the argument parser to inflationtools.
    TODO
    localisation to portuguese (BR)
    :return:
    """
    parser = ap.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('index',
                        help='The inflation index that you want to look. Available: \n{}'.format(
                            '\n'.join(indexes)
                        ))
    parser.add_argument('start_date', help="Starting date, using '01-2001' format.")
    parser.add_argument('end_date', help="Ending date, using '01-2001' format.")
    arguments = parser.parse_args()
    arguments.start_date, arguments.end_date = parse_dates(arguments.start_date), parse_dates(arguments.end_date)
    return print(main.get_cumulative_inflation(arguments.index,
                                               arguments.start_date,
                                               arguments.end_date))

if __name__ == '__main__':
    CLI()