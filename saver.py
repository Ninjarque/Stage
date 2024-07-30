from SpikeCluster import *
from Bar import *

def letters_format(id):
    if len(id) == 1:
        return id + " "
    return id

def other_number_format(id):
    if len(id) == 1:
        return " " + id
    return id

def number_format(i):
    digits = 6
    i = str(i)
    while len(i) < digits:
        i = " " + i
    return i

def write_ASG(filename, bars):
    with open(filename, 'w') as file:
        for bar in bars:
            if not bar.id:
                file.write(f"{number_format(bar.i)} {bar.x:.6f}   0.1000E+01    0.001000 10.0\n")
            else:
                id_str = f"{letters_format(bar.id[0])}{letters_format(bar.id[1])}  {other_number_format(bar.id[2])}   {letters_format(bar.id[3])}{letters_format(bar.id[4])}  {other_number_format(bar.id[5])}"
                if len(bar.id) > 5:
                    ids = f"{bar.id[6:]}".strip("[]\"',")
                    id_str = f"{id_str} {ids}"
                #id_str = " ".join(bar.id)
                file.write(f"{number_format(bar.i)} {bar.x:.6f} + 0.1000E+01    0.001000 10.0     {id_str}\n")

def write_XY(filename, curvex, curvey):
    with open(filename, 'w') as file:
        for i in range(len(curvex)):
            x = curvex[i]
            y = curvey[i]
            file.write(f" {x}  {y}\n")