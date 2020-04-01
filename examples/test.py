import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from connect_json_updater import ConnectJSONUpdater
from sched_data_interface import SchedDataInterface
from secret import SCHED_API_KEY

if __name__ == "__main__":
    sched_data_interface = SchedDataInterface(
        "https://linarotechdays.sched.com", SCHED_API_KEY, "LTD20")
    sched_data = sched_data_interface.getSessionsData()
    json_updater = ConnectJSONUpdater(
        "static-linaro-org", "connect/ltd20/", sched_data, "output/")
    # json_updater.create_initial_resources_json_file()
    missing_presentations = json_updater.getMissingPresentations()
    with open("missing_presentations.txt", "w") as my_file:
        for each in missing_presentations:
            my_file.write(each + "\n")

    missing_videos = json_updater.getMissingVideos()
    with open("missing_videos.txt", "w") as my_file:
        for each in missing_videos:
            my_file.write(each + "\n")
    json_updater.update()
