from arena.source_fetch import fetch,REPOS
if __name__ == "__main__":
    for item in REPOS.items(): print(fetch(item),flush=True)
