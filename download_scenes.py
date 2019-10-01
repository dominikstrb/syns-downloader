import requests
import csv
import re
import os

# log in to the SYNS website
# TODO: use credentials from a cmd line arg or a config file
session = requests.Session()
login_data = {'email': 'dominikstraub@yahoo.com', 'password': '#ladida1'}
LOGIN_URL = "https://syns.soton.ac.uk/auth/login"
session.post(LOGIN_URL, data=login_data)


def get_filename_from_cd(cd):
    """ Get filename from content-disposition
        from: https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
    """
    if not cd:
        return None

    # find the filename in the content-disposition dict using a regular expression
    fname = re.findall('filename="(.+)"', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_scenes(urlfile="urls.csv"):
    """ Download all scenes specified in the url file

    Args:
        urlfile: csv file of the structure $SCENE_NUMBER, $URL, $FILETYPE

    Returns:
        None
    """
    with open(urlfile) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            scene_number, url, kind = row

            if not kind == "Kind":
                print("Downloading scene # {} at {} of type {}".format(scene_number, url, kind))
                r = session.get(url, allow_redirects=True)
                filename = get_filename_from_cd(r.headers.get('content-disposition'))

                if not os.path.exists("/data/datasets/SYNS/SYNSData/{}/".format(scene_number)):
                    os.makedirs("/data/datasets/SYNS/SYNSData/{}/".format(scene_number))

                open("/data/datasets/SYNS/SYNSData/{}/{}".format(scene_number, filename), 'wb').write(r.content)
