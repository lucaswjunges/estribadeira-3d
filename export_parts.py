#!/usr/bin/env python3
"""
Exporta cada peça do STEP separadamente com posições originais.
Executar com: freecad export_parts.py
"""

import sys
import os
import json

# Paths
STEP_FILE = os.path.expanduser("~/Downloads/Automatic 3D Wire Bending Machine/Automatic 3D Wire Bending Machine.STEP")
OUTPUT_DIR = "/home/lucas-junges/Documents/clientes/w&co/Estribadeira/models/parts"
MANIFEST_FILE = "/home/lucas-junges/Documents/clientes/w&co/Estribadeira/models/parts_manifest.json"

# Criar diretório de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Importar FreeCAD
FREECADPATH = '/usr/lib/freecad-python3/lib'
if os.path.exists(FREECADPATH):
    sys.path.insert(0, FREECADPATH)

FREECADPATH2 = '/usr/lib/freecad/lib'
if os.path.exists(FREECADPATH2):
    sys.path.insert(0, FREECADPATH2)

import FreeCAD
import Part
import Mesh
import MeshPart

print(f"FreeCAD version: {FreeCAD.Version()}")
print(f"Carregando: {STEP_FILE}")

# Criar documento e importar STEP
doc = FreeCAD.newDocument("WireBender")
Part.insert(STEP_FILE, doc.Name)
FreeCAD.setActiveDocument(doc.Name)

print(f"Objetos encontrados: {len(doc.Objects)}")

# Manifest para guardar info de cada peça
manifest = {
    "source": STEP_FILE,
    "parts": []
}

# Processar cada objeto
for i, obj in enumerate(doc.Objects):
    if not hasattr(obj, 'Shape') or obj.Shape.isNull():
        print(f"  Ignorando {obj.Name} (sem shape)")
        continue

    shape = obj.Shape

    # Obter bounding box para posição
    bbox = shape.BoundBox
    center = [(bbox.XMin + bbox.XMax) / 2,
              (bbox.YMin + bbox.YMax) / 2,
              (bbox.ZMin + bbox.ZMax) / 2]

    size = [bbox.XLength, bbox.YLength, bbox.ZLength]

    # Nome seguro para arquivo
    safe_name = obj.Name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    stl_filename = f"part_{i:03d}_{safe_name}.stl"
    stl_path = os.path.join(OUTPUT_DIR, stl_filename)

    print(f"  Exportando: {obj.Name}")
    print(f"    Centro: {center}")
    print(f"    Tamanho: {size}")

    try:
        # Converter para mesh
        mesh = MeshPart.meshFromShape(
            Shape=shape,
            LinearDeflection=0.1,
            AngularDeflection=0.3,
            Relative=False
        )

        # Salvar STL
        mesh.write(stl_path)

        # Adicionar ao manifest
        part_info = {
            "index": i,
            "name": obj.Name,
            "file": stl_filename,
            "center": center,
            "size": size,
            "bbox": {
                "min": [bbox.XMin, bbox.YMin, bbox.ZMin],
                "max": [bbox.XMax, bbox.YMax, bbox.ZMax]
            },
            "vertices": mesh.CountPoints,
            "faces": mesh.CountFacets
        }
        manifest["parts"].append(part_info)

        print(f"    Salvo: {stl_filename} ({mesh.CountFacets} faces)")

    except Exception as e:
        print(f"    ERRO: {e}")

# Salvar manifest
with open(MANIFEST_FILE, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"\nExportadas {len(manifest['parts'])} peças")
print(f"Manifest salvo em: {MANIFEST_FILE}")

FreeCAD.closeDocument(doc.Name)
print("Concluído!")
