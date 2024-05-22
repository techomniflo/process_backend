import json
import os

script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, 'config.json')

if not os.path.exists(config_path):
    # Create the file if it doesn't exist
    with open(config_path, 'w') as config_file:
        # Write some default data into the file
        default_data = {
            "MYSQL_STRING": "mysql://root:put_your_password@localhost/beagle",
            "OPENAI_API_KEY": "your_default_openai_api_key"
        }
        json.dump(default_data, config_file)

with open(config_path) as config_file:
    config=json.load(config_file)

MYSQL_STRING=config.get("MYSQL_STRING")
OPENAI_API_KEY=config.get("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID=config.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=config.get("AWS_SECRET_ACCESS_KEY")