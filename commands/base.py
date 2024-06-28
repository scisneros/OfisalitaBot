import re

from telegram import Message


class Command:
    """
    This object represents a bot command.
    Takes care of basic command functionality, such as parsing and logging.
    """

    def __init__(self, message: Message):
        self.message_obj = message
        parsed = self._parse()
        self.command = parsed["command"]
        self.opts = self._parse_opts(parsed["opts"])
        self.arg = parsed["arg"]

    def _parse(self):
        """
        Parses a command message and returns a dictionary with the command,
        options and argument (text).
        """
        match = re.match(
            r"^(?P<command>\/\w+)(?:\((?P<opts>.*?)\))?(?: (?P<arg>.*))?$",
            self.message_obj.text,
            re.DOTALL,
        )
        if match:
            return match.groupdict()
        else:
            raise ValueError("Invalid command format.")

    def _parse_opts(self, opts):
        """
        Parses the options string and returns a dictionary.
        """
        if not opts:
            return {}
        opts_split = opts.split(",")
        opts_pairs = []
        for p in [opt.split("=") for opt in opts_split]:
            if len(p) != 2:
                p = (p[0], str(True))
            p = (p[0].strip(), p[1].strip())
            opts_pairs.append(p)
        opts_dict = dict(opts_pairs)
        return opts_dict

    def get_arg_reply(self) -> str:
        """
        Returns the argument of a command or the text of a reply.
        (Preference towards replies)
        """
        if self.message_obj.reply_to_message:
            return self.message_obj.reply_to_message.text
        return self.arg
