from datetime import datetime
import matplotlib
import matplotlib.pyplot as pyplot

def split(string):
    '''2013-05-30 07:21:25.288000: Switching state: Hopeful'''
    time, _, state = string.partition(': Switching state: ')
    try:
        date = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        date = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return date, state
    
def parse(filepath):
    date_list = []
    state_list = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            else:
                date, state = split(line)
                date_list.append(date)
                state_list.append(state)
    return date_list, state_list
    
def plot(date_list, state_list):
    state = {
        'Lonely': 1,
        'Hopeful': 2,
        'Sad': 3,
        'Choices': 4,
        'Joke': 5,
        'Happy': 6,
        'Why': 7,
        'Scared': 10
    }
    dates = matplotlib.dates.date2num(date_list)
    states = [state[s] for s in state_list]
    pyplot.plot_date(dates, states)
    pyplot.show()
    
def main():
    dates, states = parse('log-relevant-run.txt')
    plot(dates, states)
    
if __name__ == '__main__':
    main()
    