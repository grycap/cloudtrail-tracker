import boto3
import os

def get_structure(path):
    res = []
    for (path,i,j) in os.walk(path):
        # print(path)
        # print(j)
        if len(j) > 0:
            aux = ["{0}\{1}".format(path,x) for x in j]
            res.extend(aux)
    return res

def main():
    path = 'examples'
    res = get_structure(path)

    print(res)

if (__name__ == '__main__'):
    main()