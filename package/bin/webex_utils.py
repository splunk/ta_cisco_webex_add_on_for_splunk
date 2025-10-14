from datetime import datetime, timedelta, timezone

def get_time_span(opt_start_time, opt_end_time, last_timestamp):
    start_time = None
    end_time = None
        
    # get the last timestamp saved        
    if last_timestamp is None:
        start_time = opt_start_time
    else:
        # add 1 more second to avoid duplicates
        start_time = (
            datetime.strptime(last_timestamp, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        
    # set up end time
    now = datetime.now(timezone.utc)

    if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) < now:
        end_time = opt_end_time
    else:
        end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
    if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ"):
        return None, None
    
    return start_time, end_time