import re

headers = ["hostname", "ios", "platform"]

data = [
    ("R1", "12.4(24)T1", "Cisco 3825"),
    ("R2", "15.2(2)T1", "Cisco 2911"),
    ("SW1", "12.2(55)SE9", "Cisco WS-C2960-8TC-L"),
]

def convert_to_dict(h,d):
    return[dict(zip(headers,i)) for i in d]


if __name__ == "__main__":

    print(convert_to_dict(headers,data))
