import os
import time
os.environ['DJANGO_SETTINGS_MODULE'] = 'fits.settings'
import django

django.setup()

from django.db import connection, reset_queries
from django.conf import settings

settings.DEBUG = True

from django.test import Client
from django.contrib.auth.models import User

c = Client()
user = User.objects.filter(username="admin").first()
print(f"Admin user found: {user}")
c.force_login(user)

# Warm up
c.get("/")

reset_queries()
t0 = time.time()
resp = c.get("/employee/employee-view/")
t1 = time.time()
elapsed = (t1 - t0) * 1000

total_db_time = sum(float(q["time"]) for q in connection.queries) * 1000
print(
    f"Time: {elapsed:.0f}ms, Queries: {len(connection.queries)}, Total DB time: {total_db_time:.0f}ms"
)
# Print top 10 slowest
sorted_q = sorted(connection.queries, key=lambda x: float(x["time"]), reverse=True)
for q in sorted_q[:10]:
    print(f"  {q['time']}s: {q['sql'][:120].replace(chr(10), ' ')}")
