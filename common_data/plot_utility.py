from io import StringIO

def svgString(fig):
    io_obj = StringIO()
    fig.savefig(io_obj)

    return io_obj.getvalue()



