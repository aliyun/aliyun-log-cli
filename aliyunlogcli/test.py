from aliyunlogcli.config import SUPPORT_LIST
import itertools

if __name__ == '__main__':
    lists = SUPPORT_LIST.values()
    result = [i for j in lists for i in j]
    print(result)