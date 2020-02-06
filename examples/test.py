import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from connect_json_updater import ConnectJSONUpdater
from sched_data_interface import SchedDataInterface

if __name__ == "__main__":
    sched_data_interface = SchedDataInterface(
        "https://bud20.sched.com", "", "BUD20")
    sched_data = sched_data_interface.getSessionsData()
    json_updater = ConnectJSONUpdater(
        "static-linaro-org", "connect/bud20/", sched_data)
    # json_updater.create_initial_resources_json_file()
    # json_updater.upload_file_to_s3("resources.json", "connect/bud20/resources.json")
    json_updater.update_resources_entry_by_session_id("BUD20-103", {"youtube_video_url":"test"})
