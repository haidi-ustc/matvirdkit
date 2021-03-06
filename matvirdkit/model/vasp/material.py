""" Core definition of a Materials Document """
from datetime import datetime
from functools import partial
from typing import ClassVar, List, Mapping, Optional, Sequence, Tuple, TypeVar, Union

from pydantic import BaseModel, Field, create_model
from pymatgen.analysis.structure_analyzer import SpacegroupAnalyzer
from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core import Structure
from pymatgen.entries.computed_entries import ComputedStructureEntry

from matvirdkit.model.settings import VASP_QUALITY_SCORES
from matvirdkit.model.corematerial import CoreMaterialsDoc
from matvirdkit.model.properties import PropertyOrigin
from matvirdkit.model.structure import StructureMetadata
from matvirdkit.model.vasp.task import TaskDocument
from matvirdkit.model.vasp.calc_types.enums import CalcType, RunType, TaskType


class MaterialsDoc(CoreMaterialsDoc, StructureMetadata):

    calc_types: Mapping[str, CalcType] = Field(  # type: ignore
        None,
        description="Calculation types for all the calculations that make up this material",
    )
    task_types: Mapping[str, TaskType] = Field(
        None,
        description="Task types for all the calculations that make up this material",
    )
    run_types: Mapping[str, RunType] = Field(
        None,
        description="Run types for all the calculations that make up this material",
    )

    origins: Sequence[PropertyOrigin] = Field(
        None, description="Mappingionary for tracking the provenance of properties"
    )

    entries: Mapping[RunType, ComputedStructureEntry] = Field(
        None, description="Dictionary for tracking entries for VASP calculations"
    )
    
    @classmethod
    def from_tasks(
        cls,
        task_group: List[TaskDocument],
        quality_scores=VASP_QUALITY_SCORES,
        use_statics: bool = False,
    ) -> "MaterialsDoc":
        """
        Converts a group of tasks into one material

        Args:
            task_group: List of task document
            quality_scores: quality scores for various calculation types
            use_statics: Use statics to define a material
        """
        if len(task_group) == 0:
            raise Exception("Must have more than one task in the group.")

        # Material ID
        possible_mat_ids = [task.task_id for task in task_group]
        material_id = min(possible_mat_ids)
        print(material_id)

        # Metadata
        last_updated = max(task.last_updated for task in task_group)
        created_at = min(task.completed_at for task in task_group)
        task_ids = list({task.task_id for task in task_group})

        deprecated_tasks = {task.task_id for task in task_group if not task.is_valid}
        run_types = {task.task_id: task.run_type for task in task_group}
        task_types = {task.task_id: task.task_type for task in task_group}
        calc_types = {task.task_id: task.calc_type for task in task_group}

        valid_tasks = [task for task in task_group if task.is_valid]
        structure_optimizations = [
            task
            for task in valid_tasks
            if task.task_type == TaskType.Structure_Optimization  # type: ignore
        ]
        #print (structure_optimizations )
        statics = [task for task in valid_tasks if task.task_type == TaskType.Static]  # type: ignore
        #print (structure_optimizations)
        structure_calcs = (
            structure_optimizations + statics
            if use_statics
            else structure_optimizations
        )

        def _structure_eval(task: TaskDocument):
            """
            Helper function to order structures optimziation and statics calcs by
            - Functional Type
            - Spin polarization
            - Special Tags
            - Energy
            """

            task_run_type = task.run_type

            return (
                -1 * quality_scores.get(task_run_type.value, 0),
                -1 * task.input.parameters.get("ISPIN", 1),
                -1 * task.input.parameters.get("LASPH", False),
                task.output.energy_per_atom,
            )

        best_structure_calc = sorted(structure_calcs, key=_structure_eval)[0]
        structure = SpacegroupAnalyzer(
            best_structure_calc.output.structure, symprec=0.1
        ).get_conventional_standard_structure()

        # Initial Structures
        initial_structures = [task.input.structure for task in task_group]
        sm = StructureMatcher(
            ltol=0.1, stol=0.1, angle_tol=0.1, scale=False, attempt_supercell=False
        )
        initial_structures = [
            group[0] for group in sm.group_structures(initial_structures)
        ]

        # Deprecated
        deprecated = all(task.task_id in deprecated_tasks for task in structure_calcs)

        # Origins
        origins = [
            PropertyOrigin(
                name="structure",
                task_id=best_structure_calc.task_id,
                last_updated=best_structure_calc.last_updated,
            )
        ]

        # entries
        entries = {}
        all_run_types = set(run_types.values())
        for rt in all_run_types:
            relevant_calcs = sorted(
                [doc for doc in structure_calcs if doc.run_type == rt and doc.is_valid],
                key=_structure_eval,
            )

            if len(relevant_calcs) > 0:
                best_task_doc = relevant_calcs[0]
                entry = best_task_doc.structure_entry
                entry.data["task_id"] = entry.entry_id
                entry.entry_id = material_id
                entries[rt] = entry

        return cls.from_structure(
            structure=structure,
            material_id=material_id,
            last_updated=last_updated,
            created_at=created_at,
            task_ids=task_ids,
            calc_types=calc_types,
            run_types=run_types,
            task_types=task_types,
            initial_structures=initial_structures,
            deprecated=deprecated,
            deprecated_tasks=deprecated_tasks,
            origins=origins,
            entries=entries,
        )

if __name__=='__main__':
   import os
   from matvirdkit.model.utils import jsanitize,ValueEnum
   from matvirdkit.model.utils import test_path,create_path
   
   from monty.serialization import loadfn,dumpfn
   create_path('output')
   relax_dir=os.path.join(test_path('..'),'relax')
   scf_dir=os.path.join(test_path('..'),'scf')
   td1=TaskDocument.from_directory(task_id='t-1',task_dir=relax_dir,dst_dir='output')
   td2=TaskDocument.from_directory(task_id='t-2',task_dir=scf_dir,dst_dir='output')
   md=MaterialsDoc.from_tasks([td1,td2],use_statics = False)
