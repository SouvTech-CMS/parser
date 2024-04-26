import time

import schedule

if __name__ == "__main":
    def my_function():
        print("Функция запущена!")


    schedule.every(1).second.do(my_function)

    while True:
        schedule.run_pending()
        time.sleep(1)
