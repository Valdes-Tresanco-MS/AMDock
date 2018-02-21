# import
from warning import no_ADzn_warning, metal_no_ADzn_warning, prot_no_metal_warning, prot_with_metal_warning,metal_no_ADzn_warning1,prot_with_metal_warning1

class Checker():
    def __init__(self, parent):
        self.parent = parent
        self.resp1 = self.resp2 = self.resp3 = 0

    def autodockzn_check(self,prot):
        if prot == 'A':
            if self.parent.v.metals is None:
                if self.parent.v.cr:
                    if self.parent.v.analog_metals is not None:
                        self.out1 = metal_no_ADzn_warning1(self.parent)
                    else:
                        self.out1 = metal_no_ADzn_warning(self.parent)
                else:
                    self.out1 = metal_no_ADzn_warning(self.parent)
                return self.out1
            else: return 0
        else:
            if self.parent.v.analog_metals is None:
                if self.parent.v.cr:
                    if self.parent.v.metals is not None:
                        self.out1 = metal_no_ADzn_warning1(self.parent)
                    else:
                        self.out1 = metal_no_ADzn_warning(self.parent)
                else:
                    self.out1 = metal_no_ADzn_warning(self.parent)
                return self.out1
            else: return 0
    def check_correct_prog(self, prot):
        if prot == 'A':
            if self.parent.v.metals is not None:
                if self.parent.v.analog_metals is None and self.parent.v.analog_protein_file is not "":
                    resp = prot_with_metal_warning1(self.parent, 'B')
                else:
                    resp = prot_with_metal_warning(self.parent)
                return resp
        else:
            if self.parent.v.analog_metals is not None:
                if self.parent.v.metals is None:
                    resp = prot_with_metal_warning1(self.parent,'A')
                else:
                    resp = prot_with_metal_warning(self.parent)
                return resp


