import nbformat, os

with open("BSyamalaRao_EcommerceBI.ipynb", "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

code_cells   = [c for c in nb.cells if c["cell_type"] == "code"]
executed     = [c for c in code_cells if c.get("execution_count") is not None]
with_output  = [c for c in code_cells if len(c.get("outputs", [])) > 0]
errors       = [c for c in code_cells if any(o.get("output_type") == "error" for o in c.get("outputs", []))]

print(f"Total cells      : {len(nb.cells)}")
print(f"Code cells       : {len(code_cells)}")
print(f"Executed cells   : {len(executed)}")
print(f"Cells with output: {len(with_output)}")
print(f"Cells with error : {len(errors)}")
if errors:
    for c in errors:
        for o in c["outputs"]:
            if o.get("output_type") == "error":
                ename  = o.get("ename", "")
                evalue = o.get("evalue", "")[:120]
                print(f"  ERROR in cell #{c['execution_count']}: {ename}: {evalue}")
else:
    print("No errors found - notebook executed cleanly.")

figs = sorted([f for f in os.listdir("reports") if f.endswith(".png")])
print(f"Figures in reports/: {figs}")
