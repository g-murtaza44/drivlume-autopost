# Sleeps until the next posting slot (PKT), at most 5.5 hours. Prints "post" if a slot was reached.
import time
from datetime import datetime, timedelta, timezone
PKT = timezone(timedelta(hours=5)); SLOTS = [(9,17),(12,17),(15,17),(18,17),(21,17)]
now = datetime.now(PKT)
cands = [now.replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(days=d) for d in (0,1) for h, m in SLOTS]
nxt = min(t for t in cands if t > now)
secs = (nxt - now).total_seconds()
cap = 5.5 * 3600
time.sleep(min(secs, cap) + 30)
print("post" if secs <= cap else "wait")
