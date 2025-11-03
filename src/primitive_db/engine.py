import prompt


def welcome():
    print("DB project is running!")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        command = prompt.string("Введите команду: ").strip().lower()
        
        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print(f"Неизвестная команда: {command}")