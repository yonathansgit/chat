import hashlib

def hash_expression(expression):
    final_expression = str(expression)
    hash_object = hashlib.md5(final_expression.encode())
    return hash_object.hexdigest()

