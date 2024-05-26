from time import sleep

from app import App


if __name__ == '__main__':
    try:
        app = App()
        app.run()
    except Exception as e:
        print(e)
        sleep(10)


