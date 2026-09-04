def search_paper(
    query: str,
    top_k: int = 3
) -> list[str]:

    if not query.strip():
        raise ValueError("query不能为空")

    if top_k <= 0:
        raise ValueError("top_k必须大于0")

    result: list[str] = []

    for i in range(1, top_k + 1):
        paper = f"{query} Paper {i}"
        result.append(paper)

    return result


try:
    results = search_paper(
        query="Agent",
        top_k=-1
    )

    print(results)

except ValueError as e:
    print(f"参数错误：{e}")