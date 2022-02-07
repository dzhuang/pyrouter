import argparse

from .router_client import RouterClient


def apply_action(url, password, action, **kwargs):
    client = RouterClient(url, password)
    func = getattr(client, action)
    return func(**kwargs)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--url", required=True)
    parser.add_argument("-p", "--password", required=True)
    subparsers = parser.add_subparsers(dest="action")
    subparsers.add_parser("get_all_info")
    subparsers.add_parser("get_all_hosts_info")
    subparsers.add_parser("get_blocked_hosts")
    subparsers.add_parser("query_limit_time")
    subparsers.add_parser("get_online_hosts_info")
    subparsers.add_parser("get_restructured_info_dicts")
    set_block_flag_parser = subparsers.add_parser("set_block_flag")
    set_block_flag_parser.add_argument("--mac", required=True)
    set_block_flag_parser.add_argument("--is_blocked", required=False, default=True)

    args = parser.parse_args()

    result = apply_action(**vars(args))
    import pprint
    pprint.pprint(result)


if __name__ == "__main__":
    main()
