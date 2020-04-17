import vk_api, random, pytz, wikipedia, sqlite3, requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime


class Goliath():
    def __init__(self, token='4780dffe7455f6914472013e2b31e5659c57325d768e6548f5e9f55986eeb9d371a3d34b8bc4d24b11a9b',
                 group_id='193261610'):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.msg = 'Привет,{} вот список команд: /time, /wiki...'
        self.commands = ['/time', '/wiki', '/weat', '/regi', '/tran']
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
        self.msg = 'Здравствуйте, {}! Вот список доступных команд: /time, /wiki, /weat, /regi, /tran. ' \
                   'Примеры использования: /time, /wiki слон, /weat Тула, /regi, /tran hello.'.format(name)

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

    def current_weather(self, city_id=480562):
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

    def translation(self, word):
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
        key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97'
        lang = 'en-ru'
        r = requests.post(url, data={'key': key, 'text': word, 'lang': lang}).json()
        return r['text']

    def chatting(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message['from_id']
                vk = self.vk_session.get_api()
                user = vk.users.get(user_ids=user_id)[0]
                name, surname = user["first_name"], user['last_name']
                msg = event.obj.message['text']
                self.writer_msg(name, surname, msg)
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
                        if len(msg) > 1:
                            city_id = self.get_city_id(msg)
                            answer = self.current_weather(city_id)
                        else:
                            answer = self.current_weather()

                    elif msg[0:5] == '/regi':
                        answer = Registration(vk, user_id, msg).form()

                    elif msg[0:5] == '/tran':
                        msg = msg.lstrip('/tran ')
                        answer = self.translation(msg)

                    if msg[0:5] == '/regi' and answer[0] is True:
                        vk.messages.send(user_id=user_id,
                                         message=answer[1],
                                         attachment='foreign_files/ordinary.jpg',
                                         random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format(answer))
                    else:
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
    def __init__(self, vk, user_id, info):
        self.user_id = user_id
        self.vk = vk
        self.info = info.lstrip('/regi ').split(', ')
        msg = 'Регистрация начнётся через пару секунд...'
        self.vk.messages.send(user_id=self.user_id,
                              message=msg,
                              random_id=random.randint(0, 2 ** 64))


    def form(self):
        con = sqlite3.connect('Foreign_files/Goliath_users.db')
        cur = con.cursor()

        self.ids = cur.execute("""SELECT vk_id FROM Users""").fetchall()
        self.ids = list(map(lambda x: str(x[0]), self.ids))

        if str(self.user_id) not in self.ids:
            self.logins = cur.execute("""SELECT goliath_login FROM Users""").fetchall()
            self.logins = list(map(lambda x: str(x[0]), self.logins))

            current_login = self.info[0].lower()
            if current_login in self.logins:
                con.close()
                return 'Такой логин уже есть.'
            else:
                if len(self.info) < 3:
                    return 'Недостаточно данных'
                password = self.check_password(self.info[1])
                if password[0] is True:
                    age = self.check_age(self.info[2])
                    if age[0] is True:
                        cur.execute("""INSERT INTO Users(age, goliath_login, goliath_password, vk_id)
                         VALUES(?, ?, ?, ?)""", (age[1], current_login, password[1], self.user_id))
                        con.commit()
                        con.close()
                        msg = f'Ваш аккаунт успешно зарегистрирован. Ваш логин: {current_login}.'
                        return (True, msg)
                    else:
                        con.close()
                        return age
                else:
                    con.close()
                    return password
        else:
            return 'Ваш аккаунт уже зарегистрирован в системе'

        con.close()

    def check_password(self, password):
        up = 0
        down = 0
        if len(password) >= 6:
            for i in range(len(password)):
                if password[i - 1].isupper():
                    up += 1
                elif password[i - 1].islower():
                    down += 1
                if down > 0 and up > 0:
                    break

            if up > 0 and down > 0:
                if password.isalpha() is True:
                    return 'Пароль состоит только из букв'
                elif password.isdigit() is True:
                    return 'Пароль состоит только из цифр'
                else:
                    return (True, password)
            elif up == 0 and down == 0:
                return 'В пароле нет букв'

            else:
                return 'Пароль состоит только из букв одного регистра'
        else:
            return 'Недостаточная длина пароля'

    def check_age(self, age):
        try:
            age = int(age)
            if age < 0:
                return 'К сожалению, Вы ещё не родились'
            if age > 150:
                return 'К сожалению, данный возраст ещё не был зафиксирован. Сообщите нам, если Вы попали в ' \
                       'Кингу Рекородов Гиннесса'
            return (True, age)
        except Exception:
            return 'Указан некорректный возраст'


if __name__ == '__main__':
    goliath = Goliath()