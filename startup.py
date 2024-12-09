import importlib



if __name__ == '__main__':
    import main
    while 1:
        if main.reload_file:
            importlib.reload(main)
            bot = main.WirelessWarehouseBot()
            bot.startup()
        else:
            break
