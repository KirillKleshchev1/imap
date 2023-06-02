import base64
from socket import timeout


def get_address(addr_str):
    source_name = addr_str[0]
    if source_name[1:11] == '=?utf-8?B?':
        source_name = base64.b64decode(source_name[11:-1]) \
            .decode('utf-8')
    else:
        source_name = ' '.join(addr_str
                               [:addr_str.index("NIL")])[1:-1] \
            if "NIL" in addr_str else ''

    return f'{addr_str[-2][1:-1]}@{addr_str[-1][1:-1]} ' \
           f'<{source_name}>'


def send_message(sock, message):
    sock.send(message.encode('utf-8'))


def receive_message(sock):
    data = bytearray()
    try:
        while True:
            received_data = sock.recv(1024)
            data.extend(received_data)
            if len(received_data) < 1024:
                break
    except timeout:
        pass
    finally:
        return data.decode('utf-8')


def get_body(headers):
    body = headers[headers.find('BODY') + 7:headers.rfind(')')]
    body_parts = body.split(')(')
    attaches = []
    for part in body_parts:
        if part.find("name") == -1:
            continue
        name = part[part.find("name") + 7:part.find('")')]
        encoding = '"base64"' if '"base64"' in part \
            else '"8bit"'
        attach_size = int(part[part.find(encoding) + 9:].split(' ')[0].replace(')', ''))
        attaches.append((name, attach_size))
    print(f'{len(attaches)} attaches: {attaches}')


def get_headers(headers):
    date_str = headers[headers.find("INTERNALDATE") + 14:]
    date = date_str[:date_str.find('"')]
    size_str = headers[headers.find("RFC822.SIZE") + 12:]
    size = size_str[:size_str.find(' ')]
    envelope = headers[headers.find("ENVELOPE") + 9:
                       headers.find('BODY') - 1]
    subj_str = envelope[36:] if envelope[35:38] != 'NIL' \
        else "- "
    subj = subj_str[:subj_str.find('"')]
    if subj[:10] == '=?utf-8?B?':
        subj = base64.b64decode(subj[10:]).decode('utf-8')
    subj = subj.replace('\n', '\\n')
    from_str = envelope[envelope.find('((') + 2:
                        envelope.find('))')].split(' ')
    from_addr = get_address(from_str)
    to_str = envelope[envelope.rfind('((') + 2:
                      envelope.rfind('))')].split(' ')
    to_addr = get_address(to_str)
    print(f'From: {from_addr} To: {to_addr} Subject: {subj} '
          f'{date} Size: {size}')
