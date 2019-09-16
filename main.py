import json
import requests

class ResourcesJSONUpdater:
    """This class handles the updating of a resources.json for a given Linaro Connect event"""
    def __init__(self, connect_code):
        self._verbose = True
        self.connect_code = connect_code.lower()
        self.connect_resources_bucket_url = "https://static.linaro.org/connect/{0}/".format(self.connect_code)
        self.resources_json_url = self.connect_resources_bucket_url + "resources.json"
        self.presentations_url = self.connect_resources_bucket_url + "presentations/"
        self.videos_url = self.connect_resources_bucket_url + "videos/"
        self.main()

    def main(self):
        json_data = self.fetch_resources_json()
        if self._verbose:
            print("Updating the resources.json file. Please wait...")
        for each in json_data:
            session_id = each["session_id"].lower()
            presentation_url = "{0}{1}.pdf".format(self.presentations_url, session_id)
            video_url = "{0}{1}.mp4".format(self.videos_url, session_id)
            presentation_exists = self.check_for_file(presentation_url)
            if presentation_exists:
                each["amazon_s3_presentation_url"] = presentation_url
            video_exists = self.check_for_file(video_url)
            if video_exists:
                each["amazon_s3_video_url"] = video_url
            print("*", end="", flush=True)
        print()

        print("Writing the resources.json file...")
        with open('resources.json', 'w') as outfile:
            json.dump(json_data, outfile)#
        if self._verbose:
            print("resources.json file written!")
            print("You can now run:")
            print("aws s3 --profile Web_Developer cp resources.json s3://static-linaro-org/connect/san19/resources.json ")

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
