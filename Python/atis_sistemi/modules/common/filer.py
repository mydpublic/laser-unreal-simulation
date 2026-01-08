import json
import os
from datetime import datetime


class Filer:
    def __init__(self):
        self.data_path = os.getcwd() + '/data'

    @staticmethod
    def read_from_file(path):
        with open(path) as json_file:
            return json.load(json_file)

    def write_to_file(self, image, data):
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        name = datetime.now().strftime("%Y%m%d-%H%M%S")
        os.mkdir('{}/{}'.format(self.data_path, name))
        image.save('{}/{}/{}.png'.format(self.data_path, name, name))
        with open('{}/{}/{}.json'.format(self.data_path, name, name), 'w') as outfile:
            json.dump(data, outfile, indent=2)
