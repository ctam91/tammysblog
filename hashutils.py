import hashlib
import random
import string 


def make_salt():
    ''' 
    return the parameter with a random string attached. random.choice will select a random letter from the alphabet 5 times. The final string is attached to parameter. 
    '''
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])


def make_pw_hash(password, salt=None):
    ''' 
    take a password and turn it into hash for storing in db for users accont '''
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash,salt)

#find the salt by splitting the hash and then check if make_pw_hash(password,salt) is the same as the hash 
def check_pw_hash(password,hash):
    ''' 
    verify user password 
    '''
    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True
    return False 