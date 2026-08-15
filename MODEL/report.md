# flowcli report

**16** modules · **105** nodes · **176** edges · **632** unresolved calls · entry `flowcli.cli (module)` (52 unreachable)

## Call graph

| Node | Kind | File:Line | Out | In | Depth |
|---|---|---|---:|---:|---:|
| `flowcli.cli:_cmd_map` | function | cli.py:126 | 17 | 1 | 0 |
| `flowcli.resolver:_resolve_absolute` | function | resolver.py:264 | 8 | 3 | 4 |
| `flowcli.entrypoints:detect` | function | entrypoints.py:22 | 7 | 1 | 1 |
| `flowcli.report:write_markdown` | function | report.py:45 | 7 | 1 | 1 |
| `flowcli.resolver:_resolve_name` | function | resolver.py:150 | 7 | 1 | 3 |
| `flowcli.resolver:_resolve_one` | function | resolver.py:77 | 6 | 3 | 2 |
| `flowcli.resolver:_resolve_name_imported` | function | resolver.py:189 | 6 | 1 | 4 |
| `flowcli.simulate:simulate` | function | simulate.py:41 | 6 | 1 | 2 |
| `flowcli.resolver:_resolve_self_attr_chain` | function | resolver.py:102 | 5 | 1 | 3 |
| `flowcli.classes:build_class_graph` | function | classes.py:56 | 4 | 1 | 1 |
| `flowcli.cli:main` | function | cli.py:49 | 4 | 1 | 0 |
| `flowcli.graph:_make_nodes` | function | graph.py:46 | 4 | 1 | 2 |
| `flowcli.resolver:_resolve_dotted` | function | resolver.py:205 | 4 | 1 | 3 |
| `flowcli.resolver:_resolve_local_class_dotted` | function | resolver.py:243 | 4 | 1 | 4 |
| `flowcli.resolver:_resolve_typed_local` | function | resolver.py:226 | 4 | 1 | 4 |
| `flowcli.resolver:resolve_method` | function | resolver.py:303 | 3 | 8 | 3 |
| `flowcli.resolver:_constructor` | function | resolver.py:258 | 3 | 5 | 4 |
| `flowcli.classes:_make_node` | function | classes.py:74 | 3 | 1 | 2 |
| `flowcli.cli:_cmd_run` | function | cli.py:227 | 3 | 1 | 0 |
| `flowcli.cli:_write_outputs` | function | cli.py:208 | 3 | 1 | 0 |
| `flowcli.discovery:discover` | function | discovery.py:81 | 3 | 1 | 1 |
| `flowcli.graph:parse_entry_spec` | function | graph.py:222 | 3 | 1 | 2 |
| `flowcli.infer:_resolve_return_call` | function | infer.py:111 | 3 | 1 | 5 |
| `flowcli.report:_signatures_section` | function | report.py:123 | 3 | 1 | 2 |
| `flowcli.resolver:_resolve_enclosing_scope` | function | resolver.py:170 | 3 | 1 | 4 |
| `flowcli.simulate:_returns_of_call` | function | simulate.py:198 | 3 | 1 | 4 |
| `flowcli.resolver:_find_attr_type` | function | resolver.py:119 | 2 | 2 | 4 |
| `flowcli.resolver:_find_class_by_dotted` | function | resolver.py:359 | 2 | 2 | 4 |
| `flowcli.classes:_add_inheritance` | function | classes.py:126 | 2 | 1 | 2 |
| `flowcli.cli:_execute` | function | cli.py:274 | 2 | 1 | 0 |
| `flowcli.entrypoints:_exported` | function | entrypoints.py:75 | 2 | 1 | 2 |
| `flowcli.graph:apply_simulation` | function | graph.py:30 | 2 | 1 | 1 |
| `flowcli.graph:build_graph` | function | graph.py:23 | 2 | 1 | 1 |
| `flowcli.infer:_resolve_return_expr` | function | infer.py:94 | 2 | 1 | 4 |
| `flowcli.infer:infer_signatures` | function | infer.py:29 | 2 | 1 | 3 |
| `flowcli.render_html:build_payload` | function | render_html.py:60 | 2 | 1 | 2 |
| `flowcli.render_html:render_html` | function | render_html.py:133 | 2 | 1 | 1 |
| `flowcli.resolver:resolve_all` | function | resolver.py:41 | 2 | 1 | 1 |
| `flowcli.simulate:_eval_atom` | function | simulate.py:156 | 2 | 1 | 3 |
| `flowcli.resolver:_resolve_class_ref` | function | resolver.py:342 | 1 | 10 | 3 |
| `flowcli.discovery:find_package_prefix` | function | discovery.py:29 | 1 | 2 | 2 |
| `flowcli.graph:_annotate_flow` | function | graph.py:104 | 1 | 2 | 3 |
| `flowcli.graph:_annotate_ret_types` | function | graph.py:123 | 1 | 2 | 3 |
| `flowcli.simulate:_walk` | function | simulate.py:237 | 1 | 2 | 4 |
| `flowcli.cli:_entry_specs` | function | cli.py:121 | 1 | 1 | 0 |
| `flowcli.cli:_parse_all` | function | cli.py:326 | 1 | 1 | 0 |
| `flowcli.discovery:_namespace_prefix` | function | discovery.py:52 | 1 | 1 | 3 |
| `flowcli.entrypoints:_script_to_node` | function | entrypoints.py:108 | 1 | 1 | 2 |
| `flowcli.graph:_find_subtree` | function | graph.py:254 | 1 | 1 | 3 |
| `flowcli.graph:parse_entry_specs` | function | graph.py:200 | 1 | 1 | 1 |
| `flowcli.parser:parse_module` | function | parser.py:20 | 1 | 1 | 1 |
| `flowcli.parser:parse_source` | function | parser.py:29 | 1 | 1 | 2 |
| `flowcli.report:_classes_section` | function | report.py:71 | 1 | 1 | 2 |
| `flowcli.report:_params_str` | function | report.py:149 | 1 | 1 | 3 |
| `flowcli.report:_returns_str` | function | report.py:162 | 1 | 1 | 3 |
| `flowcli.report:_runtime_str` | function | report.py:171 | 1 | 1 | 3 |
| `flowcli.report:print_summary` | function | report.py:188 | 1 | 1 | 1 |
| `flowcli.simulate:_bind_site` | function | simulate.py:99 | 1 | 1 | 3 |
| `flowcli.simulate:_function_index` | function | simulate.py:91 | 1 | 1 | 3 |
| `flowcli.simulate:_seed_entry` | function | simulate.py:128 | 1 | 1 | 3 |
| `flowcli.simulate:_simulated_events` | function | simulate.py:216 | 1 | 1 | 3 |
| `flowcli.simulate:module_entry_candidates` | function | simulate.py:249 | 1 | 1 | 2 |
| `flowcli.tracer:capture` | function | tracer.py:74 | 1 | 1 | 1 |
| `flowcli.models:node_id` | function | models.py:112 | 0 | 15 | 2 |
| `flowcli.resolver:_internal` | function | resolver.py:65 | 0 | 9 | 3 |
| `flowcli.resolver:_unresolved` | function | resolver.py:73 | 0 | 9 | 3 |
| `flowcli.report:_cell` | function | report.py:145 | 0 | 4 | 3 |
| `flowcli.classes:class_id` | function | classes.py:52 | 0 | 3 | 2 |
| `flowcli.resolver:ProjectIndex.module_for` | method | resolver.py:31 | 0 | 3 | 3 |
| `flowcli.infer:_raw_call_for` | function | infer.py:128 | 0 | 2 | 5 |
| `flowcli.report:_by_out_degree` | function | report.py:41 | 0 | 2 | 2 |
| `flowcli.resolver:_external` | function | resolver.py:69 | 0 | 2 | 5 |
| `flowcli.simulate:_absorb` | function | simulate.py:142 | 0 | 2 | 3 |
| `flowcli.classes:_add_composition` | function | classes.py:135 | 0 | 1 | 2 |
| `flowcli.classes:_stereotype` | function | classes.py:111 | 0 | 1 | 3 |
| `flowcli.classes:scope_class_graph` | function | classes.py:148 | 0 | 1 | 1 |
| `flowcli.cli:_add_map_parser` | function | cli.py:71 | 0 | 1 | 0 |
| `flowcli.cli:_add_run_parser` | function | cli.py:94 | 0 | 1 | 0 |
| `flowcli.cli:_build_meta` | function | cli.py:339 | 0 | 1 | 0 |
| `flowcli.cli:_exit_code_of` | function | cli.py:299 | 0 | 1 | 0 |
| `flowcli.cli:_resolve_entry` | function | cli.py:108 | 0 | 1 | 0 |
| `flowcli.cli:_runtime_payload` | function | cli.py:306 | 0 | 1 | 0 |
| `flowcli.discovery:_excluded` | function | discovery.py:77 | 0 | 1 | 2 |
| `flowcli.discovery:_is_project_root` | function | discovery.py:48 | 0 | 1 | 4 |
| `flowcli.discovery:derive_module_name` | function | discovery.py:67 | 0 | 1 | 2 |
| `flowcli.entrypoints:_console_scripts` | function | entrypoints.py:91 | 0 | 1 | 2 |
| `flowcli.entrypoints:_defines_api` | function | entrypoints.py:64 | 0 | 1 | 2 |
| `flowcli.entrypoints:_is_private_path` | function | entrypoints.py:69 | 0 | 1 | 2 |
| `flowcli.entrypoints:detect.add` | function | entrypoints.py:26 | 0 | 1 | 2 |
| `flowcli.graph:_apply_edges` | function | graph.py:78 | 0 | 1 | 2 |
| `flowcli.graph:_find_module` | function | graph.py:277 | 0 | 1 | 3 |
| `flowcli.graph:apply_runtime` | function | graph.py:142 | 0 | 1 | 1 |
| `flowcli.graph:compute_depths` | function | graph.py:153 | 0 | 1 | 1 |
| `flowcli.graph:prune_unreachable` | function | graph.py:181 | 0 | 1 | 1 |
| `flowcli.parser:_Collector.__init__` | method | parser.py:55 | 0 | 1 | 3 |
| `flowcli.render_html:_class_payload` | function | render_html.py:100 | 0 | 1 | 2 |
| `flowcli.render_html:_module_of` | function | render_html.py:19 | 0 | 1 | 3 |
| `flowcli.render_html:_node_entry` | function | render_html.py:23 | 0 | 1 | 3 |
| `flowcli.report:_loc` | function | report.py:31 | 0 | 1 | 2 |
| `flowcli.report:_most_called_section` | function | report.py:93 | 0 | 1 | 2 |
| `flowcli.report:_unreachable_section` | function | report.py:108 | 0 | 1 | 2 |
| `flowcli.report:_unresolved_section` | function | report.py:133 | 0 | 1 | 2 |
| `flowcli.report:write_json` | function | report.py:17 | 0 | 1 | 1 |
| `flowcli.resolver:ProjectIndex.__init__` | method | resolver.py:28 | 0 | 1 | 1 |
| `flowcli.simulate:_Site.__init__` | method | simulate.py:34 | 0 | 1 | 4 |

