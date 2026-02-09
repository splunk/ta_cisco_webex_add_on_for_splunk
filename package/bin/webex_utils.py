from datetime import datetime, timedelta, timezone

def change_date_format(date_str, current_format, new_format):
    if not date_str:
        return None
    
    dt = datetime.strptime(date_str, current_format).strftime(new_format)
    
    if "." in dt:
        return dt[:-4] + 'Z'
    
    return dt

def get_time_span(opt_start_time, opt_end_time, last_run_timestamp, date_format):
    start_time = None
    end_time = None
    
    now = datetime.now(timezone.utc)
    
    # check if this is the first run    
    if last_run_timestamp is None:
        # use the provided start time if available, otherwise, use the current time minus one minute.
        if opt_start_time:
            start_time = opt_start_time
        else:
            start_time = (now - timedelta(minutes=1)).strftime(date_format)
    else:
        # use the last time run as the start time
        start_time = (datetime.strptime(last_run_timestamp, date_format) + timedelta(seconds=1)).strftime(date_format)
        if "." in date_format:
            start_time = start_time[:-4]+"Z"
        
    # if end time is provided and it is earlier than the current time, then it is good to be used as a param, otherwise, if the arg is not passed use the current time as the end time
    if opt_end_time and datetime.strptime(opt_end_time, date_format).replace(tzinfo=timezone.utc) < now:
        end_time = opt_end_time
    else:
        end_time = now.strftime(date_format)[:-4]+"Z"
    
    # if the start time is after the end time the ingestion already finished
    if datetime.strptime(start_time, date_format) > datetime.strptime(end_time, date_format):
        return None, None
    
    return start_time, end_time