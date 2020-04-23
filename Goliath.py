# import of necessary libraries
import vk_api, random, pytz, wikipedia, sqlite3, requests, json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime


# class of bot Goliath
class Goliath():
    def __init__(self, token='4780dffe7455f6914472013e2b31e5659c57325d768e6548f5e9f55986eeb9d371a3d34b8bc4d24b11a9b',
                 group_id='193261610'):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.msg = ''
        self.commands = ['/time', '/wiki', '/weat', '/regi', '/tran', '/help', '/news', '/dele', '/stop']
        self.tz = pytz.timezone('Europe/Moscow')
        self.days_of_week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница',
                        'суббота', 'воскресенье']
        self.app_id = "26fb73e2e5bbaf9382094cfdba8dee70"
        # 10 languages for translator
        self.langs = {'ру': 'ru',
                      'ан': 'en',
                      'ла': 'la',
                      'фр': 'fr',
                      'ис': 'es',
                      'ит': 'it',
                      'ки': 'zh',
                      'по': 'pl',
                      'ук': 'uk',
                      'не': 'de'}
        self.greetings = ['Приветствую', 'Здравствуйте']
        self.news_url = 'https://newsapi.org/v2/top-headlines?country=ru&apiKey=cd2faf3e82e4424bb5905f5247364b4b'
        self.order = {}
        self.chatting()

    # function returning current time
    def current_time(self):
        date = datetime.now(self.tz)
        day = self.days_of_week[date.weekday()]
        time = str(date)[11:16]
        date = str(date)[0:10]
        return 'Сегодня {}, {}. Московское время: {}.'.format(date, day, time)

    # function writing all dialogs into run-part
    def writer_msg(self, name, surname, msg):
        print('Новое сообщение:')
        print(name, surname + ':', msg)

    def greeting(self, name):
        self.msg = '{}, {}! Вот список доступных команд: /time, /wiki, /weat, /regi,' \
                   ' /tran, /help, /news.'.format(random.choice(self.greetings), name)

    # function using library of Wikipedia to get some info about input-data
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

    # function getting id of city from OpenWeatherMap.org using a name of city
    def get_city_id(self, city):
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

    # function getting weather from OpenWeatherMap.org using an id of city
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

    # function using API of Yandex to translate the input-phrases
    def translation(self, word, lang='ру-ан'):
        url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
        key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97'
        lang = lang.split('-')
        primary = self.langs[lang[0]]
        secondary = self.langs[lang[1]]
        trans = f'{primary}-{secondary}'
        r = requests.post(url, data={'key': key, 'text': word, 'lang': trans}).json()
        return r['text']

    def picture(self, num):
        return User.picture(user, num)

    # function with link leading to help-topic
    def help(self):
        return 'https://vk.com/topic-193261610_41497800'

    # function returning keyboard into chat
    def new_keyboard(self):
        keyboard = {
            'one_time': True,
            'buttons': [[{'action': {'type': 'text', 'label': '/regi', 'payload': {'button': 0}}, 'color': 'positive'},
                         {'action': {'type': 'text', 'label': '/news', 'payload': {'button': 1}}, 'color': 'primary'},
                         {'action': {'type': 'text', 'label': '/tran', 'payload': {'button': 2}}, 'color': 'primary'}],
                        [{'action': {'type': 'text', 'label': '/time', 'payload': {'button': 3}}, 'color': 'primary'},
                         {'action': {'type': 'text', 'label': '/weat', 'payload': {'button': 4}}, 'color': 'primary'},
                         {'action': {'type': 'text', 'label': '/help', 'payload': {'button': 5}}, 'color': 'positive'}],
                        [{'action': {'type': 'text', 'label': '/stop', 'payload': {'button': 6}}, 'color': 'negative'}]],
                        'inline': False}

        return keyboard

    # function getting news from newsapi.org
    def news(self):
        try:
            response = requests.get(self.news_url)
            news = json.loads(response.text)
            new = random.choice(news['articles'])
            return new['title']
        except:
            return 'Произошла ошибка'

    # the main function of all, checks messages and acts with users
    def chatting(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                keyboard = self.new_keyboard()

                user_id = event.obj.message['from_id']
                vk = self.vk_session.get_api()
                user = vk.users.get(user_ids=user_id)[0]
                name, surname = user["first_name"], user['last_name']
                msg = event.obj.message['text']
                self.writer_msg(name, surname, msg)
                image = ''
                # if there is command then Goliath will commit it
                if msg[0:5] in self.commands:

                    if msg == '/time':
                        answer = self.current_time()

                    elif msg[0:5] == '/wiki':
                        vk.messages.send(user_id=user_id,
                                         message='Выполняется поиск...',
                                         random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format('Выполняется поиск...'))
                        answer = self.wiki_search(msg[6:])

                    elif msg[0:5] == '/weat':
                        msg = msg.lstrip('/weat ')
                        if len(msg) > 1:
                            city_id = self.get_city_id(msg)
                            answer = self.current_weather(city_id)
                        else:
                            answer = self.current_weather()

                    elif msg[0:5] == '/regi':
                        answer = Registration(vk, user_id).check_id()
                        if answer:
                            answer = 'Введите желаемый логин!'
                            self.order[user_id] = ('/regi', user_id)
                        else:
                            answer = 'Вы уже зарегистрированы в системе!'

                    elif msg[0:5] == '/help':
                        answer = self.help()

                    elif msg[0:5] == '/stop':
                        del self.order[user_id]
                        answer = 'Все операции остановлены.'

                    elif msg[0:5] == '/news':
                        answer = self.news()

                    elif msg[0:5] == '/dele':
                        vk.messages.send(user_id=user_id,
                                              message='Проверка существованяи аккаунта...',
                                              random_id=random.randint(0, 2 ** 64))
                        answer = Registration(vk, user_id).check_id()
                        if not answer:
                            answer = 'Для подтверждения введите пароль!'
                            self.order[user_id] = ('/dele', user_id)
                        else:
                            answer = 'Вы ещё не зарегистрированы в системе!'

                    elif msg[0:5] == '/tran':
                        self.order[user_id] = '/tran'
                        msg = msg[5:].lstrip()
                        if len(msg) == 5:
                            if (msg.split('-')[0] and msg.split('-')[1]) in self.langs:
                                answer = 'Введите слово или фразу для перевода.'
                                self.order[user_id] = ('/tran', msg)
                            else:
                                answer = 'Этот язык я ещё не изучил.'
                        elif len(msg) == 0:
                            answer = 'Введите слово или фразу для перевода.'
                            self.order[user_id] = ('/tran', 'ру-ан')
                        else:
                            answer = 'Этот язык я ещё не изучил.'

                    try:
                        if image != '':
                            vk.messages.send(user_id=user_id,
                                             message=answer[1],
                                             attachment=image,
                                             keyboard=json.dumps(keyboard),
                                             random_id=random.randint(0, 2 ** 64))
                            print('Я: {}\n'.format(answer[1]))
                        else:
                            vk.messages.send(user_id=user_id,
                                             message=answer,
                                             keyboard=json.dumps(keyboard),
                                             random_id=random.randint(0, 2 ** 64))
                            print('Я: {}\n'.format(answer))

                    except Exception:
                        e = 'Произошла ошибка. Попробуйте снова.'
                        vk.messages.send(user_id=user_id,
                                         message=e,
                                         random_id=random.randint(0, 2 ** 64))
                # here is condition for multistep commands
                else:
                    if user_id in self.order:
                        command = self.order[user_id]
                        if len(command) == 2:
                            if command[0] == '/tran':
                                lang = command[1]
                                answer = self.translation(msg, lang)
                                del self.order[user_id]

                            elif command[0] == '/regi':
                                id = command[1]
                                answer = Registration(vk, id).check_login(msg)
                                if answer[0] is True:
                                    answer = f'Ваш логин: {msg.lower()}. Придумайте пароль! Он должен содержать минимум' \
                                             f' 6 символов, обязательны ' \
                                             'цифры, буквы верхнего и нижнего регистров.'
                                    self.order[user_id] = ('/logi', msg)
                                else:
                                    answer = 'Такой логин уже есть! Попробуйте снова.'
                                    image = self.picture(1)

                            elif command[0] == '/logi':
                                login = command[1]
                                answer = Registration(vk, user_id).check_password(msg)
                                if answer[0]:
                                    answer = 'Пароль принят! Введите Ваш возраст!'
                                    image = self.picture(2)
                                    self.order[user_id] = ('/pass', (login, msg))
                                else:
                                    answer = answer[1]
                                    image = self.picture(1)

                            elif command[0] == '/pass':
                                login = command[1][0]
                                password = command[1][1]
                                info = (login, password, msg)
                                answer = Registration(vk, user_id).check_age(msg)
                                if answer[0]:
                                    answer = 'Заявка принята! Регистрация окончена!'
                                    Registration(vk, user_id).filling(info)
                                    del self.order[user_id]
                                    image = self.picture(0)
                                else:
                                    answer = answer[1]
                                    image = self.picture(1)

                            elif command[0] == '/dele':
                                answer = Registration(vk, user_id).delete_account(msg)
                                if answer[0] is True:
                                    answer = 'Ваш аккаунт будет удалён! Спасибо, что были с нами!'
                                    del self.order[user_id]
                                    image = self.picture(2)
                                else:
                                    answer = answer[1]
                                    image = self.picture(1)

                        if image:
                            vk.messages.send(user_id=user_id,
                                             message=answer,
                                             keyboard=json.dumps(keyboard),
                                             attachment=image,
                                             random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=user_id,
                                             message=answer,
                                             keyboard=json.dumps(keyboard),
                                             random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format(answer))
                    # if message without command then default message will be returned
                    else:
                        self.greeting(name)
                        vk.messages.send(user_id=user_id,
                                         message=self.msg,
                                         keyboard=json.dumps(keyboard),
                                         random_id=random.randint(0, 2 ** 64))
                        print('Я: {}\n'.format(self.msg))


# class helping to register in system(database)
class Registration():
    def __init__(self, vk, user_id):
        self.user_id = user_id
        self.vk = vk
        self.con = sqlite3.connect('Foreign_files/Goliath_users.db')
        self.cur = self.con.cursor()

    def check_id(self):
        ids = self.cur.execute("""SELECT vk_id FROM Users""").fetchall()
        ids = list(map(lambda x: str(x[0]), ids))
        if str(self.user_id) not in ids:
            return True
        else:
            self.con.close()
            return False

    def check_login(self, login):
        logins = self.cur.execute("""SELECT goliath_login FROM Users""").fetchall()
        logins = list(map(lambda x: str(x[0]), logins))
        self.vk.messages.send(user_id=self.user_id,
                              message='Проверка логина...',
                              random_id=random.randint(0, 2 ** 64))

        if login.lower() in logins:
            return (False, 'Такой логин уже есть.')
        else:
            return (True,)

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
                    return (False, 'Пароль состоит только из букв!')
                elif password.isdigit() is True:
                    return (False, 'Пароль состоит только из цифр!')
                else:
                    return (True, )
            elif up == 0 and down == 0:
                return (False, 'В пароле нет букв!')

            else:
                return (False, 'Пароль состоит только из букв одного регистра!')
        else:
            return (False, 'Недостаточная длина пароля!')

    def check_age(self, age):
        try:
            age = int(age)
            if age < 0:
                return (False, 'К сожалению, Вы ещё не родились.')
            if age > 150:
                return (False, 'К сожалению, данный возраст ещё не был зафиксирован. Сообщите нам, если Вы попали в ' \
                       'Книгу Рекордов Гиннесса.')
            return (True,)
        except Exception:
            return (False, 'Указан некорректный возраст!')

    def filling(self, info):
        self.cur.execute("""INSERT INTO Users(age, goliath_login, goliath_password, vk_id)
                                 VALUES(?, ?, ?, ?)""", (info[2], info[0], info[1], self.user_id))
        self.con.commit()
        self.con.close()

    def delete_account(self, word):
        con = sqlite3.connect('Foreign_files/Goliath_users.db')
        cur = con.cursor()

        self.ids = cur.execute("""SELECT vk_id FROM Users""").fetchall()
        self.ids = list(map(lambda x: str(x[0]), self.ids))
        if str(self.user_id) in self.ids:
            password = cur.execute("""SELECT goliath_password FROM Users
                                            WHERE vk_id = ?""", (str(self.user_id), )).fetchall()[0][0]
            print(password, word)
            self.vk.messages.send(user_id=self.user_id,
                                  message='Проверка пароля...',
                                  random_id=random.randint(0, 2 ** 64))
            if word == password:
                self.vk.messages.send(user_id=self.user_id,
                                      message='Пароль принят!',
                                      random_id=random.randint(0, 2 ** 64))
                cur.execute("""DELETE FROM Users
                                WHERE vk_id = ?""", (self.user_id, ))
                con.commit()
                con.close()
                return (True,)
            else:
                con.close()
                return (False, 'Неверный пароль - в доступе отказано!')
        else:
            con.close()
            return (False, 'Ваш аккаунт не зарегистрирован в системе!')


# class User, join into Vk as user
class User():
    def __init__(self, login, password):
        vk_session = vk_api.VkApi(login, password, auth_handler=self.auth_handler)
        self.vk = vk_session.get_api()
        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)

    # double check of authorization in Vk
    def auth_handler(self):
        key = input("Enter authentication code: ")
        remember_device = True
        return key, remember_device

    # returns the picture from hidden album of group with id 193261610(Goliath)
    def picture(self, num):
        picture = self.vk.photos.get(group_id='193261610', album_id='271816083')['items']
        owner_id = picture[num]['owner_id']
        photo_id = picture[num]['id']
        group_attachment = 'photo{}_{}'.format(owner_id, photo_id)
        return group_attachment


if __name__ == '__main__':
    # initializing of classes, creating the objects
    user = User(number, password)
    goliath = Goliath()