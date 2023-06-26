def greeting(name):
    message = f"Hello, {name} \nHow are you doing today, {name}? \nWhat are you up to later {name}?"
    print(message)

names = ['Sam', 'Jakob', 'Philip']

for name in names:
    greeting(name)

def fullname(first, last):
    full = "Hello, " + first + ' ' + last
    print(full)

fullname('Sam', 'Brodsky')
fullname('Jakob', 'Johnson')
fullname('Spencer', 'Wallace')


def add(n1, n2):
    sum = n1 + n2
    #print(f"{n1} + {n2} = {sum}")
    return sum

s1 = add(1, 2)
s2 = add(2, 3)
s3 = add(3, 5)
print(s1)


a = pow(16,(1/2))
b = pow(16, .5)
print(a)
print(b)