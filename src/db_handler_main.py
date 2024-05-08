import json
import time

from api.command_handler import get_parser_info, update_parser_command_to_default
from configs.env import DATA_FOLDER_PATH
from constants.commands import ParserCommand
from schemes.parser_info import Parser


def update_commands_json(command: int, parser_id: int):
    with open(f"{DATA_FOLDER_PATH}/shops/commands.json", "r") as f:
        data = json.load(f)

    data[parser_id - 1]["command"] = command

    with open(f"{DATA_FOLDER_PATH}/shops/commands.json", "w") as f:
        json.dump(data, f)

    print(data)


def command_check(parser: Parser):
    command = parser.command
    if command == ParserCommand.NO_COMMAND:
        return
    update_commands_json(command, parser.id)
    update_parser_command_to_default(parser.id)
    # elif command == ParserCommand.PARSE_NOW:
    #     pass
    # elif command == ParserCommand.UPDATE_ETSY_COOKIE:
    #     pass


def main():
    while True:
        try:
            with open(f"{DATA_FOLDER_PATH}/shops/shops.json", "r") as f:
                data = json.load(f)
        except Exception:
            continue
        for shop in data:
            parser = get_parser_info(shop["parser_id"])
            command_check(parser)
        time.sleep(15)


if __name__ == "__main__":
    main()
