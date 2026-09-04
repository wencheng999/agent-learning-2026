def classify_query(query:str) ->str:
    if "最新" in query:
        return "search"
    else:
        return "chat"

def search_paper(query:str,
                 top_k:int=3) -> list[str]:
    return [
        f"{query} Paper {i}"
        for i in range(top_k)
    ]

query = "最新Agent论文"

route = classify_query(query)

print(route)

results = search_paper(
    query="Agent",
    top_k=3
)

print(results)