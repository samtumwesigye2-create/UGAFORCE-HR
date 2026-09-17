from pathlib import Path

p = Path(__file__).with_name("dashboard.html")
s = p.read_text(encoding="utf-8")

# The root page remains the secure sign-in surface. Once an authenticated
# session has been validated, the mobile Workforce Command screen becomes
# the default home instead of the legacy HR Command Center.
old = "showApp();const s=await fetch('/health').then(r=>r.json());q('status').innerHTML=s.database&&s.database.connected?'<span class=\"dot ok\"></span>API online • PostgreSQL connected':'<span class=\"dot\"></span>Database unavailable';showView('home');await loadHome()"
new = "showApp();const s=await fetch('/health').then(r=>r.json());q('status').innerHTML=s.database&&s.database.connected?'<span class=\"dot ok\"></span>API online • PostgreSQL connected':'<span class=\"dot\"></span>Database unavailable';location.replace('/modules');return"

if old in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
