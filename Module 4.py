import math

inputCoeff = [1.00, -5.68, 8.5408]

def qRoot(coeff):
    a = coeff[0]
    b = coeff[1]
    b2 = pow(b, 2)
    c = coeff[2]
    ac4 = 4 * a * c
    discriminant = b2 - ac4
    complex = False
    if discriminant < 0 : complex = True
    if complex : discriminant = discriminant * (-1)
    if complex:
        radical = (math.sqrt(discriminant) * 1j)/(2*(a))
    else: 
        radical = (math.sqrt(discriminant))/(2*(a))
    realPart = (-b)/(2*(a))
    plusRoot = realPart + radical
    minusRoot = realPart - radical
    return [plusRoot, minusRoot]

[a, b] = qRoot(inputCoeff)
print(a,b)

def recip(denom):
    dec = 1/denom
    return dec

for i in range(2, 11):
    d = recip(i)
    print(d)