#!python
# send simple boot message

if __name__ == "__main__":
    import slack_funcs as sf

    msg = "Booting up."

    sf.sendmsg(msg)