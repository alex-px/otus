#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short
# '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
# '$status $body_bytes_sent "$http_referer" '
#
#
#
# '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
# 1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390

# логи некоего веб-сервиса пишутся в указанном формате
# семпл лога: nginx-access-ui.log-20170630.gz
# лог ротируется раз в день
# некоторые страниы тупят и долго грузятся, нужно разобраться
# для этого нужен скрипт, который обрабатывает при запуске последний лог в LOG_DIR
# лог может быть plain и gzip
# если удачно обработал, то работу не переделывает при повторном запуске
# в результате работы должен получится ответ как в report-2017.06.30.html
# скрипт читает лог, парсит нужные поля, считает необходимую статистику по url'ам и рендерит шаблон report.html
# в шаблоне нужно только подставить `$table_json
# Готовые отчеты лежат в REPORT_DIR
# Доп задания
# убрать time_avg, заменить time_med на time_p50, добавить time_p95, time_p99 (50, 95 и 99 перцентиль)
# добавить возможность запуска, при котором передается путь до лога, который нужно обработать
# python log_analyzer.py –log_path=/some/path/to/log.gz
# добавить возможность сохранять отчет в json, без рендера шаблона

from os import listdir, path
from collections import defaultdict
import re
import gzip

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def date_from_name(name):
    """
    Returns int representation of date from name
    E.g.: for nginx-access-ui.log-20170629.gz returns 20170629
    """
    return int(name.split('-')[-1][:8])


def find_newest(path_to_search, sort_func):
    """
    Finds the newest log file by date in given path.
    Logs are supposed to be .gz or plain text.
    :return: Path to the newest log file
    """
    file_name = max((name for name in listdir(path_to_search)), key=sort_func)
    return path.join(path_to_search, file_name)


def lines_gen(file_name):
    if file_name.endswith(".gz"):
        _open = gzip.open
    else:
        _open = open
    with _open(file_name) as fh:
        while True:
            line = fh.readline()
            if not line:
                break
            yield line


def broadcast(source, consumers):
    for item in source:
        for c in consumers:
            c.send(item)
    for c in consumers:
        try:
            c.send(None)
        except StopIteration:
            pass


def consumer(func):
    def start(*args,**kwargs):
        c = func(*args,**kwargs)
        c.next()
        return c
    return start


@consumer
def time_count(total):
    # total = 0
    while True:
        r = (yield)
        if r is None:
            break
        total[r['url']] = total.get(r['url'], 0.0) + (float(r['request_time']) if r != '-' else 0)
    #print "Total time ", total


def main():
    newest = find_newest(config['LOG_DIR'], date_from_name)

    pattern = r'^(.+\]) \"(\S+) (\S+) (\S+)\" (.+) (\S+)$'
    compiled_pattern = re.compile(pattern)

    lines = lines_gen(newest)
    groups = (compiled_pattern.match(line) for line in lines)
    tuples = (g.groups() for g in groups if g)
    columns = (
        'dummy', 'method', 'url', 'protocol', 'dummy2', 'request_time')

    log = (dict(zip(columns, t)) for t in tuples)
    total = {}
    broadcast(log, [time_count(total), ])
    g = sorted(((v, k) for k, v in total.items()), reverse=True)


if __name__ == "__main__":
    main()