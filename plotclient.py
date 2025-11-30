import os
import pickle
import itertools


class plotclient:
    def __init__(self, pfname="/tmp/epplot.pkl"):
        self.pfname = pfname
        self.idgen = itertools.count(1)

    # ---------------------------------------------------------
    def send(self, cmd):
        if os.path.exists(self.pfname):
            with open(self.pfname, "rb") as f:
                lst = pickle.load(f)
        else:
            lst = []
        lst.append(cmd)
        with open(self.pfname, "wb") as f:
            pickle.dump(lst, f)

    # ---------------------------------------------------------
    # FIGURE + AXES CREATION
    # ---------------------------------------------------------
    def figure(self, *args, **kwargs):
        cid = f"fig_c{next(self.idgen)}"
        self.send({
            "type": "figure_create",
            "cid": cid,
            "args": args,
            "kwargs": kwargs,
        })
        return FigureProxy(self, cid)

    def subplots(self, *args, **kwargs):
        fig_cid = f"fig_c{next(self.idgen)}"
        ax_cid = f"ax_c{next(self.idgen)}"
        self.send({
            "type": "subplot_create",
            "fig_cid": fig_cid,
            "ax_cid": ax_cid,
            "args": args,
            "kwargs": kwargs,
        })
        return (FigureProxy(self, fig_cid),
                AxesProxy(self, ax_cid))

    # ---------------------------------------------------------
    # RAW PYplot calls
    # ---------------------------------------------------------
    def __getattr__(self, name):
        def f(*args, **kwargs):
            self.send({"type": name, "args": args, "kwargs": kwargs})
        return f


# ---------------------------------------------------------
# PROXY CLASSES
# ---------------------------------------------------------
class BaseProxy:
    def __init__(self, client, cid):
        self.client = client
        self.cid = cid

    def __getattr__(self, method):
        def f(*args, **kwargs):
            self.client.send({
                "type": "method",
                "cid": self.cid,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            })
        return f

class FigureProxy(BaseProxy):
    pass

class AxesProxy(BaseProxy):
    pass

# test code
if __name__ == '__main__':
    epc = plotclient()
    epc.figure()
    epc.plot([1, 9, 2])
    epc.show(block=False)
    f, a = epc.subplots()
    a.plot([9, 0, 2])
    epc.show(block=False)
    epc.grid()
    epc.draw()

    figure = epc.figure
    plot = epc.plot
    show = epc.show

    figure()
    plot([1, 9, 2, 1, 5])
    show(block=False)
