import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from connect_json_updater import ConnectJSONUpdater


if __name__ == "__main__":
    resources_updater = ConnectJSONUpdater("SAN19")
