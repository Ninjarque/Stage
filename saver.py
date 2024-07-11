from SpikeCluster import *
from Bar import *

def write_ASG(filename, bars):
    with open(filename, 'w') as file:
        for bar in bars:
            if not bar.id:
                file.write(f"  {bar.i} {bar.x:.6f}   0.1000E+01    0.001000 10.0\n")
            else:
                id_str = f"{bar.id[0]} {bar.id[1]}   {bar.id[2]}   {bar.id[3]} {bar.id[4]}   {bar.id[5]}"
                if len(bar.id) > 5:
                    ids = f"{bar.id[6:]}".strip("[]\"',")
                    id_str = f"{id_str} {ids}"
                #id_str = " ".join(bar.id)
                file.write(f"  {bar.i} {bar.x:.6f} + 0.1000E+01    0.001000 10.0     {id_str}\n")

def write_XY(filename, curvex, curvey):
    with open(filename, 'w') as file:
        for i in range(len(curvex)):
            x = curvex[i]
            y = curvey[i]
            file.write(f" {x}  {y}\n")