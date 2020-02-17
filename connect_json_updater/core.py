import json
import requests
import boto3
from botocore.exceptions import ClientError
import logging


class ConnectJSONUpdater:
    """
    The Linaro Connect JSON Updater

    Attributes
    ----------
    s3_bucket : string
        The s3 bucket e.g static-linaro-org
    s3_prefix: string
        The s3 object key prefix to the presentations/videos/resources.json
    sched_data: json
        The Sched sessions data.
    sched_data: json
        AWS credentials Access/secret keys.

    Methods
    -------
    update()
        Download and update the resources.json file.
    updateEntry(key, options)
        Updates a specific entry in the JSON file based on a key.
    getMissingPresentations()
        Returns a list of the missing presentations.
    getMissingVideos()
        Returns a list of the missing videos.

    """

    def __init__(self, s3_bucket_url, s3_prefix, sched_data, output_directory):

        # Toggle verbose output
        self._verbose = True
        self.output_directory = output_directory
        # Set the s3 bucket url
        self.s3_bucket = s3_bucket_url
        self.s3_prefix = s3_prefix
        # Set the s3 urls
        self.cdn_url = "https://static.linaro.org/"
        self.resources_json_url = self.cdn_url + s3_prefix + "resources.json"
        self.presentations_prefix = s3_prefix + "presentations/"
        self.other_files_prefix = s3_prefix + "other_files/"
        self.videos_prefix = s3_prefix + "videos/"
        self.current_json_data = self.fetch_resources_json()
        self.missing_videos_list = []
        self.missing_presentations_list = []

        self.session = boto3.Session()
        self.s3_client = self.session.client('s3')
        self.s3_resource = self.session.resource('s3')
        self.bucket = self.s3_resource.Bucket(self.s3_bucket)
        # Sched Data from the SchedDataInterface module
        self.sched_data = sched_data

    def upload_file_to_s3(self, file_path, s3_path):
        """Uploads the given file located at file_path to the specified s3_path"""
        try:
            self.s3_client.upload_file(file_path, self.s3_bucket, s3_path)
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def update_resources_entry_by_session_id(self, session_id, options_dict):
        """Updates the resources json file based on a given session id"""

        for session in self.current_json_data:
            if session["session_id"] == session_id:
                for key, value in options_dict.items():
                    session[key] = value

        self.upload_json_data(self.current_json_data)

    def create_initial_resources_json_file(self):

        """Creates a new resources JSON file based on sessions data provided by the SchedDataInterface Module"""

        print("Creating an initial resources.json file")
        json_data = []
        for session in self.sched_data.values():
            new_session_dict = {
                "session_id": session["session_id"],
                "s3_presentation_url": [],
                "s3_video_url": "",
                "youtube_video_url": "",
                "other_files": []
            }
            json_data.append(new_session_dict)

        with open('resources.json', 'w') as outfile:
            json.dump(json_data, outfile)

    def fetch_files_from_s3_path(self, s3_path):
        """ Fetches a list of files from an s3 path/bucket """
        uploaded_files = []
        for obj in self.bucket.objects.filter(Prefix=s3_path):
            file_name = obj.key
            session_id = file_name.split(".")[0].split("/")[-1]
            dateModified = obj.last_modified
            uploaded_files.append([session_id, dateModified,file_name])
        if len(uploaded_files) > 0:
            return uploaded_files
        else:
            return False

    def check_for_presentation(self, session_id):
        presentations_list = []
        for file_uploaded in self.presentations_uploaded:
            if session_id in file_uploaded[0] or session_id.upper() in file_uploaded[0]:
               presentations_list.append(file_uploaded)
        return presentations_list

    def check_for_other_files(self, session_id):
        other_files_list = []
        for file_uploaded in self.other_files_uploaded:
            if session_id in file_uploaded[0]:
               other_files_list.append(file_uploaded)
        return other_files_list

    def check_for_video(self, session_id):
        found = False
        for file_uploaded in self.videos_uploaded:
            upload_session_id = file_uploaded[0]
            if session_id == upload_session_id:
                found = True
            elif session_id.lower() == upload_session_id:
                found = True
            elif session_id.upper() == upload_session_id:
                found = True
        return found

    def updateEntry(self, key, options):
        """Update an entry in the resources json file

        Paramters
        ---------
        key: string
            The unique key of the entry in the JSON file
        options: dict
            Dictionary object containing the changed values and their respective keys


        Returns
        -------
        boolean: Returns True if the JSON file updated successfully

        """
        pass

    def getMissingPresentations(self):
        """Fetches a list of the missing presentations

        Returns
        -------
        list: list of the missing presentations

        """
        # Fetch the current list of videos from S3
        self.presentations_uploaded = self.fetch_files_from_s3_path(self.presentations_prefix)
        for each in self.current_json_data:
            session_id = each["session_id"]
            if self.presentations_uploaded != False:
                presentation_exists = self.check_for_presentation(session_id)
                if len(presentation_exists) == 0:
                    self.missing_presentations_list.append(session_id)

        return self.missing_presentations_list

    def getMissingVideos(self):
        """Fetches a list of the missing videos

        Returns
        -------
        list: list of the missing videos

        """
        # Fetch the current list of videos from S3
        self.videos_uploaded = self.fetch_files_from_s3_path(self.videos_prefix)

        for each in self.current_json_data:
            session_id = each["session_id"].lower()
            if self.videos_uploaded != False:
                video_exists = self.check_for_video(session_id)
                if not video_exists:
                    self.missing_videos_list.append(session_id)

        return self.missing_videos_list

    def update(self):
        """Batch update to ensure json file is up to date

        Returns
        -------
        boolean: Returns True if the JSON file updated successfully

        """
        # Get list of latest session_ids
        list_of_latest_session_ids = [each["session_id"] for each in self.sched_data.values()]
        # Get list of current session_ids
        list_of_current_session_ids = [each["session_id"] for each in self.current_json_data]

        # # Test removing latest session
        # list_of_latest_session_ids.pop(2)
        # # Test removing current session
        # list_of_current_session_ids.pop(1)

        # Check if all latest session_ids exist in list_of_current_session_ids
        # if not then add a new entry to the json_data
        added_sessions = []
        for latest in list_of_latest_session_ids:
            if latest not in list_of_current_session_ids:
                added_sessions.append(latest)
                new_session_dict = {
                    "session_id": latest,
                    "s3_presentation_url": "",
                    "s3_video_url": "",
                    "youtube_video_url": "",
                    "other_files": ""
                }
                self.current_json_data.append(new_session_dict)

        print("{0} sessions Added:".format(len(added_sessions)))
        print(added_sessions)
        # Remove entries that no longer exist
        removed_sessions = []
        self.current_json_data = [entry if entry["session_id"] in list_of_latest_session_ids else removed_sessions.append(entry) for entry in self.current_json_data]
        print("{0} sessions removed:".format(len(removed_sessions)))
        print(removed_sessions)

        # Update resource urls in json_data
        #session_id
        # Fetch the current list of presentations from S3
        self.presentations_uploaded = self.fetch_files_from_s3_path(self.presentations_prefix)
        # Fetch the current list of presentations from S3
        self.other_files_uploaded = self.fetch_files_from_s3_path(self.other_files_prefix)
        # Fetch the current list of videos from S3
        self.videos_uploaded = self.fetch_files_from_s3_path(self.videos_prefix)

        if self._verbose:
            print("Updating the resources.json file. Please wait...")

        for each in self.current_json_data:
            session_id = each["session_id"].lower()
            if self.other_files_uploaded != False:
                other_files_list = self.check_for_other_files(each["session_id"])
                if len(other_files_list) >0:
                    other_files_url_list = []
                    for other_file in other_files_list:
                        other_files_url_list.append("{0}{1}".format(self.cdn_url, other_file[2]))
                    each["other_files"] = other_files_url_list
                else:
                    each["other_files"] = []

            if self.presentations_uploaded != False:
                presentations_list = self.check_for_presentation(each["session_id"])
                if len(presentations_list) >0:
                    presentations_url_list = []
                    for presentation_file in presentations_list:
                        presentations_url_list.append("{0}{1}".format(self.cdn_url, presentation_file[2]))
                    each["s3_presentation_url"] = presentations_url_list
                else:
                    each["s3_presentation_url"] = []
            if self.videos_uploaded != False:
                video_exists = self.check_for_video(session_id)
                if video_exists:
                    video_url = "{0}{1}videos/{2}.mp4".format(self.cdn_url, self.s3_prefix, session_id)
                    each["s3_video_url"] = video_url
            print("*", end="", flush=True)

        self.upload_json_data(self.current_json_data)


    def upload_json_data(self, json_data):
        """ Upload given json_data to s3 as resources.json"""

        print("Writing the resources.json file locally...")
        output_path = os.path.join(self.output_directory, "resources.json")
        with open(output_path, 'w') as outfile:
            json.dump(json_data, outfile)
        # Upload updated resources.json file
        uploaded = self.upload_file_to_s3(output_path, self.s3_prefix + "resources.json")
        if uploaded:
            print("The updated resources.json file has been uploaded to s3.")
            return True
        else:
            print("The updated resources.json file failed to upload!")
            return False

    def check_for_file(self, file_url):
        try:
            resp = requests.get(url=file_url)
            if resp.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def fetch_resources_json(self):
        try:
            resp = requests.get(url=self.resources_json_url)
            if self._verbose:
                print(self.resources_json_url)
            data = resp.json()
            return data
        except Exception as e:
            print(e)
            return False


if __name__ == "__main__":
    json_updater = ConnectJSONUpdater("static-linaro-org", "connect/san19/presentations/", "connect/san19/videos/", "connect/san19/resources.json")
    json_updater.update()
