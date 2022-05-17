import os
from monty.serialization import loadfn,dumpfn
from pymatgen.electronic_structure.plotter import  DosPlotter, BSPlotter, BSPlotterProjected
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp import Vasprun,Incar,Outcar,Oszicar,Potcar
from pymatgen.electronic_structure.dos import  DOS,Dos
from matvirdkit.model.utils import transfer_file

class ElectronicStructure(object):
        
    def __init__(self,workpath, 
        parse_projected_eigen=False,
        parse_potcar_file=True):
        self.workpath=workpath
        self.parse_projected_eigen = parse_projected_eigen
        self.parse_potcar_file = parse_potcar_file
        self._vr= None
        self._dos= None
        self._band = None
        self._set_vasprun()

    def _set_vasprun(self,filename='vasprun.xml'):
        fname=os.path.join(self.workpath,filename)
        try:
            vr = Vasprun(fname, parse_potcar_file = self.parse_potcar_file,
                                parse_projected_eigen = self.parse_projected_eigen)
            if vr.converged:
               self._vr = vr.as_dict()
            else:
               self._vr = None
        except:
            self._vr = None

    def set_dos(self,Emin=None,Emax=None):
        self._dos = self._vr.complete_dos()

    def get_spd_dos(self):
        return  self._dos.get_spd_dos()

    def get_elem_dos(self):
        return  self._dos.get_element_dos()

    def get_dos_dict(self):
        return self._dos.as_dict()

    def set_band(self,labels,f_kpoints):
        # kpoints labels example
        # labels=[u"$\\Gamma$", u"$Y$", u"$N$", u"$X$", u"$\\Gamma$", u"$N$"]
        self._band = self._vr.get_band_structure(f_kpoints,
                                   line_mode=True,
                                   efermi=self._vr.efermi)

    def get_dos_auto(self,dst_path,abs_path=True):
        pass
        # 1. plot dos  2. transfer file
        #dst_fname="set the json file name of dos" 
        #dst_figname="set the compressed file name of band fig"
        #return {'j_id': dst_fname, 'f_id':dst_figname}

    def get_band_auto(self,dst_path,abs_path=True):
        pass
        # 1. plot band  2. transfer file
        #dst_fname="set the json file name of band" 
        #dst_figname="set the compressed file name of band fig"
        #return {'j_id': dst_fname, 'f_id':dst_figname}

    def get_band_dict(self):
        return self._band.as_dict()

    @staticmethod
    def get_dos_manually(material_id,src_path,dst_path,abs_path=False):
        src_fname=material_id+'-dos.json'
        src_figname=material_id+'.png'
        dst_fname=transfer_file(src_fname,src_path,dst_path, abs_path=abs_path,compress = False)
        dst_figname=transfer_file(src_figname,src_path,dst_path, abs_path=abs_path)
        return {'j_id': dst_fname, 'f_id':dst_figname}
        
    @staticmethod
    def get_band_manually(material_id,src_path,dst_path,abs_path=True):
        src_fname=material_id+'-band.json'
        src_figname=material_id+'.png'
        dst_fname=transfer_file(src_fname,src_path,dst_path, abs_path= abs_path, compress = False)
        dst_figname=transfer_file(src_figname,src_path,dst_path,abs_path= abs_path)
        return {'j_id': dst_fname, 'f_id':dst_figname}


if __name__=='__main__':
   material_id='mp-755811'
   dos=ElectronicStructure.get_dos_manually(material_id,'dosdata','dataset/4',abs_path=False)
   print(dos)
   
