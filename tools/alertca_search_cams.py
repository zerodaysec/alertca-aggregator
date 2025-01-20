import requests
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--county", help="What county did you want to search in?")
    parser.add_argument(
        "--show-all", help="Show all cams??", action="store_true", default=False
    )
    parser.add_argument(
        "--show-fixed",
        help="Show all fixed cams - potentially fixed because someone is watching...",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--list-counties",
        help="List the counties found",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    # if args.list_counties is False and args.show_all is False and args.county is None:
    #     parser.print_help()
    #     exit(1)

    return args


def get_cams(args):
    """get cams"""
    url = "https://cameras.alertcalifornia.org/public-camera-data/all_cameras-v3.json"
    resp = requests.get(url, timeout=30)

    if resp.status_code != 200:
        raise Exception("Error fetching cam data")

    return resp.json()["features"]


def show_fixed_cams(cam_data):
    """show patrolling cams"""
    cams = []
    for cam in cam_data:
        # is_currently_patrolling = 0 means not patrolling?
        if cam["properties"]["is_currently_patrolling"] == 1:
            cams.append(cam)

        # cams.sort()
        for cam in cams:
            print(
                f"{cam['properties']['id']} - {cam['properties']['name']} - {cam['properties']['county']} - {cam['properties']['is_currently_patrolling']}"
            )

    return cams


def main():
    """main"""
    args = get_args()
    cam_resp = get_cams(args)

    if args.show_fixed:
        cams = show_fixed_cams(cam_resp)
        # print(cams)

    if args.list_counties:
        counties = []
        for cam in cam_resp:
            if cam["properties"]["county"] not in counties:
                counties.append(cam["properties"]["county"])

        counties.sort()

        print("Counties:")
        for c in counties:
            if c != "":
                print(f"- {c}")

    if args.show_all:
        cams = []
        for cam in cam_resp:
            details = cam["properties"]
            cams.append(
                (
                    details["id"],
                    details["name"],
                    details["county"],
                    details["is_currently_patrolling"],
                )
            )
        cams.sort()
        print("Cameras:")
        for c in cams:
            if c != "":
                print(f"ID: {c[0]}  Name: {c[1]}  County: {c[2]} Patrolling: {c[3]}")

    # if args.show_fixed:
    #     show_patrolling_cams(cam_resp['features'])
    if args.county:
        cams = []
        for cam in cam_resp:
            if cam["properties"]["county"] == args.county:
                cams.append(
                    (
                        cam["properties"]["id"],
                        cam["properties"]["name"],
                        cam["properties"]["county"],
                    )
                )
        cams.sort()
        for c in cams:
            if c != "":
                print(c)


if __name__ == "__main__":
    main()
