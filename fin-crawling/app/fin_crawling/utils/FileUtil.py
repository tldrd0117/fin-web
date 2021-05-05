
def changeCharSet(path):
    lines = ""
    with open(path, "r", encoding="euc-kr") as f:
        lines = f.readlines()
    with open(path, 'w', encoding="utf-8") as f:
        f.writelines(lines)
