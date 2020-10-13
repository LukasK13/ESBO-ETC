import percache

cache = percache.Cache("cache")
cache.clear(3600 * 24)
