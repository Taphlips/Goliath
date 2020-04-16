import vk_api, random, pytz, wikipedia, time, requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime


class Goliath():
    def __init__(self, token='4780dffe7455f6914472013e2b31e5659c57325d768e6548f5e9f55986eeb9d371a3d34b8bc4d24b11a9b',
                 group_id='193261610'):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.msg = 'Привет,{} вот список команд: /time, /wiki...'
        self.commands = ['/time', '/wiki', '/weat', '/regi']
        self.tz = pytz.timezone('Europe/Moscow')
        self.days_of_week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница',
                        'суббота', 'воскресенье']
        self.app_id = "26fb73e2e5bbaf9382094cfdba8dee70"
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
        self.msg = 'Здравствуйте, {}! Вот список доступных команд: /time, /wiki, /weat, /regi. ' \
                   'Примеры использования: /time, /wiki слон, /weat Тула, /regi.'.format(name)

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

    def get_city_id(self, city):
        s_city = "Москва, US"
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': self.app_id})
            data = res.json()
            cities = ["{} ({})".format(d['name'], d['sys']['country'])
                      for d in data['list']]
            print("city:", cities)
            city_id = data['list'][0]['id']
            print(city_id)
            return city_id
        except Exception as e:
            print("Exception (find):", e)
            pass

    def current_weather(self, city_id):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                               params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': self.app_id})
            data = res.json()
            weather = 'Температура составляет {}°C, {}.'.format(data['main']['temp'],
                                                                data['weather'][0]['description'])
            return weather
        except Exception as e:
            print("Exception (weather):", e)
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
                    elif msg[0:5] == '/weat':
                        msg = msg.lstrip('/weat ')
                        city_id = self.get_city_id(msg)
                        answer = self.current_weather(city_id)
                    elif msg[0:5] == '/regi':
                        registration = Registration(vk, user_id)

                    try:
                        vk.messages.send(user_id=user_id,
                                         message=answer,
                                         random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format(answer))
                    except Exception:
                        e = 'Произошла ошибка. Попробуйте снова.'
                        vk.messages.send(user_id=user_id,
                                         message=e,
                                         random_id=random.randint(0, 2 ** 64))
                else:
                    self.greeting(name)
                    vk.messages.send(user_id=user_id,
                                     message=self.msg,
                                     random_id=random.randint(0, 2 ** 64))
                    print('Я: {}\n'.format(self.msg))


class Registration():
    def __init__(self, vk, user_id):
        self.user_id = user_id
        self.vk = vk
        msg = 'Регистрация начнётся через пару секунд...'
        self.vk.messages.send(user_id=self.user_id,
                              message=msg,
                              random_id=random.randint(0, 2 ** 64))
        self.log_in()

    def log_in(self):


    def password(self):
        pass

    def age(self):
        pass

    def avatar(self):
        pass


if __name__ == '__main__':
    goliath = Goliath()