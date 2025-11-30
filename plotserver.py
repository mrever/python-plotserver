import os
import pickle
import matplotlib.pyplot as plt


class plotserver:
    def __init__(self, pfname="/tmp/epplot.pkl"):
        self.pfname = pfname
        self.objects = {}  # maps client IDs to real Figure/Axes

    # ---------------------------------------------------------
    def create_figure(self, cid, *args, **kwargs):
        fig = plt.figure(*args, **kwargs)
        self.objects[cid] = fig

    def create_subplot(self, fig_cid, ax_cid, *args, **kwargs):
        fig, ax = plt.subplots(*args, **kwargs)
        self.objects[fig_cid] = fig
        self.objects[ax_cid] = ax

    # ---------------------------------------------------------
    def call_method(self, cid, method, args, kwargs):
        if cid not in self.objects:
            print("Unknown object:", cid)
            return
        obj = self.objects[cid]
        fn = getattr(obj, method, None)
        if fn:
            fn(*args, **kwargs)

    # ---------------------------------------------------------
    def process_cmd(self, cmd):
        t = cmd["type"]

        if t == "figure_create":
            self.create_figure(cmd["cid"], *cmd["args"], **cmd["kwargs"])
            return

        if t == "subplot_create":
            self.create_subplot(cmd["fig_cid"], cmd["ax_cid"],
                                *cmd["args"], **cmd["kwargs"])
            return

        if t == "method":
            self.call_method(cmd["cid"], cmd["method"],
                             cmd["args"], cmd["kwargs"])
            return

        # raw pyplot
        if hasattr(plt, t):
            getattr(plt, t)(*cmd["args"], **cmd["kwargs"])
        else:
            print("Unknown command:", t)

    # ---------------------------------------------------------
    def proclist(self):
        if not os.path.exists(self.pfname):
            print("No commands.")
            return

        with open(self.pfname, "rb") as f:
            cmds = pickle.load(f)

        for cmd in cmds:
            self.process_cmd(cmd)

        os.remove(self.pfname)


if __name__ == "__main__":
    srv = plotserver("/tmp/epplot.pkl")

    q = ""
    while q != "q":
        srv.proclist()
        q = input("Press enter to check again, 'q' to quit: ")

