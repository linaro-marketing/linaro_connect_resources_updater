import json
import requests
import boto3


class ConnectJSONUpdater:
    """
    The Linaro Connect JSON Updater

    Attributes
    ----------
    s3_bucket : string
        The s3 bucket e.g static-linaro-org
    presentations_object_prefix: string
        The s3 object key prefix to the presentation objects e.g connect/SAN19/presentations/
    videos_object_prefix: string
        The s3 object key prefix to the video objects e.g. connect/SAN19/videos/
    json_object_key: string
        The s3 object key name of the resources json file e.g connect/SAN19/resources.json

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

    def __init__(self, s3_bucket_url, presentations_object_prefix, videos_object_prefix, json_object_key):

        # Toggle verbose output
        self._verbose = True
        # Set the s3 bucket url
        self.s3_bucket = s3_bucket_url
        # Set the s3 urls
        self.resources_json_url = "https://static.linaro.org/" + json_object_key
        print(self.resources_json_url)
        self.presentations_prefix = presentations_object_prefix
        self.videos_prefix = videos_object_prefix

    def fetch_files_from_s3_path(self, s3_bucket, s3_path):
        """ Fetches a list of files from an s3 path/bucket """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(s3_bucket)
        uploaded_files = []
        for obj in bucket.objects.filter(Prefix=s3_path):
            file_name = obj.key
            session_id = file_name.split(".")[0].split("/")[-1]
            dateModified = obj.last_modified
            uploaded_files.append([session_id, dateModified])
        if len(uploaded_files) > 0:
            return uploaded_files
        else:
            return False

    def check_for_presentation(self, session_id):
        found = False
        for file_uploaded in self.presentations_uploaded:
            upload_session_id = file_uploaded[0]
            if session_id == upload_session_id:
                found = True
        return found

    def check_for_video(self, session_id):
        found = False
        for file_uploaded in self.videos_uploaded:
            upload_session_id = file_uploaded[0]
            if session_id == upload_session_id:
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
        pass

    def getMissingVideos(self):
        """Fetches a list of the missing videos

        Returns
        -------
        list: list of the missing videos

        """
        pass

    def update(self):
        """Batch update to ensure json file is up to date

        Returns
        -------
        boolean: Returns True if the JSON file updated successfully

        """

        # Fetch the current list of presentations from S3
        self.presentations_uploaded = self.fetch_files_from_s3_path(
            self.s3_bucket, self.presentations_prefix)
        # Fetch the current list of videos from S3
        self.videos_uploaded = self.fetch_files_from_s3_path(
            self.s3_bucket, self.videos_prefix)

        # Get the current resources json file
        json_data = self.fetch_resources_json()
        missing_presentations_list = []
        missing_videos_list = []
        if self._verbose:
            print("Updating the resources.json file. Please wait...")
        for each in json_data:
            session_id = each["session_id"].lower()
            presentation_exists = self.check_for_presentation(session_id)
            video_exists = self.check_for_video(session_id)
            if presentation_exists:
                presentation_url = "{0}{1}.pdf".format(
                    "https://static.linaro.org/connect/san19/presentations/", session_id)
                each["s3_presentation_url"] = presentation_url
            video_exists = self.check_for_video(session_id)
            if video_exists:
                video_url = "{0}{1}.mp4".format(
                    "https://static.linaro.org/connect/san19/videos/", session_id)
                each["s3_video_url"] = video_url
            print("*", end="", flush=True)

        print("Writing the resources.json file...")
        with open('resources.json', 'w') as outfile:
            json.dump(json_data, outfile)
        if self._verbose:
            print("resources.json file written!")
            print("You can now run:")
            print(
                "aws s3 cp resources.json s3://static-linaro-org/connect/san19/resources.json ")

        with open("missing_presentations_list.txt", "w") as missing_presentations_file:
            for line in missing_presentations_list:
                missing_presentations_file.write(line + "\n")
        with open("missing_videos_list.txt", "w") as missing_videos_file:
            for line in missing_videos_list:
                missing_videos_file.write(line + "\n")

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
