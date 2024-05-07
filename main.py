import bson
import datetime
import telebot

with open('sample_collection.bson', 'rb') as file:
    DATA = sorted(bson.decode_all(file.read()), key=lambda x: x['dt'])



prompt = {
   "dt_from": "2022-02-01T00:00:00",
   "dt_upto": "2022-02-02T00:00:00",
   "group_type": "hour"
}

prompt['dt_from'] = datetime.datetime.strptime(prompt['dt_from'], '%Y-%m-%dT%H:%M:%S')
prompt['dt_upto'] = datetime.datetime.strptime(prompt['dt_upto'], '%Y-%m-%dT%H:%M:%S')

def filter_by_dt(data, dt_from, dt_upto):
    return [x for x in data if dt_from <= x['dt'] <= dt_upto]

formats = {
        'hour': '%Y-%m-%dT%H:00:00',
        'day': '%Y-%m-%dT00:00:00',
        'month': '%Y-%m-01T00:00:00',
        'year': '%Y-01-01T00:00:00',
    }

def group_by(data, group_type):
    fmt = formats
    dataset = [0]
    labels = [data[0]['dt'].strftime(fmt[group_type])]
    curattr = getattr(data[0]['dt'],group_type)
    while len(data):
        if getattr(data[0]['dt'], group_type) == curattr:
            dataset[-1]+=data.pop(0)['value']
        else:
            labels.append(data[0]['dt'].strftime(fmt[group_type]))
            curattr = getattr(data[0]['dt'],group_type)
            dataset.append(data.pop(0)['value'])
    return {'dataset':dataset, 'labels':labels}

def fill_in_blanks(data, group_type, dt_from, dt_upto):
    fmt = formats
    labels = []
    dt = dt_from
    if group_type != 'month':
        while dt <= dt_upto:
            labels.append(dt.strftime(fmt[group_type]))
            dt += datetime.timedelta(**{group_type+'s':1})
    else:
        while dt <= dt_upto:
            labels.append(dt.strftime(fmt[group_type]))
            dt += datetime.timedelta(days=30)
    for i in range(len(labels)):
        if labels[i] not in data['labels']:
            data['dataset'].insert(i, 0)
            data['labels'].insert(i, labels[i])
    return data


print(fill_in_blanks(group_by(filter_by_dt(DATA, prompt['dt_from'], prompt['dt_upto']), prompt['group_type']), prompt['group_type'], prompt['dt_from'], prompt['dt_upto']))