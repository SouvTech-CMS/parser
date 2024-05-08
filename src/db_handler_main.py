import json
import time

from api.command_handler import get_parser_info
from configs.env import DATA_FOLDER_PATH
from constants.commands import ParserCommand
from schemes.parser_info import Parser


def update_json(command: int, parser_id: int):
    pass


def command_check(parser: Parser):
    command = parser.command
    if command == ParserCommand.NO_COMMAND:
        pass
    elif command == ParserCommand.PARSE_NOW:
        pass
    elif command == ParserCommand.UPDATE_ETSY_COOKIE:
        pass


def main():
    while True:
        with open(f"{DATA_FOLDER_PATH}/shops.json") as f:
            data = json.load(f)
        for shop in data:
            parser = get_parser_info(shop["parser_id"])
            command_check(parser)
        time.sleep(30)


if __name__ == "__main__":
    main()
