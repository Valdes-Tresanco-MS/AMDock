from AMDock.warning import (prot_with_metal_warning, metal_no_ADzn_warning1,
                     prot_with_metal_warning1, metal_no_ADzn_od_warning)


class Checker():
    def __init__(self, parent):
        self.parent = parent
        self.resp1 = self.resp2 = self.resp3 = 0

    def autodockzn_check(self, prot1, prot2=None):
        pt1 = pt2 = True
        text = {}
        if prot2:
            if not prot2.zn_atoms:
                text['Off-Target'] = prot2
                pt2 = False
        if not prot1.zn_atoms:
            text['Target'] =  prot1
            pt1 = False
        if not pt1 or not pt2:
            self.out1 = metal_no_ADzn_od_warning(self.parent, text)
            if prot2:
                return self.out1, pt1, pt2
            else:
                return self.out1
        return

    def check_correct_prog(self, prot1, prot2=None):
        pt1 = pt2 = False
        text = {}
        if prot2:
            if prot2.zn_atoms:
                text['Off-Target'] = prot2
                pt2 = True
        if prot1.zn_atoms:
            text['Target'] = prot1
            pt1 = True
        if pt1 or pt2:
            self.out1 = prot_with_metal_warning(self.parent, text)
            if prot2:
                return self.out1, pt1, pt2
            else:
                return self.out1
        return None, None, None
