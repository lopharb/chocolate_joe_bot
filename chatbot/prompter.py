from .prompt import SYSTEM_MESSAGE

class Prompter:
    def __init__(self, system_message=SYSTEM_MESSAGE):
        self.system_message = system_message

    def get_context(self, message:str, username:str):
        context = [
            {
                'role':'system',
                'content' : self.system_message.format(
                    user_name = username
                )
            },
            {
                'role':'user',
                'content': message
            }
        ]

        return context
