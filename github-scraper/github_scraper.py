import os
import json
import requests
import argparse
from dotenv import load_dotenv

class GitHubScraper:
    def __init__(self) -> None:
        self.base_url = 'https://api.github.com'
        load_dotenv()
    
    def retrieve_user(self, username):
        user_req = requests.get(f'{self.base_url}/users/{username}', headers={"Accept":"application/vnd.github+json", "Authorization":f"Bearer {os.getenv('auth_token')}"})
        return user_req.json()


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description='Fetch GitHub user information.')
    cli_parser.add_argument('username', type=str, nargs=1, help='GitHub username whose information is needed.')
    cli_parser.add_argument('--file', type=str, nargs=1, choices=('y','n'), help='Output to file.')


    args = vars(cli_parser.parse_args())
    username = args['username'][0]
    output_to_file = args["file"][0]

    scraper = GitHubScraper()
    user_info = scraper.retrieve_user(username)

    if output_to_file == 'y':
        with open('data.json', 'w') as f:
            json.dump(user_info, f)
    else:
        print(user_info)