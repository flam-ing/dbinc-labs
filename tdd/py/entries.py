"""방명록 목록을 다루는 작은 함수예요."""


def add_entry(entries, name, message):
    # 목록 맨 뒤에 새 글을 붙인 새 목록을 돌려줘요.
    return [*entries, {"name": name, "message": message}]
