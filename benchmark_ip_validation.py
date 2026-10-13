import time
from ipaddress import AddressValueError, ip_address

providers = ["8.8.8.8", "1.1.1.1", "9.9.9.9", "invalid_ip", "192.168.1.1"] * 20
domains = ["example.com", "google.com", "github.com"]
iterations = 100

def original_validation(provider_ip):
    try:
        ip_address(provider_ip)
        return True
    except (AddressValueError, ValueError):
        return False

invalid_providers = set()
for p in providers:
    try:
        ip_address(p)
    except (AddressValueError, ValueError):
        invalid_providers.add(p)

def optimized_validation(provider_ip):
    if provider_ip in invalid_providers:
        return False
    return True

tasks = [(p, d) for p in providers for d in domains for _ in range(iterations)]

start = time.perf_counter()
for p, d in tasks:
    original_validation(p)
orig_time = time.perf_counter() - start

start = time.perf_counter()
for p, d in tasks:
    optimized_validation(p)
opt_time = time.perf_counter() - start

print(f"Original: {orig_time:.5f}s")
print(f"Optimized: {opt_time:.5f}s")
print(f"Improvement: {orig_time / opt_time:.2f}x")
