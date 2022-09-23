import binascii, ast



def hash(text):
    str_text = str(text)
    result = int(binascii.hexlify(str_text.encode('utf8')), 16)
    result = str(result)
    return result

def unhash(text):
    result = binascii.unhexlify('%x' % int(text))
    result = result.decode('ascii')
    return result




p = ['toannguyen', 'quannguyen', 'hongnguyen', 'vantran', 'minhvo']
p = ['quannguyen', 'hongnguyen', 'vantran', 'minhvo']
n = hash(p)

print (n)

n1 = unhash(n)

print (n1, type(n1))
print(n1, type(ast.literal_eval(n1)))

