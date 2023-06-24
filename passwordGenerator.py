import random

def generate():
    upperCase1 = chr(random.randint(65,90))
    upperCase2 = chr(random.randint(65,90))

    lowerCase1 = chr(random.randint(97,122))
    lowerCase2 = chr(random.randint(97,122))

    digit1 = chr(random.randint(48,57))
    digit2 = chr(random.randint(48,57))

    sign1 = chr(random.randint(33,42))
    sign2 = chr(random.randint(33,42))

    password = upperCase1 + upperCase2 + lowerCase1 + lowerCase2 + digit1 + digit2 + sign1 + sign2
    
    return password

print(generate())
    