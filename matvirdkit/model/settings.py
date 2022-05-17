from typing import Dict, List
SYMPREC: float =   0.1  #"Symmetry precision for spglib symmetry finding"
LTOL:   float  = 0.2    #"Fractional length tolerance for structure matching"
ANGLE_TOL: float=5.0   #Angle tolerance for structure matching in degrees.
STOL: float=0.3   #"Site tolerance for structure matching. Defined as the fraction of the average free length per atom = ( V / Nsites ) ** (1/3)"
MAX_PIEZO_MILLER: int = 10 # Maximum miller allowed for computing strain direction for maximal piezo response
VASP_QUALITY_SCORES: Dict[str, int] = {"SCAN": 3, "GGA+U": 2, "GGA": 1} #"Dictionary Mapping VASP calculation run types to rung level for VASP materials builders"
VASP_KSPACING_TOLERANCE: float = 0.05 #"Relative tolerance for kspacing to still be a valid task document"
VASP_KPTS_TOLERANCE: float=  0.9 #"Relative tolerance for kpt density to still be a valid task document"
#Default input sets for task validation
VASP_DEFAULT_INPUT_SETS: Dict[str, str] = {
            "GGA Structure Optimization": "USTCRelaxSet",
            #pymatgen.io.vasp.sets.MPRelaxSet,
            "GGA+U Structure Optimization": "USTCMPRelaxSet",   }  
VASP_CHECKED_LDAU_FIELDS: List[str] =  ["LDAUU", "LDAUJ", "LDAUL"] # description="LDAU fields to validate for tasks" 
VASP_MAX_SCF_GRADIENT: float = 100 # "Maximum upward gradient in the last SCF for any VASP calculation"
