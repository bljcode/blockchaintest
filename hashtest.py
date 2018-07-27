from hashlib import sha256


if __name__ == '__main__':
    x = 5
    y = 0  # y未知
    while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "0":
        y += 1
    print(f'{x*y}')
    print(sha256(f'{x*y}'.encode()).hexdigest())
    print(f'The solution is y = {y}')

