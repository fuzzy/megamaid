# Stdlib imports
import argparse
from inspect import currentframe, getframeinfo


def argparse_constructor(d):
    try:
        frameinfo = getframeinfo(currentframe())
        parser = argparse.ArgumentParser(description=d.get("description", ""))

        for group in d.get("groups", []):
            frameinfo = getframeinfo(currentframe())
            g_name = group.pop("title", "parent")
            g_desc = group.pop("description", False)

            frameinfo = getframeinfo(currentframe())
            g = None
            if g_name and g_desc and g_name != "parent":
                frameinfo = getframeinfo(currentframe())
                g = parser.add_argument_group(g_name, g_desc)
            elif g_name and not g_desc and g_name != "parent":
                frameinfo = getframeinfo(currentframe())
                g = parser.add_argument_group(g_name)
            else:
                frameinfo = getframeinfo(currentframe())
                g = parser

            for arg in group["arguments"]:
                frameinfo = getframeinfo(currentframe())
                t_short = arg.pop("short", False)
                t_long = arg.pop("long", False)
                t_type = arg.pop("type", False)

                frameinfo = getframeinfo(currentframe())
                if t_short and t_short[0] != "-":
                    o_short = f"-{t_short}"
                else:
                    o_short = t_short

                frameinfo = getframeinfo(currentframe())
                if t_long and t_long[0:1] != "--":
                    o_long = f"--{t_long}"
                else:
                    o_long = t_long

                frameinfo = getframeinfo(currentframe())
                if t_type:
                    arg["type"] = eval(t_type)

                frameinfo = getframeinfo(currentframe())
                g.add_argument(o_short, o_long, **arg)
    except Exception as e:
        print(f"{frameinfo.filename}, {frameinfo.lineno}: {e}")
        raise

    return parser.parse_args()
