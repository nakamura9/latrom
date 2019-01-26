import matplotlib
from io import StringIO

# Remember to 
# matplotlib.use("svg")

def svgString(fig):
    io_obj = StringIO()
    fig.savefig(io_obj)

    return io_obj.getvalue()



