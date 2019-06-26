# Command Line Interface
import argparse as ap
import datetime as dt
import inflationtools.main as main
from argparse import RawTextHelpFormatter # Allows to use newline in help text
import locale
import gettext # Unable to get pot for this file... find the reason.

pt = gettext.translation('CLI', localedir='locales', languages=['pt_BR'])

sys_locale = locale.getdefaultlocale()
if 'BR' in sys_locale[0]:
    pt.install()
    _ = pt.gettext

locale.setlocale(locale.LC_NUMERIC,
                 sys_locale[0][0:2])# Sets locales to system default for numbers
locale.setlocale(locale.LC_MONETARY, 'pt') # Sets locales to Brazil, for money

# Prepares indexes list.
indexes = {}
indexes.update(main.bcb_urls)
indexes.update(main.quandl_urls)
indexes = list(indexes.keys())
indexes.sort()
indexes = '\n'.join(indexes)

# Date parser
def parse_dates(date_string):
    assert type(date_string) is str, f'date_string is a {type(date_string)}'
    date_string = '01-' + date_string
    new_date = dt.datetime.strptime(date_string, '%d-%m-%Y')  # Quandl uses '2009-09-30' date style
    return new_date


def CLI():
    """
    Implements the argument parser to inflationtools.
    :return:
    """
    parser = ap.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('index', metavar=_('index'),
                        help=_('The inflation index that you want to look. Available: \n') + indexes)
    parser.add_argument('start_date', metavar=_('start_date'),
                        help=_("Starting date, using '01-2001' format."))
    parser.add_argument('end_date', metavar=_('end_date'),
                        help=_("Ending date, using '01-2001' format."))
    parser.add_argument('-a', '--amount', metavar=_('amount'),
                        help=_('Amount you want to update.'))
    arguments = parser.parse_args()
    arguments.start_date, arguments.end_date = parse_dates(arguments.start_date), parse_dates(arguments.end_date)
    inflation = main.get_cumulative_inflation(arguments.index, arguments.start_date, arguments.end_date)
    if arguments.amount:
        money = arguments.amount
        if money[0:2] == 'R$':
            money = money[2:]
        money = locale.atof(money)
        money *= inflation
        print(locale.currency(money)) # Prints in BRL
    else:
        print(locale.str(inflation))

if __name__ == '__main__':
    CLI()