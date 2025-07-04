import re
log = open("access.log.txt", "r")

lines = [re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line) for line in log.readlines()]
dates = [line[3][1:12] for line in lines]
date_counts = []
for date in set(dates):
    date_counts.append([date,dates.count(date)])

pages = [line[5] for line in lines]
page_counts = []
for page in set(pages):
    if page[:14] == "\"GET /allocate":
        page_counts.append([page,pages.count(page)])
page_counts.sort(key=(lambda x: x[1]), reverse=True)

# for page in page_counts:
#     print(page[0], page[1])


users = [line[9] for line in lines]
user_counts = []
for user in set(users):
    user_counts.append([user,users.count(user)])
user_counts.sort(key=(lambda x: x[1]), reverse=True)

#for user in user_counts:
#    print(user[0], user[1])
#print(users[:10])


ips = [line[0] for line in lines]
ip_counts = []
for ip in set(ips):
    ip_counts.append([ip,ips.count(ip)])
ip_counts.sort(key=(lambda x: x[1]), reverse=True)

#for ip in ip_counts:
#    print(ip[0], ip[1])

response_codes = [line[6] for line in lines]
code_counts = []
for code in set(response_codes):
    code_counts.append([code,response_codes.count(code)])
code_counts.sort(key=(lambda x: x[1]), reverse=True)

for code in code_counts:
    print(code[0], code[1])

