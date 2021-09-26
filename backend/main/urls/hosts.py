from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(r"", "main.urls.client_api", name="default"),
    host(r"client-api", "main.urls.client_api", name="client-api"),
    host(r"dj-admin", "main.urls.dj_admin", name="dj-api"),
)
