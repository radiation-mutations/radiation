from antigen import Antigen
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
    antigen = Antigen(filters=[PatchFilter(example_patch)])

    for mut in antigen.gen_mutations_str(
        file, path="/home/yanayg/mutation/test/test.py"
    ):
        print(mut)
        print(
            antigen.test_mutation(
                mut,
                project_root="/home/yanayg/mutation/test",
                run_command="cat test.py",
            )
        )
