import pya
import sys
import traceback

# Import register_library to register libraries
import register_library

layout = pya.Layout()
top = layout.create_cell("top")

libs = ["NIST_LithoToolbox", "NIST_MEMS_NEMS"]
failed = 0
passed = 0

for lib_name in libs:
    lib = pya.Library.library_by_name(lib_name)
    if lib is None:
        print(f"Library {lib_name} not found!")
        failed += 1
        continue
    
    print(f"\nTesting library: {lib_name}")
    pcell_names = lib.layout().pcell_names()
    for name in pcell_names:
        print(f"Instantiating PCell: {name} ... ", end="")
        sys.stdout.flush()
        try:
            # Get the pcell declaration from library
            pcell_decl = lib.layout().pcell_declaration(name)
            # Create a dictionary of default parameter values
            params_dict = {}
            for p in pcell_decl.get_parameters():
                params_dict[p.name] = p.default
            
            # Instantiate PCell using create_cell
            pcell_cell = layout.create_cell(name, lib_name, params_dict)
            pcell_cell_index = pcell_cell.cell_index()
            
            # Insert instance into top cell
            trans = pya.Trans(0, 0)
            top.insert(pya.CellInstArray(pcell_cell_index, trans))
            
            # Flatten to force geometry production (produce_impl)
            pcell_cell.flatten(True)
            
            print("PASSED")
            passed += 1
        except Exception as e:
            print("FAILED")
            traceback.print_exc()
            failed += 1

print(f"\nVerification finished: {passed} passed, {failed} failed.")
if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
