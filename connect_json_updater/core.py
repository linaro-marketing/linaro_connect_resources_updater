import json
import requests
import boto3


class ConnectJSONUpdater:
    """This class handles the updating of a resources.json for a given Linaro Connect event"""

    def __init__(self, ):
        self._verbose = True
        self.connect_code = connect_code.lower()
        self.connect_resources_bucket_url = "https://static.linaro.org/connect/{0}/".format(
            self.connect_code)
        self.resources_json_url = self.connect_resources_bucket_url + "resources.json"
        self.presentations_url = self.connect_resources_bucket_url + "presentations/"
        self.videos_url = self.connect_resources_bucket_url + "videos/"
        # self.main()

        self.presentations_uploaded = self.fetch_files_from_s3_path(
            "static-linaro-org", "connect/san19/presentations/")

        self.videos_uploaded = self.fetch_files_from_s3_path(
            "static-linaro-org", "connect/san19/videos/")

        self.main()

    def fetch_files_from_s3_path(self, s3_bucket, s3_path):
        """ Fetches a list of files from an s3 path/bucket """
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('static-linaro-org')
        uploaded_files = []
        for obj in bucket.objects.filter(Prefix=s3_path):
            file_name = obj.key
            session_id = file_name.split(".")[0].split("/")[-1]
            dateModified = obj.last_modified
            uploaded_files.append([session_id, dateModified])
        if len(uploaded_files) > 0:
            return uploaded_files

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

    def main(self):
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
            else:
                missing_presentations_list.append(session_id)
            video_exists = self.check_for_video(session_id)
            if video_exists:
                video_url = "{0}{1}.mp4".format(
                    "https://static.linaro.org/connect/san19/videos/", session_id)
                each["s3_video_url"] = video_url
            else:
                missing_videos_list.append(session_id)
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
    updater = ResourcesJSONUpdater("SAN19")
