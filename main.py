from pathlib import Path

from antigen import Antigen
from antigen.config import Config
from antigen.filters.patch import PatchFilter

example_patch = """
diff --git blabla
index 1d36346..6a53a30 100644
--- old_test.py
+++ /home/yanayg/mutation/test/test.py
@@ -1,1 +1,1 @@
-a = b'a' + (-2) if 1 > 2 < 3 else ~(a // 2)
+a = b'a' + (-2) if 1 > 2 < 4 else ~(a // 2)
""".lstrip()

file = """
a = b'a' + (-2) if 1 > 2 < 3 else ~(a // 2)
b = 5 * 7
""".lstrip()


if __name__ == "__main__":
    antigen = Antigen(
        filters=[PatchFilter(example_patch)],
        config=Config(project_root=Path("/home/yanayg/mutation/test/")),
    )

    for path in antigen.find_files("."):
        for mut in antigen.gen_mutations(path):
            print(mut)
            print(
                antigen.test_mutation(
                    mut,
                    run_command="cat test.py",
                )
            )
