#! /usr/bin/python

import hmac
import random

import IMDefaults

PLATFORM_SECRET = IMDefaults.get_platform_secret()
USER_SECRET_LENGTH = IMDefaults.get_user_secret_length()

# function gen_apikey: generate apikey
def gen_apikey():
    # generate user_secret 
    # create the set of alphanum characters
    alphanum = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'    
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    user_secret = ''
    
    length = len(alphanum)    
    len_vow = len(vowels)
    len_cons = len(consonants)    
    for i in range(USER_SECRET_LENGTH / 2):
        cons = random.randint(0, len_cons - 1)
        vow = random.randint(0, len_vow - 1)
        user_secret = user_secret + consonants[cons] + vowels[vow] 
    
    # generate api_key
    random1 = ''
    random2 = ''
    
    # random1
    for i in range(16):
        temp = random.randint(0, length - 1)
        random1 = random1 + alphanum[temp]

    # random2
    for i in range(16):
        temp = random.randint(0, length - 1)
        random2 = random2 + alphanum[temp]

    # `sig` part
    n = hmac.new(PLATFORM_SECRET, random1 + random2)
    digest = n.hexdigest()
    sig_part = digest[-16:]
    
    api_key = "%s-%s-%s" %(sig_part, random1, random2)
    return (api_key, user_secret)


# function validate_key: validate if key is valid
def validate_key(key):
    # explode the api-key to [`sig`, `random1`, `random2`]
    api_key = key.split("-") 
   
    # check the `sig` part
    if len(api_key) == 3:    
        n = hmac.new(PLATFORM_SECRET, api_key[1] + api_key[2])
        digest = n.hexdigest()
        sig_part = digest[-16:]
        if sig_part == api_key[0]:
            return True

    return False
