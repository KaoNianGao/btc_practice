# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 20:55:33 2023


"""
import hashlib

P = 2**256 - 2**32 - 977
A = 0
B = 7
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


class FieldElement:
    
    def __init__(self,num,prime):
        if num >= prime or num < 0:
            error = "Num {} not in field range 0 to {}".format(num,prime-1)
            raise ValueError(error)
        self.num = num
        self.prime = prime
        
    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)
    
    def __eq__(self,other):
        if isinstance(other, type(self)):
            if other is None:
                return False
            return self.num == other.num and self.prime == other.prime
        elif isinstance(other, int):
            return self.num == other
    
    def __neq__(self,other):
        if isinstance(other, type(self)):
            if other is None:
                return True
            return self.num != other.num or self.prime != other.prime
        elif isinstance(other, int):
            return not (self.num == other)
    
    def __add__(self,other):
        #deal with int + fieldelement
        if isinstance(other, type(self)):
            if self.prime!=other.prime:
                raise TypeError("Cannot add two numbers in different Fields")
            num = (self.num + other.num) % self.prime
        elif isinstance(other, int):
            num = (self.num + other) % self.prime
        else:
            raise TypeError
        return self.__class__(num, self.prime)

    def __sub__(self,other):
        #deal with int + fieldelement
        if isinstance(other, type(self)):
            if self.prime!=other.prime:
                raise TypeError("Cannot substract two numbers in different Fields")
            num = (self.num - other.num) % self.prime
        elif isinstance(other, int):
            num = (self.num - other) % self.prime
        else:
            raise TypeError
        return self.__class__(num, self.prime)
    
    def __mul__(self,other):
        #deal with fieldelement * int
        if isinstance(other, type(self)):
            if self.prime!=other.prime:
                raise TypeError("Cannot multiply two numbers in different Fields")
            num = (self.num * other.num) % self.prime
        elif isinstance(other, int):
            num = (self.num * other) % self.prime
        else:
            raise TypeError
        return self.__class__(num, self.prime)
    
    def __rmul__(self,other):
        #deal with  int * fieldelement
        if isinstance(other, type(self)):
            if self.prime!=other.prime:
                raise TypeError("Cannot multiply two numbers in different Fields")
            num = (self.num * other.num) % self.prime
        elif isinstance(other, int):
            num = (self.num * other) % self.prime
        else:
            raise TypeError
        return self.__class__(num, self.prime)

    
    def __pow__(self,exponent):
        #num = (self.num ** exponent) % self.prime
        #b ** (prime-1)= 1
        #b ** ex1 = b ** ex1 * b ** (prime-1) = b** (prime-1+ex1)
        #if  ex1>0 ,ex1, prime-1+ex1
        # ex = ex1%(prime-1)
        ex = exponent % (self.prime - 1)
        num = pow(self.num,ex,self.prime)
        return self.__class__(num, self.prime)
    
    def __truediv__(self,other):
        #deal with int + fieldelement
        if isinstance(other, type(self)):
            if self.prime!=other.prime:
                raise TypeError("Cannot divede two numbers in different Fields")
            num = (self.num * (other.num**(self.prime-2))) % self.prime
        elif isinstance(other, int):
            num = (self.num * (other**(self.prime-2))) % self.prime
        else:
            raise TypeError       
        return self.__class__(num, self.prime)
    
class Point:
    def __init__(self,x,y,a,b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        
        if self.x is None and self.y is None:
            return
        
        if self.y**2 != self.x**3 + a*x + b:
            raise ValueError('({},{}) is not on the curve'.format(x, y))
            
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b
    
    def __ne__(self, other):
        return not (self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b)
    
    def __add__(self,other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('Points {},{} are not on the same curve'.format(self, other))
        
        if self.x is None:
            return other
        
        if other.x is None:
            return self
        
        if self.x == other.x and (self.y != other.y):
            return self.__class__(None, None, self.a,self.b)
        
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)
        
        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.a,self.b)
        
        if self == other:
            s = (3 * (self.x**2) + self.a)/(2*self.y)
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)
        
    def __rmul__(self,coefficient):
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result = result + current
            current += current
            coef >>= 1
        return result

class S256Field(FieldElement):
    def __init__(self,num,prime=None):
        super().__init__(num=num,prime=P)
        
    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

class S256Point(Point):
    def __init__(self, x, y, a=None, b=None):
        a,b = S256Field(A),S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x),y=S256Field(y),a=a,b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)
            
    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)
    
    def verify(self,z,sig):
        s_inv = pow(sig.s, N-2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u * G + v * self
        return total.x.num == sig.r
    
class Signature:
    def __init__(self,r,s):
        self.r = r
        self.s = s
        
    def __repr__(self):
        return 'Signature({:x},{:x})'.format(self.r, self.s)

G = S256Point(gx,gy)

def hash256(s):
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


e = int.from_bytes(hash256(b'my secret'), 'big')
z = int.from_bytes(hash256(b'my message'), 'big')

k = 1234567890

r = (k*G).x.num
