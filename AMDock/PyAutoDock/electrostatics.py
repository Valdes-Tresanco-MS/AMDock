############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: electrostatics.py,v 1.3 2004/07/23 00:54:46 lindy Exp $
#

import math
from scorer import DistDepPairwiseScorer


class ElectrostaticsRefImpl(DistDepPairwiseScorer):
    """reference implementation of the Electrostatics class

    Notes
    ======
    * For now, the MolecularSystem has the responsibility of
      supplying charges. This could change in the future if the
      chargeCalculators migrate away from MolKit. This requires
      a reduced dependency on the Atoms.

    * The electrostatics calculation depends on relative distance
      not absolute coords. Hopefully, we won't need coords in this
      class.

    * A GridMap might be represencted as a 'subset' in this class
      by defining psuedo-atoms at each grid point.

    """
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('charge', False)
        self.required_attr_dictB.setdefault('charge', False)
        if ms is not None:
            self.set_molecular_system(ms)
        self.use_non_bond_cutoff = False


    def get_dddp(self, distance):
        """return distance dependent dielectric permittivity

        weight to be remove to WeightedMultiTermDistDepPairwiseScorer
        
        Reference
        ==========
        Mehler & Solmajer (1991) Protein Engineering vol.4 no.8, pp. 903-910.

        Basically, this describes a sigmoidal function from a low
        dielectric (like organic solvent) at small distance (<5Ang)
        asymptoticly to dielectric of water at large distance (30Ang).
        
        epsilon(r) = A + (B/[1+ k*exp(-lambda*B*r)])     (equation 6)

        where, A, lambda, and k are parameters supplied by the paper,
               B = epsilon0 - A (so B is also a parameter)
               epsilon0 is the dielectric constant of water at 25C (78.4)

        Two sets of parameters are given in the paper:
        {'A' : -8.5525, 'k' : 7.7839, 'lambda_' : 0.003627} [Conway]
        {'A' : -20.929, 'k' : 3.4781, 'lambda_' : 0.001787} [Mehler&Eichele]
        """
        
        epsilon0 = 78.4     # dielectric constant of water at 25C
        lambda_ = 0.003627  # supplied parameter
        A = -8.5525         # supplied parameter
        k = 7.7839          # supplied parameter
        B = epsilon0 - A

        # epsilon is a unitless scaling factor 
        epsilon = A + B / (1.0 + k*math.e**(-lambda_*B*distance))
        return epsilon
    


    def _f(self, at_a, at_b, dist):
        """Return electrostatic potential in kcal/mole.

        Here's how the 332. unit conversion factor is calculated:
        
        q = 1.60217733E-19  # (C) charge on electron
        eps0 = 8.854E-12    # (C^2/J*m) vacuum permittivity
        J_per_cal = 4.18400 # Joules per calorie
        avo = 6.02214199E23 # Avogadro's number

        factor = (q*avo*q*1E10 )/(4.0*math.pi*eps0*J_per_cal*1000)

        """
        q1 = at_a.charge;
        q2 = at_b.charge;
        epsilon = self.get_dddp(dist)
        factor = 332. # 4*pi*esp0*units conversions
        if dist != 0.0:
            return (factor*q1*q2) / (epsilon*dist) # kcal/mole
        else: return 0.


Electrostatics = ElectrostaticsRefImpl
# ElectrostaticsRefImpl

if __name__ == '__main__':
    pass
    # test_scorer.run_test()
