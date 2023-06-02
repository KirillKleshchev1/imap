from socket import AF_INET, SOCK_STREAM, gaierror, socket, timeout
from threading import Lock
import base64
import getpass
import ssl
from subsidiary import get_body, get_headers, receive_message, send_message


class Client:
    def __init__(self, ssl, server, n, user):
        self.ssl = ssl
        server_port = server.split(':')
        if len(server_port) != 2:
            raise ValueError('Некорректный адрес')
        self.server = server_port[0]
        self.port = int(server_port[1])
        if len(n) == 0 or len(n) > 2 or len(n) == 2 and \
                (int(n[0]) > int(n[1]) or int(n[0]) < 0 or int(n[1]) < 0):
            raise ValueError('Некорректный интервал писем')
        self.interval = n
        self.user = user
        self.name = 'A001'
        self.print_lock = Lock()

    def modify_login_and_password(self):
        return base64.b64encode(f'{self.user}{getpass.getpass()}'
                                .encode('utf-8')).decode('utf-8')

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.connect((self.server, self.port))
            sock.settimeout(1)
            try:
                receive_message(sock)
            except timeout:
                raise gaierror
            if self.ssl:
                send_message(sock, f'{self.name} STARTTLS\n')
                receive_message(sock)
                sock = ssl.wrap_socket(sock)
            else:
                print('Вы находитесь в открытом соединении!')
            send_message(sock, f'{self.name} LOGIN '
                               f'{self.user} '
                               f'{getpass.getpass()}\n')
            login_response = receive_message(sock)
            if 'NO' in login_response:
                raise str(login_response[5:])
            send_message(sock, f'{self.name} LIST \"\" *\n')
            list_response = receive_message(sock)
            folders = [f[f.find('/')+4:-2]
                       for f in list_response.split('\n')[:-1]]
            for folder in folders[:-1]:
                self.select_group(sock, folder)

    def select_group(self, sock, folder):
        number_str = ''
        while 'EXISTS' not in number_str:
            send_message(sock, f'{self.name} SELECT {folder}\n')
            number_str = receive_message(sock).split('\n')[1]
        print(f'{folder} FOLDER')
        letters_number = int(number_str.split(' ')[1])
        letter_range = self.get_range(letters_number)
        for i in letter_range:
            send_message(sock, f'{self.name} FETCH {i} '
                               f'(FLAGS FULL)\n')
            headers = receive_message(sock)
            if not headers or '(nothing matched)' in headers:
                break
            get_headers(headers)
            get_body(headers)
        print()

    def get_range(self, letters_number):
        if self.interval == ['-1']:
            return range(letters_number, 0, -1)
        if len(self.interval) == 1:
            return range(letters_number,
                         max(0, letters_number - int(self.interval[0])), -1)
        return range(letters_number - int(self.interval[0]) + 1,
                     letters_number - int(self.interval[1]), -1)
