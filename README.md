<p align="center">
  <img src="https://user-images.githubusercontent.com/49815029/166558654-7de207d0-f520-49f4-ace8-60769b3d9c12.png" height="200">
</p>


Extendable mutation testing framework

## What is mutation testing?
Mutation testing provides what coverage tries to, it finds logic that is not covered by your test suite.

It finds such places by applying mutations to your code and running the modified code against your test suite.
If the tests succeed with the mutated code, it means the changed expression is likely not covered ny the tests.

In comparison to coverage:

:green_heart: Checks expressions, not lines.

:green_heart: Checks whether the expression is covered, not whether it was executed.

:x: Can find irrelevant mutants (e.g. mutations in logging or performance optimizations or a mutation that does not break the code)
    
:x: Executes the tests many times and therefore **takes much more time**.

There are mitigations for these downsides:

:star:	We can mutate only lines that have changed in a given PR

:star:	We can show the failing mutants via comments/warnings, as opposed to failing the whole CI pipeline.

A much more in-depth explanation about the concept can be found in [This blog post by Goran Petrovic](https://testing.googleblog.com/2021/04/mutation-testing.html)

## Why use radiation?

### Extendability

In my personal experience, trying to integrate mutation testing into your CI pipeline can be a bit challenging.
There are a lot of features you might want to customize to mitigate some of the downsides of mutation testing, or to be able to integrate it to your project and dev environment effectively.

For example, ignoring mutations on logging logic (which depends on your logging framework and conventions), or showing the results on various platforms (e.g. github, bitbucket, gitlab).

radiation puts extendability as a top priority so that adding mutation testing to your project is feasible.

How?

#### Mechine friendly
The core of radiation is a pure python package that can be used by scripts.

The actual CLI uses the core package instead of the logic being coupled to it.

#### Pluginable
radiation is written as a pipeline, each stage has an interface (e.g. Mutator, MutantFilter, Runner).

Extending the logic is as simple as creating an object or function that matches that (simple) interface.

The radiation CLI utilises [entry points](https://amir.rachum.com/blog/2017/07/28/python-entry-points/) so that radiation plugins can be added just by installing them with pip.

## Usage

*radiation is currently in development, the API might change between versions.*

```python
radiation = Radiation(
    filters=[PatchFilter.from_git_diff("develop")],
    config=Config(project_root=Path("/home/myuser/myproject/")),
)

for path in radiation.find_files("."):
    for mutation in radiation.gen_mutations(path):
        result = radiation.test_mutation(
            mutation,
            run_command="pytest",
        )
        print(result)
```

or use CLI

```
Usage: radiation [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config-file PATH   configuration file to use  [default:
                           (.radiation.cfg)]
  -p, --project-root PATH  path to project to run on  [default: (cwd)]
  -i, --include TEXT       paths from which to take files for mutation, can be
                           globs
  --run-command TEXT       command to run to test a mutation  [default:
                           (pytest)]
  --help                   Show this message and exit.

Commands:
  run  run the mutation testing pipeline
```


## Roadmap
- [x] Add Basic CLI
- [ ] Improve output in CLI
- [ ] Support PatchFilter in CLI
- [ ] Use `parso` instead of the built-in `ast` for cross-version mutations.
- [ ] Add wrapper class for remote components (i.e. `RemoteFilter(hostname)`, `RemoteRunner(hostname)`).
- [ ] Add Output component (with `JunitXMLOutput`, `GithubOutput`, `BitbucketOutput` builtins)
- [ ] Add Cache component (with `FileCache`, `MongoCache` builtins)
- [ ] Add Sorter component (for selecting the most likely to succeed mutations)
