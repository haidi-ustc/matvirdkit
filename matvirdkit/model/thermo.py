""" Core definition of a Thermo Document """
from datetime import datetime
from enum import Enum
from typing import ClassVar, Dict, List, Union, Optional

from pydantic import BaseModel, Field
from pymatgen.analysis.phase_diagram import PhaseDiagram, PhaseDiagramError
from pymatgen.core import Composition
from pymatgen.core.periodic_table import Element
from pymatgen.entries.computed_entries import ComputedEntry, ComputedStructureEntry

from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin 
from matvirdkit.model.structure import StructureMetadata
from matvirdkit.model.common import MatvirdBase


class DecompositionProduct(BaseModel):
    """
    Entry metadata for a decomposition process
    """

    material_id: str = Field(
        None, description="The material this decomposition points to"
    )
    formula: str = Field(
        None,
        description="The formula of the decomposed material this material decomposes to",
    )
    amount: float = Field(
        None,
        description="The amount of the decomposed material by formula units this this material decomposes to",
    )

class Thermo(MatvirdBase):
    """
    A thermo entry document
    """
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
    uncorrected_energy_per_atom: float = Field(
        None, description="The total DFT energy of this material per atom in eV/atom"
    )

    energy_per_atom: float = Field(
        None,
        description="The total corrected DFT energy of this material per atom in eV/atom",
    )

    energy_uncertainy_per_atom: float = Field(None, description="")

    formation_energy_per_atom: float = Field(
        None, description="The formation energy per atom in eV/atom"
    )

    energy_above_hull: float = Field(
        None, description="The energy above the hull in eV/Atom"
    )
    exfoliation_energy : Optional[float] = Field(None, description= 'Exfoliation energy for 2D materials. J/m^2')

    is_stable: bool = Field(
        False,
        description="Flag for whether this material is on the hull and therefore stable",
    )

    equillibrium_reaction_energy_per_atom: float = Field(
        None,
        description="The reaction energy of a stable entry from the neighboring equilibrium stable materials in eV."
        " Also known as the inverse distance to hull.",
    )

    decomposes_to: List[DecompositionProduct] = Field(
        None,
        description="List of decomposition data for this material. Only valid for metastable or unstable material.",
    )

    energy_type: Optional[str] = Field(
        'Unknown',
        description="The type of calculation this energy evaluation comes from. TODO: Convert to enum?",
    )

    entry_types: Optional[List[str]] = Field(None,
        description="List of available energy types computed for this material"
    )

    entries: Optional[Dict[str, Union[ComputedEntry, ComputedStructureEntry]]] = Field(
        None,
        description="List of all entries that are valid for this material."
        " The keys for this dictionary are names of various calculation types",
    )

    #@classmethod
    #def from_entries(cls, entries: List[Union[ComputedEntry, ComputedStructureEntry]]):

    #    pd = PhaseDiagram(entries)

    #    docs = []

    #    for e in entries:
    #        (decomp, ehull) = pd.get_decomp_and_e_above_hull(e)

    #        d = {
    #            "material_id": e.entry_id,
    #            "uncorrected_energy_per_atom": e.uncorrected_energy
    #            / e.composition.num_atoms,
    #            "energy_per_atom": e.uncorrected_energy / e.composition.num_atoms,
    #            "formation_energy_per_atom": pd.get_form_energy_per_atom(e),
    #            "energy_above_hull": ehull,
    #            "is_stable": e in pd.stable_entries,
    #        }

    #        if "last_updated" in e.data:
    #            d["last_updated"] = e.data["last_updated"]

    #        # Store different info if stable vs decomposes
    #        if d["is_stable"]:
    #            d[
    #                "equillibrium_reaction_energy_per_atom"
    #            ] = pd.get_equilibrium_reaction_energy(e)
    #        else:
    #            d["decomposes_to"] = [
    #                {
    #                    "material_id": de.entry_id,
    #                    "formula": de.composition.formula,
    #                    "amount": amt,
    #                }
    #                for de, amt in decomp.items()
    #            ]

    #        d["energy_type"] = e.parameters.get("run_type", "Unknown")
    #        d["entry_types"] = [e.parameters.get("run_type", "Unknown")]
    #        d["entries"] = {e.parameters.get("run_type", ""): e}

    #        for k in ["last_updated"]:
    #            if k in e.parameters:
    #                d[k] = e.parameters[k]
    #            elif k in e.data:
    #                d[k] = e.data[k]

    #        docs.append(ThermoDoc.from_structure(structure=e.structure, **d))

    #    return docs

class ThermoDoc(BaseModel):
      """
      A thermo  property block
      """
      property_name: ClassVar[str] = Field(
        "thermo", description="The subfield name for this property"
         )
      thermo: Dict[str,Thermo]=Field({}, description='Thermo list')

if __name__=='__main__':
   from uuid import uuid4
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize,ValueEnum
   origins0=[
            Origin(name='pbe-static',task_id='task-112'),
            Origin(name='pbe-static-d2',task_id='task-112'),
            ]
   origins1=[
            Origin(name='pbe-static',task_id='task-112'),
            Origin(name='pbe-static-d2',task_id='task-112'),
            ]
   provenance0=LocalProvenance(origins=origins0,
                              created_at=datetime.now(),
                              authors=[{'name':'haidi','email':'haidi@hfut.edu.cn'},{'name':'zhangsan','email':'zhangsan@ustc.edu.cn'}]
                   )
   provenance1=LocalProvenance(origins=origins1)
   td=ThermoDoc(
      thermo={
              'pbe-static':      Thermo(formation_energy_per_atom=-0.1, uncorrected_energy_per_atom=-2.3),
              'pbe-static-d2' :  Thermo(energy_above_hull=0.1, uncorrected_energy_per_atom=-2.4,
      provenance={'energy_above_hull': provenance0, 'formation_energy': provenance1})
               } 
      )
   dumpfn(jsanitize(td),'thermo.json',indent=4)
#rovenance: LocalProvenance = Field(None, description="Property provenance")
