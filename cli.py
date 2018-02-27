import argparse
from yuna import update, delete, query

parser = argparse.ArgumentParser()
sub_parsers = parser.add_subparsers()


def update_cli(args):
    update(args.stocks, args.from_date, args.to_date)


update_parser = sub_parsers.add_parser('update', aliases=['u'])
update_parser.add_argument('stocks', nargs='*')
update_parser.add_argument('-f', '--from', required=True, dest='from_date')
update_parser.add_argument('-t', '--to', required=True, dest='to_date')
update_parser.set_defaults(func=update_cli)


def query_cli(args):
    query(args.stocks, args.indicator)


query_parser = sub_parsers.add_parser('query', aliases=['q'])
query_parser.add_argument('stocks', nargs='*')
query_parser.add_argument('-i', '--indicator', required=True, dest='indicator')
query_parser.set_defaults(func=query_cli)


def delete_cli():
    delete()


delete_parser = sub_parsers.add_parser('delete', aliases=['d'])
delete_parser.set_defaults(func=delete_cli)


def cli():
    args = parser.parse_args()
    if len(vars(args)) == 1:
        args.func()
    else:
        args.func(args)


if __name__ == '__main__':
    cli()
