from argparse import ArgumentParser
from socket import gaierror, timeout
from imap import Client


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ssl', action='store_true',
                        help='Использовать SSL')
    parser.add_argument('-s', '--server', default='imap.mail.ru:143',
                        help='Сервер и порт')
    parser.add_argument('-n', nargs='*', default=['-1'],
                        help='Интервал')
    parser.add_argument('-u', '--user', help='Имя пользователя')
    args = parser.parse_args().__dict__
    try:
        Client(**args).run()
    except ValueError as e:
        print(e)
        exit(1)
    except gaierror:
        print('Не удалось подключить сервер (DNS Error)')
        exit(1)
    except timeout:
        print('Не удалось получить ответ от сервера')
        exit(1)
    except KeyboardInterrupt:
        print('Terminated.\n')
        exit()
    except IndexError:
        print('')
        exit()
    except TypeError as e:
        print(e)
        exit()
