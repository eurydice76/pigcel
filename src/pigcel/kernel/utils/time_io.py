import datetime


def add_time(time, delta):

    hours, minutes = time.split('h')

    if hours[0] == '-':
        hours = int(hours)
        minutes = int(minutes)
        hours = str(24 + hours - 1)
        minutes = str(60 - minutes)
        time = 'h'.join([hours, minutes])

    d = datetime.datetime.strptime(time, '%Hh%M') + datetime.timedelta(0, delta*60)

    if d.hour >= 12:
        hour = 24 - d.hour - 1
        minute = 60 - d.minute
        return '-{}h{:02d}'.format(hour, minute)
    else:
        return '{}h{:02d}'.format(d.hour, d.minute)


if __name__ == '__main__':

    print(add_time('-0h31', 30))
