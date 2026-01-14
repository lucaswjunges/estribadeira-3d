#!/usr/bin/env python3
"""
Script para converter STEP para GLB usando FreeCAD
Executar com: freecad -c convert_step_to_glb.py
"""

import sys
import os

# Adicionar path do FreeCAD
FREECADPATH = '/usr/lib/freecad/lib'
if FREECADPATH not in sys.path:
    sys.path.append(FREECADPATH)

try:
    import FreeCAD
    import Part
    import Mesh
    import MeshPart
except ImportError as e:
    print(f"Erro ao importar FreeCAD: {e}")
    print("Tente executar com: freecad -c convert_step_to_glb.py")
    sys.exit(1)

# Arquivos
STEP_FILE = os.path.expanduser("~/Downloads/Automatic 3D Wire Bending Machine/Automatic 3D Wire Bending Machine.STEP")
OUTPUT_DIR = "/home/lucas-junges/Documents/clientes/w&co/Estribadeira/models"
OBJ_FILE = os.path.join(OUTPUT_DIR, "wire_bending_machine.obj")
STL_FILE = os.path.join(OUTPUT_DIR, "wire_bending_machine_complete.stl")

print(f"Carregando STEP: {STEP_FILE}")

# Carregar STEP
doc = FreeCAD.newDocument("WireBender")
Part.insert(STEP_FILE, doc.Name)

print("STEP carregado. Convertendo para mesh...")

# Obter todos os objetos
objects = doc.Objects
print(f"Objetos encontrados: {len(objects)}")

# Criar mesh de todos os objetos
meshes = []
for obj in objects:
    if hasattr(obj, 'Shape'):
        try:
            # Converter shape para mesh
            mesh = MeshPart.meshFromShape(
                Shape=obj.Shape,
                LinearDeflection=0.1,
                AngularDeflection=0.5,
                Relative=False
            )
            meshes.append(mesh)
            print(f"  - Convertido: {obj.Name}")
        except Exception as e:
            print(f"  - Erro em {obj.Name}: {e}")

if meshes:
    # Combinar todos os meshes
    combined = meshes[0]
    for m in meshes[1:]:
        combined.addMesh(m)

    # Salvar como STL
    print(f"Salvando STL: {STL_FILE}")
    combined.write(STL_FILE)
    print("Conversao concluida!")
else:
    print("Nenhum mesh gerado!")

FreeCAD.closeDocument(doc.Name)
