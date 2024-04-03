from termcolor import cprint

header_print= lambda s: (
    print("*"*round(1.8*len(s))),
    cprint(s, "yellow",attrs=["bold"]),
    print("*"*round(1.8*len(s))),
    )
warning_print= lambda s: cprint("*"+s, "red", attrs=["dark"])
hint_print= lambda s: cprint("*"+s, "blue")
