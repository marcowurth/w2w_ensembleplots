
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.ensemble_spread_maps import ens_spread_map


def main(var1var2):
    ens_spread_map(var1var2)
    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    main(sys.argv[1])