## Top 10 most-called

| Node | In | Called by |
|---|---:|---|
| `flowcli.models:node_id` | 15 | `flowcli.entrypoints:_exported`, `flowcli.entrypoints:_script_to_node`, `flowcli.entrypoints:detect`, `flowcli.graph:_find_subtree`, `flowcli.graph:_make_nodes`, … +10 |
| `flowcli.resolver:_resolve_class_ref` | 10 | `flowcli.classes:_add_inheritance`, `flowcli.classes:_make_node`, `flowcli.infer:_resolve_return_call`, `flowcli.infer:_resolve_return_expr`, `flowcli.resolver:_find_attr_type`, … +5 |
| `flowcli.resolver:_internal` | 9 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_enclosing_scope`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, … +4 |
| `flowcli.resolver:_unresolved` | 9 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_dotted`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, … +4 |
| `flowcli.resolver:resolve_method` | 8 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, `flowcli.resolver:_resolve_one`, … +3 |
| `flowcli.resolver:_constructor` | 5 | `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_enclosing_scope`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, `flowcli.resolver:_resolve_name_imported` |
| `flowcli.report:_cell` | 4 | `flowcli.report:_classes_section`, `flowcli.report:_params_str`, `flowcli.report:_returns_str`, `flowcli.report:_runtime_str` |
| `flowcli.classes:class_id` | 3 | `flowcli.classes:_add_inheritance`, `flowcli.classes:_make_node`, `flowcli.classes:build_class_graph` |
| `flowcli.resolver:ProjectIndex.module_for` | 3 | `flowcli.entrypoints:_exported`, `flowcli.resolver:_find_class_by_dotted`, `flowcli.resolver:_resolve_absolute` |
| `flowcli.resolver:_resolve_absolute` | 3 | `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_dotted`, `flowcli.resolver:_resolve_name_imported` |

