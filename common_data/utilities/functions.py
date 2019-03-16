import datetime

def apply_style(context):
    styles = {
            1: "simple",
            2: "blue",
            3: "steel",
            4: "verdant",
            5: "warm"
            }
    context['style'] = styles[context["document_theme"]]
    return context 


def extract_period(kwargs):
    n = kwargs.get('default_periods', None)
    if n and n != '0':
        deltas = {
                '1': 7,
                '2': 30,
                '3': 90,
                '4': 180,
                '5': 365
            }
        end = datetime.date.today()
        start = end - datetime.timedelta(
                days=deltas[n])
    else:
        start = datetime.datetime.strptime(
            kwargs['start_period'], "%m/%d/%Y")
        end = datetime.datetime.strptime(
            kwargs['end_period'], "%m/%d/%Y")

    return (start, end)

def time_choices(start, stop, interval, delta=False):
    """
    Creates a list of times between start and stop separated by interval.

    Inputs
    =======
        start and stop are strings that represent time in the format H:M:00.
        interval is the time to be incremented between start and stop in the
        same format as above.
        delta, boolean, whether return elements are timedeltas
    Returns:
    =======
    The function returns a list of tuples in human readable format from
    the start time up to but not including the end time. 
    either 
        [(timedelta, string), ...]
    or
        [(time, string), ...] 
    """

    times = []
    try:
        _start = datetime.datetime.strptime(start, "%H:%M:%S").time()
        _stop = datetime.datetime.strptime(stop, "%H:%M:%S").time()
        _interval = datetime.datetime.strptime(interval, "%H:%M:%S").time()
    except:
        raise Exception("the times supplied do not match the required format")

    current_time = _start
    while current_time < _stop:
        if delta:
            times.append((datetime.timedelta(hours=current_time.hour,
                                            minutes=current_time.minute),
                                                current_time.strftime("%H:%M")))
        else:
            times.append((current_time ,current_time.strftime("%H:%M")))
        
        current_time = (datetime.datetime.combine(datetime.date.today(), current_time) \
                        + datetime.timedelta(hours = _interval.hour,
                                            minutes=_interval.minute,
                                            seconds=_interval.second)).time()
    return times
