from datetime import datetime, date, time, timedelta


message_timestamp = datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S')


def calc_support_year_start():
    """ Calculate start of BAFA support year.
    :return:
    March, 12th the year before if today is between January, 1st and March, 11th
    March, 12th of the current year otherwise
    :rtype: unix timestamp in milliseconds
    """

    now = datetime.utcnow()
    start_day = 12
    start_month = 3
    if (now.month < start_month) or (now.month == start_month and now.day <
                                     start_day):
        start_year = now.year - 1
    else:
        start_year = now.year
    d = date(start_year, start_month, start_day)
    t = time(0, 0)
    support_year_start = round(datetime.combine(d, t).timestamp() * 1000)
    return support_year_start


def calc_term_boundaries():
    """ Calculate begin and end of previous and ongoing terms.
    :return: begin and end of the previous and the current support year until
    today as unix milliseconds timestamps
    :rtype: tuple(int)
    """

    # Calculate timestamps for ongoing term
    begin_ongoing_term = calc_support_year_start()
    end_ongoing_term = round(datetime.combine(datetime.now().date(), time(0, 0,
                                                                          0)).timestamp()
                             * 1000)

    # Calculate timestamps for previous term
    end_prev_term = round((datetime.fromtimestamp(
        begin_ongoing_term/1000) - timedelta(days=1)).timestamp() * 1000)

    previous_year = datetime.fromtimestamp(
        begin_ongoing_term/1000).year - 1
    begin_previous_term_date = datetime.fromtimestamp(
        begin_ongoing_term/1000).date().replace(year=previous_year)
    begin_prev_term = round(datetime.combine(begin_previous_term_date,
                                             time(0, 0, 0)).timestamp() *
                            1000)

    return begin_ongoing_term, end_ongoing_term, begin_prev_term, end_prev_term


def calc_end():
    """ Calculate timestamp of end of interval. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round(datetime.utcnow().timestamp() * 1000)


def calc_support_year_start_datetime():
    """ Calculate start of BAFA support year.
    :return:
    March, 12th the year before if today is between January, 1st and March, 11th
    March, 12th of the current year otherwise
    :rtype: datetime.date in UTC
    """

    now = datetime.utcnow()
    start_day = 12
    start_month = 3
    if (now.month < start_month) or (now.month == start_month and now.day <
                                     start_day):
        start_year = now.year - 1
    else:
        start_year = now.year
    d = date(start_year, start_month, start_day)
    t = time(0, 0)
    return datetime.combine(d, t)


def calc_support_week_start():
    """ Calculate start of BAFA support week.
    :return:
    March, 12th of the current year if today is between March, 12th
    and March, 18th
    7 days back in time otherwise
    :rtype: unix timestamp in milliseconds
    """

    now = datetime.utcnow()
    if (now.month == 3) and (11 < now.day < 19):
        d = date(now.year, 3, 12)
    else:
        d = (now - timedelta(days=7)).date()
    t = now.time()
    support_week_start = round(datetime.combine(d, t).timestamp() * 1000)
    return support_week_start


def calc_two_days_back():
    """ Calculate timestamp of 48 hours back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.utcnow() - timedelta(hours=48)).timestamp() * 1000)
