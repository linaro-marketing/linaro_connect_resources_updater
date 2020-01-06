import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from connect_json_updater import ConnectJSONUpdater


if __name__ == "__main__":
    json_updater = ConnectJSONUpdater("static-linaro-org", "connect/san19/presentations/", "connect/san19/videos/", "connect/san19/resources.json")
    json_updater.update()
