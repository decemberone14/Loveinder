import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools
from data_store import check_user, add_user


class BotInterface:
    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.handle_message(event)

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send', {
            'user_id': user_id,
            "message": message,
            "attachment": attachment,
            "random_id": get_random_id()
        })

    def handler_info(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text

    def int_check(self, num):
        try:
            int(num)
        except (TypeError, ValueError):
            return False
        else:
            return True

    def handle_message(self, event):
        text = event.text.lower()

        if text == 'привет':
            self.handle_greeting(event)
        elif text == 'поиск':
            self.handle_search(event)
        elif text == 'пока':
            self.message_send(event.user_id, 'До новых встреч')
        else:
            self.message_send(event.user_id, 'Неизвестная команда')

    def handle_greeting(self, event):
        self.params = self.vk_tools.get_profile_info(event.user_id)
        self.message_send(event.user_id, f'Привет, {self.params["name"]},')

        if self.params['year'] is None:
            self.message_send(event.user_id, 'Укажите Ваш возраст, пожалуйста')
            age = self.get_valid_input('Введите корректный возраст', self.int_check)
            self.params['year'] = int(age)

        if self.params['city'] is None:
            self.message_send(event.user_id, 'Укажите Ваш город, пожалуйста')
            self.params['city'] = self.handler_info()

        if self.params['sex'] == 0:
            self.message_send(event.user_id, 'Укажите Ваш пол, пожалуйста м/ж')
            sex = self.get_valid_input('Введите корректный пол м/ж', lambda x: x.lower() in ['м', 'ж'])
            self.params['sex'] = 1 if sex == 'ж' else 2

        self.message_send(event.user_id, 'Введите "поиск" для поиска')

    def get_valid_input(self, prompt, validation_func):
        while True:
            user_input = self.handler_info()
            if validation_func(user_input):
                return user_input
            self.message_send(event.user_id, prompt)

    def handle_search(self, event):
        self.message_send(event.user_id, 'Начинаем поиск')

        if not self.worksheets:
            self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
            if not self.worksheets:
                self.message_send(event.user_id, 'К сожалению, не найдено анкет.')
                return

        worksheet = self.worksheets.pop()
        photos = self.vk_tools.get_photos(worksheet['id'])
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

        user_link = f'vk.com/id{worksheet["id"]}'
        self.message_send(
            event.user_id,
            f'имя: {worksheet["name"]} ссылка: {user_link}',
            attachment=photo_string
        )
        # добавление в БД
        if not check_user(event.user_id, worksheet["id"]):
            add_user(event.user_id, worksheet["id"])


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.run()
