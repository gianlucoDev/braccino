from json import JSONDecoder, JSONDecodeError


def json_iter(source):
    decoder = JSONDecoder()
    buffer = ''

    for data in source:
        buffer += str(data)
        buffer = buffer.strip()

        try:
            item, i = decoder.raw_decode(buffer)
            buffer = buffer[i:]
            yield item
        except JSONDecodeError:
            pass