## Unreachable from `flowcli.cli (module)`

_52 function(s) outside this call graph were pruned from the report (rerun with --keep-unreachable to include them)._

## Signatures

| Node | Signature | Returns | Data flow |
|---|---|---|---|
| `flowcli.classes:_add_composition` | `(node: ClassNode, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · graph:ClassGraph |
| `flowcli.classes:_add_inheritance` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · index:ProjectIndex, graph:ClassGraph |
| `flowcli.classes:_make_node` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo)` | `ClassNode` | ~1 site(s) · index:ProjectIndex |
| `flowcli.classes:_stereotype` | `(ci: ClassInfo)` | `str` | ~1 site(s) · ci:ClassInfo |
| `flowcli.classes:build_class_graph` | `(index: ProjectIndex)` | `ClassGraph` | ~1 site(s) · index:ProjectIndex |
| `flowcli.classes:class_id` | `(module: str, qualname: str)` | `str` | ~5 site(s) · no args |
| `flowcli.classes:scope_class_graph` | `(graph: ClassGraph, keep_modules: set[str])` | `ClassGraph` | ~1 site(s) · graph:scope_class_graph, keep_modules={nid.split(':', 1)[0] for nid  |
| `flowcli.cli:_add_map_parser` | `(sub: argparse._SubParsersAction)` | `None` | ~1 site(s) · sub:argparse._SubParsersAction |
| `flowcli.cli:_add_run_parser` | `(sub: argparse._SubParsersAction)` | `None` | ~1 site(s) · sub:argparse._SubParsersAction |
| `flowcli.cli:_build_meta` | `(graph: Graph, index: ProjectIndex, root: Path, entry_id: str / None, unreachable: int, include_external: bool, failures: list[ParseFailure])` | `dict` | ~1 site(s) · graph:Graph, index:ProjectIndex, root:Path |
| `flowcli.cli:_cmd_map` | `(args: argparse.Namespace)` | `int` | ~1 site(s) · args:argparse.Namespace |
| `flowcli.cli:_cmd_run` | `(args: argparse.Namespace)` | `int` | ~1 site(s) · args:argparse.Namespace |
| `flowcli.cli:_entry_specs` | `(raw: list[str], root: Path)` | `list[str]` | ~1 site(s) · raw:list[str], root:Path |
| `flowcli.cli:_execute` | `(mode: str, target: str, prog_args: list[str], root: Path, script_dir: Path, samples: bool)` | `~tuple` | ~1 site(s) · mode:str, target:str, prog_args:list[str] |
| `flowcli.cli:_exit_code_of` | `(exc: SystemExit)` | `int` | ~1 site(s) · exc:SystemExit |
| `flowcli.cli:_parse_all` | `(files: list[tuple[str, Path]])` | `tuple[dict[str, ModuleInfo], list[ParseFailure]]` | ~1 site(s) · files:discover |
| `flowcli.cli:_resolve_entry` | `(entry: str, root: Path)` | `str` | ~1 site(s) · entry:str, root:Path |
| `flowcli.cli:_runtime_payload` | `(cap, root: Path, mode: str, target: str, prog_args: list[str], exit_code: int, samples: bool)` | `~dict` | ~1 site(s) · root:Path, mode:str, target:str |
| `flowcli.cli:_write_outputs` | `(graph: Graph, meta: dict, formats: set[str], out_dir: Path, runtime_data: dict / None, sim_events: list[list[str]], class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:_build_meta, formats:set[str] |
| `flowcli.cli:main` | `(argv: list[str] / None=None)` | `int` | ~2 site(s) · argv=None |
| `flowcli.discovery:_excluded` | `(rel_posix: str, name: str, excludes: Sequence[str])` | `bool` | ~2 site(s) · excludes:Sequence |
| `flowcli.discovery:_is_project_root` | `(path: Path)` | `bool` | ~2 site(s) · no args |
| `flowcli.discovery:_namespace_prefix` | `(start: Path)` | `tuple[Path, str]` | ~1 site(s) · start:root.resolve |
| `flowcli.discovery:derive_module_name` | `(file: Path, anchor: Path)` | `str` | ~3 site(s) · file:root.resolve |
| `flowcli.discovery:discover` | `(root: Path, excludes: Sequence[str]=())` | `list[tuple[str, Path]]` | ~1 site(s) · root:Path |
| `flowcli.discovery:find_package_prefix` | `(root: Path)` | `tuple[Path, str]` | ~3 site(s) · root:root.resolve |
| `flowcli.entrypoints:_console_scripts` | `(root: Path / None)` | `list[str]` | ~1 site(s) · root:Path |
| `flowcli.entrypoints:_defines_api` | `(mod: ModuleInfo)` | `bool` | ~1 site(s) · no args |
| `flowcli.entrypoints:_exported` | `(index: ProjectIndex)` | `set[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.entrypoints:_is_private_path` | `(mod_name: str, qual: str)` | `bool` | ~1 site(s) · no args |
| `flowcli.entrypoints:_script_to_node` | `(spec: str, index: ProjectIndex)` | `str / None` | ~1 site(s) · index:ProjectIndex |
| `flowcli.entrypoints:detect` | `(index: ProjectIndex, called: set[str], root: Path / None=None)` | `list[dict[str, Any]]` | ~1 site(s) · index:ProjectIndex, root:Path |
| `flowcli.entrypoints:detect.add` | `(nid: str, kind: str, score: int, why: str)` | `None` | ~7 site(s) · nid:node_id, kind='script'/'main', score=100/95 |
| `flowcli.graph:_annotate_flow` | `(flow: list[dict], calls: list[tuple[int, str]])` | `None` | ~4 site(s) · calls:list |
| `flowcli.graph:_annotate_ret_types` | `(flow: list[dict], line_map: dict[int, str])` | `None` | ~4 site(s) · line_map:dict |
| `flowcli.graph:_apply_edges` | `(nodes: dict[str, Node], resolved: list[ResolvedCall], include_external: bool)` | `list[UnresolvedCall]` | ~1 site(s) · nodes:_make_nodes, resolved:list, include_external:bool |
| `flowcli.graph:_find_module` | `(mod_part: str, index: ProjectIndex)` | `ModuleInfo` | ~1 site(s) · index:ProjectIndex |
| `flowcli.graph:_find_subtree` | `(mod_part: str, index: ProjectIndex)` | `tuple[str, list[str]] / None` | ~1 site(s) · index:ProjectIndex |
| `flowcli.graph:_make_nodes` | `(index: ProjectIndex, resolved: list[ResolvedCall])` | `dict[str, Node]` | ~1 site(s) · index:ProjectIndex, resolved:list |
| `flowcli.graph:apply_runtime` | `(graph: Graph, runtime: dict)` | `int` | ~1 site(s) · graph:build_graph, runtime:json.loads |
| `flowcli.graph:apply_simulation` | `(graph: Graph, index: ProjectIndex, resolved: list[ResolvedCall], entry_ids: list[str] / None=None)` | `list[list[str]]` | ~1 site(s) · graph:build_graph, index:ProjectIndex, resolved:resolve_all |
| `flowcli.graph:build_graph` | `(index: ProjectIndex, resolved: list[ResolvedCall], include_external: bool=False)` | `Graph` | ~1 site(s) · index:ProjectIndex, resolved:resolve_all |
| `flowcli.graph:compute_depths` | `(graph: Graph, entries: str / Sequence[str], max_depth: int / None=None)` | `int` | ~1 site(s) · graph:build_graph, entries:list |
| `flowcli.graph:parse_entry_spec` | `(spec: str, index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.graph:parse_entry_specs` | `(specs: Sequence[str], index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · specs:_entry_specs, index:ProjectIndex |
| `flowcli.graph:prune_unreachable` | `(graph: Graph)` | `int` | ~1 site(s) · graph:build_graph |
| `flowcli.infer:_raw_call_for` | `(parts: tuple[str, ...], fn: FunctionInfo)` | `RawCall` | ~2 site(s) · parts:tuple, fn:FunctionInfo |
| `flowcli.infer:_resolve_return_call` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...])` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.infer:_resolve_return_expr` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, tag: str, value: Any)` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.infer:infer_signatures` | `(index: ProjectIndex)` | `tuple[Signatures, RetLines]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.models:node_id` | `(module: str, qualname: str)` | `str` | ~20 site(s) · module:index.module_for, qualname:str |
| `flowcli.parser:_Collector.__init__` | `(self, info: ModuleInfo)` | `None` | ~1 site(s) · info:ModuleInfo |
| `flowcli.parser:parse_module` | `(module_name: str, file: Path)` | `ModuleInfo / ParseFailure` | ~1 site(s) · no args |
| `flowcli.parser:parse_source` | `(module_name: str, file: str, source: str, is_package: bool=False)` | `ModuleInfo / ParseFailure` | ~1 site(s) · module_name:str, source:fh.read |
| `flowcli.render_html:_class_payload` | `(class_graph: ClassGraph / None)` | `dict[str, Any]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.render_html:_module_of` | `(node_id: str)` | `str` | ~2 site(s) · no args |
| `flowcli.render_html:_node_entry` | `(n: Node, module_index: int)` | `dict[str, Any]` | ~1 site(s) · no args |
| `flowcli.render_html:build_payload` | `(graph: Graph, meta: dict[str, Any], runtime: dict[str, Any] / None=None)` | `dict[str, Any]` | ~1 site(s) · graph:Graph, meta:dict, runtime:dict |
| `flowcli.render_html:render_html` | `(graph: Graph, meta: dict[str, Any], out: Path, runtime: dict[str, Any] / None=None, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, class_graph:ClassGraph |
| `flowcli.report:_by_out_degree` | `(graph: Graph)` | `list[Node]` | ~2 site(s) · graph:Graph |
| `flowcli.report:_cell` | `(text: str)` | `str` | ~7 site(s) · text=f"{node.dynamic.get('ncalls', /f'~{sites} site(s) · {detail}' |
| `flowcli.report:_classes_section` | `(class_graph: ClassGraph / None)` | `list[str]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.report:_loc` | `(node: Node, root: str)` | `str` | ~1 site(s) · root:str |
| `flowcli.report:_most_called_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:_params_str` | `(node: Node)` | `str` | ~1 site(s) · no args |
| `flowcli.report:_returns_str` | `(node: Node)` | `str` | ~1 site(s) · no args |
| `flowcli.report:_runtime_str` | `(node: Node)` | `str` | ~1 site(s) · no args |
| `flowcli.report:_signatures_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:_unreachable_section` | `(graph: Graph, meta: dict[str, Any])` | `list[str]` | ~1 site(s) · graph:Graph, meta:dict |
| `flowcli.report:_unresolved_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:print_summary` | `(graph: Graph, meta: dict[str, Any])` | `None` | ~1 site(s) · graph:build_graph, meta:_build_meta |
| `flowcli.report:write_json` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, class_graph:ClassGraph |
| `flowcli.report:write_markdown` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, class_graph:ClassGraph |
| `flowcli.resolver:ProjectIndex.__init__` | `(self, modules: dict[str, ModuleInfo])` | `None` | ~1 site(s) · no args |
| `flowcli.resolver:ProjectIndex.module_for` | `(self, dotted: str)` | `str / None` | ~3 site(s) · dotted:str |
| `flowcli.resolver:_constructor` | `(index: ProjectIndex, module: str, class_qualname: str, expr: str)` | `Outcome` | ~5 site(s) · index:ProjectIndex, module:index.module_for, class_qualname:str |
| `flowcli.resolver:_external` | `(dotted: str)` | `Outcome` | ~2 site(s) · dotted=f'builtins.{name}' |
| `flowcli.resolver:_find_attr_type` | `(index: ProjectIndex, module: str, class_qualname: str, attr: str, _seen: set[tuple[str, str]] / None=None)` | `tuple[str, tuple[str, ...]] / None` | ~2 site(s) · index:ProjectIndex, class_qualname:str, attr:str |
| `flowcli.resolver:_find_class_by_dotted` | `(index: ProjectIndex, dotted: str, _seen: set[str] / None=None)` | `tuple[str, str] / None` | ~3 site(s) · index:ProjectIndex, _seen:set |
| `flowcli.resolver:_internal` | `(target_id: str)` | `Outcome` | ~11 site(s) · target_id:resolve_method |
| `flowcli.resolver:_resolve_absolute` | `(index: ProjectIndex, dotted: str, expr: str, _seen: set[str] / None=None)` | `Outcome` | ~4 site(s) · index:ProjectIndex, dotted=f'{star_mod}.{rem}', expr:str |
| `flowcli.resolver:_resolve_class_ref` | `(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...])` | `tuple[str, str] / None` | ~12 site(s) · index:ProjectIndex, mod:ModuleInfo, parts:caller.local_types.get |
| `flowcli.resolver:_resolve_dotted` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_enclosing_scope` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, name: str, hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_local_class_dotted` | `(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo |
| `flowcli.resolver:_resolve_name` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_name_imported` | `(index: ProjectIndex, mod: ModuleInfo, name: str, hint: str)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo |
| `flowcli.resolver:_resolve_one` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~3 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_self_attr_chain` | `(index: ProjectIndex, mod: ModuleInfo, class_qualname: str, call: RawCall)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, call:RawCall |
| `flowcli.resolver:_resolve_typed_local` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_unresolved` | `(expr: str, reason: str)` | `Outcome` | ~17 site(s) · expr:str, reason='instance-attr'/'not-found-in-hierarchy' |
| `flowcli.resolver:resolve_all` | `(index: ProjectIndex)` | `list[ResolvedCall]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.resolver:resolve_method` | `(index: ProjectIndex, module: str, class_qualname: str, method: str, skip_self: bool=False, _seen: set[tuple[str, str]] / None=None)` | `str / None` | ~8 site(s) · index:ProjectIndex, module:index.module_for, class_qualname:str |
| `flowcli.simulate:_Site.__init__` | `(self, caller: str, target: str, lineno: int, pairs: list[tuple[str, tuple[str, Any]]])` | `None` | ~1 site(s) · pairs:list |
| `flowcli.simulate:_absorb` | `(slot: dict[str, Any], types: list[str], value: str / None, source: str)` | `bool` | ~3 site(s) · types=[str(p['ann'])]/[], value=None, source='(entry)'/'(default)' |
| `flowcli.simulate:_bind_site` | `(rc: ResolvedCall, fns: dict[str, FunctionInfo])` | `_Site / None` | ~1 site(s) · fns:_function_index |
| `flowcli.simulate:_eval_atom` | `(index: ProjectIndex, fns: dict[str, FunctionInfo], records: dict[str, dict[str, Any]], signatures: dict[str, dict[str, Any]], caller_id: str, atom: tuple[str, Any])` | `tuple[list[str], str / None]` | ~1 site(s) · index:ProjectIndex, fns:_function_index, records:dict |
| `flowcli.simulate:_function_index` | `(index: ProjectIndex)` | `dict[str, FunctionInfo]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.simulate:_returns_of_call` | `(index: ProjectIndex, mod: ModuleInfo, caller: FunctionInfo, signatures: dict[str, dict[str, Any]], parts: tuple[str, ...])` | `list[str]` | ~1 site(s) · index:ProjectIndex, mod:index.modules.get, caller:fns.get |
| `flowcli.simulate:_seed_entry` | `(rec: dict[str, Any] / None, fn: FunctionInfo / None)` | `None` | ~1 site(s) · no args |
| `flowcli.simulate:_simulated_events` | `(sites: list[_Site], entry_ids: list[str])` | `list[list[str]]` | ~1 site(s) · no args |
| `flowcli.simulate:_walk` | `(node: str, out_edges: dict[str, list[tuple[int, str]]], stack: set[str], events: list[list[str]])` | `None` | ~2 site(s) · out_edges:dict, stack:set, events:list |
| `flowcli.simulate:module_entry_candidates` | `(index: ProjectIndex)` | `list[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.simulate:simulate` | `(index: ProjectIndex, resolved: list[ResolvedCall], signatures: dict[str, dict[str, Any]], entry_ids: list[str] / None=None)` | `tuple[dict[str, dict[str, Any]], list[list[str]]]` | ~1 site(s) · index:ProjectIndex, resolved:list |
| `flowcli.tracer:capture` | `(root: Path, samples: bool=True)` | `Iterator[RuntimeCapture]` | ~1 site(s) · root:Path, samples:bool |

## Classes

| Class | Kind | Inherits | Properties | Holds |
|---|---|---|---|---|
| `flowcli.classes:ClassEdge` | dataclass | — | source: str, target: str, kind: str, label: str | — |
| `flowcli.classes:ClassGraph` | dataclass | — | nodes: dict[str, ClassNode], edges: list[ClassEdge] | — |
| `flowcli.classes:ClassNode` | dataclass | — | id: str, module: str, name: str, file: str, lineno: int, stereotype: str, … +4 | — |
| `flowcli.graph:Graph` | dataclass | — | nodes: dict[str, Node], unresolved: list[UnresolvedCall], entry: str / None | — |
| `flowcli.models:CallKind` | enum | enum.Enum | NAME, DOTTED, SELF_ATTR, CLS_ATTR, SUPER_ATTR, OPAQUE | — |
| `flowcli.models:ClassInfo` | dataclass | — | qualname: str, module: str, lineno: int, bases: list[tuple[str, ...]], base_reprs: list[str], methods: dict[str, str], … +3 | — |
| `flowcli.models:FunctionInfo` | dataclass | — | qualname: str, module: str, file: str, lineno: int, class_qualname: str / None, raw_calls: list[RawCall], … +8 | — |
| `flowcli.models:ModuleInfo` | dataclass | — | name: str, file: str, is_package: bool, imports: dict[str, str], star_imports: list[str], functions: dict[str, FunctionInfo], … +2 | — |
| `flowcli.models:Node` | dataclass | — | id: str, file: str, lineno: int, calls: list[str], called_by: list[str], depth: int / None, … +7 | — |
| `flowcli.models:ParseFailure` | dataclass | — | file: str, error: str | — |
| `flowcli.models:RawCall` | dataclass | — | kind: CallKind, parts: tuple[str, ...], lineno: int, repr_hint: str, args: tuple[ArgAtom, ...] | kind → CallKind |
| `flowcli.models:UnresolvedCall` | dataclass | — | caller: str, callee_expr: str, lineno: int, reason: str | — |
| `flowcli.parser:_Collector` | class | ast.NodeVisitor | _stack: list[tuple[str, str]], _sink: FunctionInfo / None, visit_Yield, visit_YieldFrom | _sink → FunctionInfo |
| `flowcli.resolver:ProjectIndex` | class | — | — | — |
| `flowcli.resolver:ResolvedCall` | dataclass | — | caller: str, lineno: int, status: str, target: str, reason: str, call: RawCall / None | call → RawCall |
| `flowcli.simulate:_Site` | class | — | __slots__ | — |
| `flowcli.tracer:RuntimeCapture` | dataclass | — | functions: dict[str, dict[str, Any]], events: list[list[str]], calls_total: int, events_truncated: bool | — |

## Unresolved calls

- **instance-attr**: 280
- **external**: 250
- **opaque**: 82
- **not-found-in-hierarchy**: 19
- **unknown-name**: 1

| Callee expression | Occurrences |
|---|---:|
| `builtins.len` | 57 |
| `builtins.sorted` | 38 |
| `builtins.print` | 23 |
| `p.add_argument` | 18 |
| `builtins.set` | 17 |
| `builtins.str` | 16 |
| `meta.get` | 16 |
| `'.'.join` | 15 |
| `builtins.list` | 13 |
| `pathlib.Path` | 13 |
| `', '.join` | 13 |
| `index.modules.get` | 10 |
| `graph.nodes.values` | 9 |
| `item.get` | 8 |
| `builtins.ValueError` | 7 |
