import vk_api, random, pytz, wikipedia, time, requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime


class Goliath():
    def __init__(self, token='4780dffe7455f6914472013e2b31e5659c57325d768e6548f5e9f55986eeb9d371a3d34b8bc4d24b11a9b',
                 group_id='193261610'):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.msg = 'Привет,{} вот список команд: /time, /wiki...'
        self.commands = ['/time', '/wiki']
        self.tz = pytz.timezone('Europe/Moscow')
        self.days_of_week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница',
                        'суббота', 'воскресенье']
        self.chatting()

    def current_time(self):
        date = datetime.now(self.tz)
        day = self.days_of_week[date.weekday()]
        time = str(date)[11:16]
        date = str(date)[0:10]
        return 'Сегодня {}, {}. Московское время: {}.'.format(date, day, time)

    def writer_msg(self, name, surname, msg):
        print('Новое сообщение:')
        print(name, surname + ':', msg)

    def greeting(self, name):
        self.msg = 'Здравствуйте, {}! Вот список доступных команд: /time, /wiki...'.format(name)

    def wiki_search(self, request):
        try:
            return 'Вот результат Вашего запроса! {}'.format(wikipedia.summary(request)).split('\n')[0]
        except wikipedia.exceptions.PageError:
            return 'К сожалению, информация по Вашему запросу не была найдена.'

        except wikipedia.exceptions.DisambiguationError as error:
            if len(error.options) != 0:
                return 'Ваш запрос имеет несколько значений, представленных далее. ' \
                      '{}. Для получения результата попробуйте описать ' \
                       'искомое поточнее.'.format(', '.join(error.options))
            else:
                return 'К сожалению, что-то пошло не так, и Википедия не дала ответа на Ваш запрос.'

    def current_weather(self):
        pass

    def chatting(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                vk = self.vk_session.get_api()
                user = vk.users.get(user_ids=user_id)[0]
                name, surname = user["first_name"], user['last_name']
                msg = event.obj.message['text']
                self.writer_msg(name, surname, msg)
                msg = msg.lower()
                if msg[0:5] in self.commands:
                    if msg == '/time':
                        answer = self.current_time()
                    elif msg[0:5] == '/wiki':
                        vk.messages.send(user_id=user_id,
                                         message='Выполняется поиск...',
                                         random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format('Выполняется поиск...'))
                        answer = self.wiki_search(msg.lstrip('/wiki '))
                    vk.messages.send(user_id=user_id,
                                     message=answer,
                                     random_id=random.randint(0, 2 ** 64))
                    print('Я: {}\n'.format(answer))
                else:
                    self.greeting(name)
                    vk.messages.send(user_id=user_id,
                                     message=self.msg,
                                     random_id=random.randint(0, 2 ** 64))
                    print('Я: {}\n'.format(self.msg))


if __name__ == '__main__':
    goliath = Goliath()