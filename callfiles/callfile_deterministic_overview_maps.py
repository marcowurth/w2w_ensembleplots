
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.deterministic_overview_maps import double_contourplot


def main(var1var2, model):
    double_contourplot(var1var2, model)
    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
