from router_client import RouterClient
import argparse


def apply_action(url, password, action, **kwargs):
    client = RouterClient(url, password)
    func = getattr(client, action)
    return func(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--url", required=True)
    parser.add_argument("-p", "--password", required=True)
    subparsers = parser.add_subparsers(dest="action")
    get_all_hosts_info_parser = subparsers.add_parser("get_all_hosts_info")
    get_blocked_hosts_parser = subparsers.add_parser("get_blocked_hosts")
    query_limit_time_parser = subparsers.add_parser("query_limit_time")

    args = parser.parse_args()

    result = apply_action(**vars(args))
    import pprint
    pprint.pprint(result)
