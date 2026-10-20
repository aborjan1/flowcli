"""flowcli — static call-graph mapper for Python codebases.

Layers, each importing only from the ones below it:

    cli, pipeline      argument parsing / orchestration
    output, runtime    emitters / running a program under the tracer
    graph              the call graph built from analysis results
    analysis           reading source code: parse, index, resolve, infer
"""

__version__ = "0.2.0"
