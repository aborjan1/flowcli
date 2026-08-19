# flowcli report

**16** modules · **160** nodes · **249** edges · **855** unresolved calls · entry `flowcli/ (16 modules)` (0 unreachable)

## Call graph

| Node | Kind | File:Line | Out | In | Depth |
|---|---|---|---:|---:|---:|
| `flowcli.cli:_cmd_map` | function | cli.py:125 | 17 | 1 | 0 |
| `flowcli.resolver:_resolve_absolute` | function | resolver.py:264 | 8 | 3 | 0 |
| `flowcli.parser:_Collector._handle_function` | method | parser.py:141 | 8 | 2 | 0 |
| `flowcli.entrypoints:detect` | function | entrypoints.py:22 | 7 | 1 | 0 |
| `flowcli.report:write_markdown` | function | report.py:45 | 7 | 1 | 0 |
| `flowcli.resolver:_resolve_name` | function | resolver.py:150 | 7 | 1 | 0 |
| `flowcli.simulate:simulate` | function | simulate.py:46 | 7 | 1 | 0 |
| `flowcli.resolver:_resolve_one` | function | resolver.py:77 | 6 | 3 | 0 |
| `flowcli.resolver:_resolve_name_imported` | function | resolver.py:189 | 6 | 1 | 0 |
| `flowcli.parser:_flow_of_stmt` | function | parser.py:385 | 5 | 1 | 0 |
| `flowcli.resolver:_resolve_self_attr_chain` | function | resolver.py:100 | 5 | 1 | 0 |
| `flowcli.cli:main` | function | cli.py:50 | 4 | 2 | 0 |
| `flowcli.classes:build_class_graph` | function | classes.py:56 | 4 | 1 | 0 |
| `flowcli.graph:_make_nodes` | function | graph.py:46 | 4 | 1 | 0 |
| `flowcli.graph:parse_entry_spec` | function | graph.py:238 | 4 | 1 | 0 |
| `flowcli.resolver:_resolve_dotted` | function | resolver.py:205 | 4 | 1 | 0 |
| `flowcli.resolver:_resolve_local_class_dotted` | function | resolver.py:243 | 4 | 1 | 0 |
| `flowcli.resolver:_resolve_typed_local` | function | resolver.py:226 | 4 | 1 | 0 |
| `flowcli.tracer:capture.on_call` | function | tracer.py:114 | 4 | 1 | 0 |
| `flowcli.parser:_Collector.visit_Assign` | method | parser.py:282 | 4 | 0 | 0 |
| `flowcli.parser:_Collector.visit_ClassDef` | method | parser.py:183 | 4 | 0 | 0 |
| `flowcli.resolver:resolve_method` | function | resolver.py:303 | 3 | 8 | 0 |
| `flowcli.resolver:_constructor` | function | resolver.py:258 | 3 | 5 | 0 |
| `flowcli.parser:_Collector._visit_decorators` | method | parser.py:119 | 3 | 2 | 0 |
| `flowcli.classes:_make_node` | function | classes.py:74 | 3 | 1 | 0 |
| `flowcli.cli:_cmd_run` | function | cli.py:235 | 3 | 1 | 0 |
| `flowcli.cli:_write_outputs` | function | cli.py:216 | 3 | 1 | 0 |
| `flowcli.discovery:discover` | function | discovery.py:104 | 3 | 1 | 0 |
| `flowcli.infer:_resolve_return_call` | function | infer.py:111 | 3 | 1 | 0 |
| `flowcli.parser:_flow_of_try` | function | parser.py:444 | 3 | 1 | 0 |
| `flowcli.report:_signatures_section` | function | report.py:119 | 3 | 1 | 0 |
| `flowcli.resolver:_resolve_enclosing_scope` | function | resolver.py:170 | 3 | 1 | 0 |
| `flowcli.simulate:_returns_of_call` | function | simulate.py:201 | 3 | 1 | 0 |
| `flowcli.parser:_Collector.visit_AnnAssign` | method | parser.py:302 | 3 | 0 | 0 |
| `flowcli.parser:_Collector.visit_Call` | method | parser.py:343 | 3 | 0 | 0 |
| `flowcli.parser:_annotation_parts` | function | parser.py:597 | 2 | 3 | 0 |
| `flowcli.parser:_Collector._classify_callable_expr` | method | parser.py:88 | 2 | 2 | 0 |
| `flowcli.parser:_Collector._record_self_attr` | method | parser.py:249 | 2 | 2 | 0 |
| `flowcli.resolver:_find_attr_type` | function | resolver.py:119 | 2 | 2 | 0 |
| `flowcli.resolver:_find_class_by_dotted` | function | resolver.py:359 | 2 | 2 | 0 |
| `flowcli.classes:_add_inheritance` | function | classes.py:126 | 2 | 1 | 0 |
| `flowcli.cli:_execute` | function | cli.py:282 | 2 | 1 | 0 |
| `flowcli.discovery:_namespace_prefix` | function | discovery.py:60 | 2 | 1 | 0 |
| `flowcli.entrypoints:_exported` | function | entrypoints.py:75 | 2 | 1 | 0 |
| `flowcli.graph:apply_simulation` | function | graph.py:30 | 2 | 1 | 0 |
| `flowcli.graph:build_graph` | function | graph.py:23 | 2 | 1 | 0 |
| `flowcli.infer:_resolve_return_expr` | function | infer.py:94 | 2 | 1 | 0 |
| `flowcli.infer:infer_signatures` | function | infer.py:29 | 2 | 1 | 0 |
| `flowcli.parser:_Collector._classify_attribute` | method | parser.py:97 | 2 | 1 | 0 |
| `flowcli.parser:_classify_arg_expr` | function | parser.py:540 | 2 | 1 | 0 |
| `flowcli.render_html:build_payload` | function | render_html.py:60 | 2 | 1 | 0 |
| `flowcli.render_html:render_html` | function | render_html.py:133 | 2 | 1 | 0 |
| `flowcli.resolver:resolve_all` | function | resolver.py:41 | 2 | 1 | 0 |
| `flowcli.simulate:_bind_site` | function | simulate.py:102 | 2 | 1 | 0 |
| `flowcli.simulate:_eval_atom` | function | simulate.py:159 | 2 | 1 | 0 |
| `flowcli.tracer:capture.node_for` | function | tracer.py:99 | 2 | 1 | 0 |
| `flowcli.tracer:capture.on_return` | function | tracer.py:147 | 2 | 1 | 0 |
| `flowcli.tracer:capture.profiler` | function | tracer.py:162 | 2 | 0 | 0 |
| `flowcli.resolver:_resolve_class_ref` | function | resolver.py:342 | 1 | 10 | 0 |
| `flowcli.parser:_flow_of_body` | function | parser.py:374 | 1 | 3 | 0 |
| `flowcli.discovery:find_package_prefix` | function | discovery.py:29 | 1 | 2 | 0 |
| `flowcli.graph:_annotate_flow` | function | graph.py:104 | 1 | 2 | 0 |
| `flowcli.graph:_annotate_ret_types` | function | graph.py:123 | 1 | 2 | 0 |
| `flowcli.parser:_Collector._record_call` | method | parser.py:85 | 1 | 2 | 0 |
| `flowcli.simulate:_walk` | function | simulate.py:240 | 1 | 2 | 0 |
| `flowcli.cli:_entry_specs` | function | cli.py:120 | 1 | 1 | 0 |
| `flowcli.cli:_parse_all` | function | cli.py:334 | 1 | 1 | 0 |
| `flowcli.cli:_resolve_entry` | function | cli.py:109 | 1 | 1 | 0 |
| `flowcli.entrypoints:_script_to_node` | function | entrypoints.py:108 | 1 | 1 | 0 |
| `flowcli.graph:_find_subtree` | function | graph.py:267 | 1 | 1 | 0 |
| `flowcli.graph:parse_entry_specs` | function | graph.py:200 | 1 | 1 | 0 |
| `flowcli.parser:_classify_args` | function | parser.py:514 | 1 | 1 | 0 |
| `flowcli.parser:_classify_return_expr` | function | parser.py:558 | 1 | 1 | 0 |
| `flowcli.parser:_is_overload_stub` | function | parser.py:587 | 1 | 1 | 0 |
| `flowcli.parser:_literal_arg` | function | parser.py:524 | 1 | 1 | 0 |
| `flowcli.parser:_param_list` | function | parser.py:477 | 1 | 1 | 0 |
| `flowcli.parser:_param_list.entry` | function | parser.py:480 | 1 | 1 | 0 |
| `flowcli.parser:parse_module` | function | parser.py:22 | 1 | 1 | 0 |
| `flowcli.parser:parse_source` | function | parser.py:31 | 1 | 1 | 0 |
| `flowcli.report:_classes_section` | function | report.py:71 | 1 | 1 | 0 |
| `flowcli.report:_params_str` | function | report.py:145 | 1 | 1 | 0 |
| `flowcli.report:_returns_str` | function | report.py:158 | 1 | 1 | 0 |
| `flowcli.report:_runtime_str` | function | report.py:167 | 1 | 1 | 0 |
| `flowcli.report:print_summary` | function | report.py:184 | 1 | 1 | 0 |
| `flowcli.simulate:_function_index` | function | simulate.py:94 | 1 | 1 | 0 |
| `flowcli.simulate:_seed_entry` | function | simulate.py:131 | 1 | 1 | 0 |
| `flowcli.simulate:_simulated_events` | function | simulate.py:219 | 1 | 1 | 0 |
| `flowcli.simulate:module_entry_candidates` | function | simulate.py:252 | 1 | 1 | 0 |
| `flowcli.tracer:capture` | function | tracer.py:74 | 1 | 1 | 0 |
| `flowcli.tracer:capture.module_of` | function | tracer.py:87 | 1 | 1 | 0 |
| `flowcli.__main__:<module>` | module | __main__.py:1 | 1 | 0 | 0 |
| `flowcli.parser:_Collector.visit_AsyncFunctionDef` | method | parser.py:138 | 1 | 0 | 0 |
| `flowcli.parser:_Collector.visit_FunctionDef` | method | parser.py:135 | 1 | 0 | 0 |
| `flowcli.parser:_Collector.visit_If` | method | parser.py:320 | 1 | 0 | 0 |
| `flowcli.parser:_Collector.visit_ImportFrom` | method | parser.py:221 | 1 | 0 | 0 |
| `flowcli.parser:_Collector.visit_Return` | method | parser.py:327 | 1 | 0 | 0 |
| `flowcli.models:node_id` | function | models.py:112 | 0 | 16 | 0 |
| `flowcli.parser:_safe_unparse` | function | parser.py:41 | 0 | 11 | 0 |
| `flowcli.resolver:_internal` | function | resolver.py:65 | 0 | 9 | 0 |
| `flowcli.resolver:_unresolved` | function | resolver.py:73 | 0 | 9 | 0 |
| `flowcli.parser:_dotted_parts` | function | parser.py:619 | 0 | 6 | 0 |
| `flowcli.report:_cell` | function | report.py:141 | 0 | 4 | 0 |
| `flowcli.classes:class_id` | function | classes.py:52 | 0 | 3 | 0 |
| `flowcli.parser:_Collector._nearest_class` | method | parser.py:67 | 0 | 3 | 0 |
| `flowcli.resolver:ProjectIndex.module_for` | method | resolver.py:31 | 0 | 3 | 0 |
| `flowcli.discovery:derive_module_name` | function | discovery.py:90 | 0 | 2 | 0 |
| `flowcli.graph:split_entry_spec` | function | graph.py:222 | 0 | 2 | 0 |
| `flowcli.infer:_raw_call_for` | function | infer.py:128 | 0 | 2 | 0 |
| `flowcli.parser:_Collector._qual` | method | parser.py:64 | 0 | 2 | 0 |
| `flowcli.parser:_Collector._record_field` | method | parser.py:262 | 0 | 2 | 0 |
| `flowcli.parser:_short` | function | parser.py:369 | 0 | 2 | 0 |
| `flowcli.report:_by_out_degree` | function | report.py:41 | 0 | 2 | 0 |
| `flowcli.resolver:_external` | function | resolver.py:69 | 0 | 2 | 0 |
| `flowcli.simulate:_absorb` | function | simulate.py:145 | 0 | 2 | 0 |
| `flowcli.simulate:_param_names` | function | simulate.py:28 | 0 | 2 | 0 |
| `flowcli.tracer:_safe_repr` | function | tracer.py:53 | 0 | 2 | 0 |
| `flowcli.tracer:_type_name` | function | tracer.py:46 | 0 | 2 | 0 |
| `flowcli.classes:_add_composition` | function | classes.py:135 | 0 | 1 | 0 |
| `flowcli.classes:_stereotype` | function | classes.py:111 | 0 | 1 | 0 |
| `flowcli.classes:scope_class_graph` | function | classes.py:148 | 0 | 1 | 0 |
| `flowcli.cli:_add_map_parser` | function | cli.py:72 | 0 | 1 | 0 |
| `flowcli.cli:_add_run_parser` | function | cli.py:95 | 0 | 1 | 0 |
| `flowcli.cli:_build_meta` | function | cli.py:347 | 0 | 1 | 0 |
| `flowcli.cli:_exit_code_of` | function | cli.py:307 | 0 | 1 | 0 |
| `flowcli.cli:_runtime_payload` | function | cli.py:314 | 0 | 1 | 0 |
| `flowcli.discovery:_excluded` | function | discovery.py:100 | 0 | 1 | 0 |
| `flowcli.discovery:_holds_modules` | function | discovery.py:52 | 0 | 1 | 0 |
| `flowcli.discovery:_is_project_root` | function | discovery.py:48 | 0 | 1 | 0 |
| `flowcli.entrypoints:_console_scripts` | function | entrypoints.py:91 | 0 | 1 | 0 |
| `flowcli.entrypoints:_defines_api` | function | entrypoints.py:64 | 0 | 1 | 0 |
| `flowcli.entrypoints:_is_private_path` | function | entrypoints.py:69 | 0 | 1 | 0 |
| `flowcli.entrypoints:detect.add` | function | entrypoints.py:26 | 0 | 1 | 0 |
| `flowcli.graph:_apply_edges` | function | graph.py:78 | 0 | 1 | 0 |
| `flowcli.graph:_find_module` | function | graph.py:290 | 0 | 1 | 0 |
| `flowcli.graph:apply_runtime` | function | graph.py:142 | 0 | 1 | 0 |
| `flowcli.graph:compute_depths` | function | graph.py:153 | 0 | 1 | 0 |
| `flowcli.graph:prune_unreachable` | function | graph.py:181 | 0 | 1 | 0 |
| `flowcli.parser:_Collector.__init__` | method | parser.py:57 | 0 | 1 | 0 |
| `flowcli.parser:_Collector._ensure_module_fn` | method | parser.py:73 | 0 | 1 | 0 |
| `flowcli.parser:_Collector._resolve_from_base` | method | parser.py:233 | 0 | 1 | 0 |
| `flowcli.parser:_end` | function | parser.py:463 | 0 | 1 | 0 |
| `flowcli.parser:_is_main_guard` | function | parser.py:467 | 0 | 1 | 0 |
| `flowcli.render_html:_class_payload` | function | render_html.py:100 | 0 | 1 | 0 |
| `flowcli.render_html:_module_of` | function | render_html.py:19 | 0 | 1 | 0 |
| `flowcli.render_html:_node_entry` | function | render_html.py:23 | 0 | 1 | 0 |
| `flowcli.report:_loc` | function | report.py:31 | 0 | 1 | 0 |
| `flowcli.report:_most_called_section` | function | report.py:91 | 0 | 1 | 0 |
| `flowcli.report:_unreachable_section` | function | report.py:104 | 0 | 1 | 0 |
| `flowcli.report:_unresolved_section` | function | report.py:129 | 0 | 1 | 0 |
| `flowcli.report:write_json` | function | report.py:17 | 0 | 1 | 0 |
| `flowcli.resolver:ProjectIndex.__init__` | method | resolver.py:28 | 0 | 1 | 0 |
| `flowcli.simulate:_Site.__init__` | method | simulate.py:39 | 0 | 1 | 0 |
| `flowcli.tracer:_param_names` | function | tracer.py:60 | 0 | 1 | 0 |
| `flowcli.classes:<module>` | module | classes.py:1 | 0 | 0 | 0 |
| `flowcli.graph:<module>` | module | graph.py:1 | 0 | 0 | 0 |
| `flowcli.models:<module>` | module | models.py:1 | 0 | 0 | 0 |
| `flowcli.parser:_Collector._mark_generator` | method | parser.py:333 | 0 | 0 | 0 |
| `flowcli.parser:_Collector.visit_Import` | method | parser.py:213 | 0 | 0 | 0 |
| `flowcli.resolver:<module>` | module | resolver.py:1 | 0 | 0 | 0 |
| `flowcli.tracer:<module>` | module | tracer.py:1 | 0 | 0 | 0 |

## Top 10 most-called

| Node | In | Called by |
|---|---:|---|
| `flowcli.models:node_id` | 16 | `flowcli.entrypoints:_exported`, `flowcli.entrypoints:_script_to_node`, `flowcli.entrypoints:detect`, `flowcli.graph:_find_subtree`, `flowcli.graph:_make_nodes`, … +11 |
| `flowcli.parser:_safe_unparse` | 11 | `flowcli.parser:_Collector._classify_attribute`, `flowcli.parser:_Collector._classify_callable_expr`, `flowcli.parser:_Collector._handle_function`, `flowcli.parser:_Collector._visit_decorators`, `flowcli.parser:_Collector.visit_AnnAssign`, … +6 |
| `flowcli.resolver:_resolve_class_ref` | 10 | `flowcli.classes:_add_inheritance`, `flowcli.classes:_make_node`, `flowcli.infer:_resolve_return_call`, `flowcli.infer:_resolve_return_expr`, `flowcli.resolver:_find_attr_type`, … +5 |
| `flowcli.resolver:_internal` | 9 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_enclosing_scope`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, … +4 |
| `flowcli.resolver:_unresolved` | 9 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_dotted`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, … +4 |
| `flowcli.resolver:resolve_method` | 8 | `flowcli.resolver:_constructor`, `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, `flowcli.resolver:_resolve_one`, … +3 |
| `flowcli.parser:_dotted_parts` | 6 | `flowcli.parser:_Collector.visit_Assign`, `flowcli.parser:_Collector.visit_ClassDef`, `flowcli.parser:_annotation_parts`, `flowcli.parser:_classify_arg_expr`, `flowcli.parser:_classify_return_expr`, … +1 |
| `flowcli.resolver:_constructor` | 5 | `flowcli.resolver:_resolve_absolute`, `flowcli.resolver:_resolve_enclosing_scope`, `flowcli.resolver:_resolve_local_class_dotted`, `flowcli.resolver:_resolve_name`, `flowcli.resolver:_resolve_name_imported` |
| `flowcli.report:_cell` | 4 | `flowcli.report:_classes_section`, `flowcli.report:_params_str`, `flowcli.report:_returns_str`, `flowcli.report:_runtime_str` |
| `flowcli.classes:class_id` | 3 | `flowcli.classes:_add_inheritance`, `flowcli.classes:_make_node`, `flowcli.classes:build_class_graph` |

## Unreachable from `flowcli/ (16 modules)`

_0 function(s) outside this call graph were pruned from the report (rerun with --keep-unreachable to include them)._

## Signatures

| Node | Signature | Returns | Data flow |
|---|---|---|---|
| `flowcli.classes:_add_composition` | `(node: ClassNode, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · node:ClassNode, nid:str, graph:ClassGraph |
| `flowcli.classes:_add_inheritance` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, ci:ClassInfo |
| `flowcli.classes:_make_node` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo)` | `ClassNode` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, ci:ClassInfo |
| `flowcli.classes:_stereotype` | `(ci: ClassInfo)` | `str` | ~1 site(s) · ci:ClassInfo |
| `flowcli.classes:build_class_graph` | `(index: ProjectIndex)` | `ClassGraph` | ~1 site(s) · index:ProjectIndex |
| `flowcli.classes:class_id` | `(module: str, qualname: str)` | `str` | ~5 site(s) · module:str, qualname:str |
| `flowcli.classes:scope_class_graph` | `(graph: ClassGraph, keep_modules: set[str])` | `ClassGraph` | ~1 site(s) · graph:ClassGraph, keep_modules={nid.split(':', 1)[0] for nid  |
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
| `flowcli.discovery:_excluded` | `(rel_posix: str, name: str, excludes: Sequence[str])` | `bool` | ~2 site(s) · rel_posix:str, name:str, excludes:Sequence |
| `flowcli.discovery:_holds_modules` | `(path: Path)` | `bool` | ~1 site(s) · path:Path |
| `flowcli.discovery:_is_project_root` | `(path: Path)` | `bool` | ~3 site(s) · path:Path |
| `flowcli.discovery:_namespace_prefix` | `(start: Path)` | `tuple[Path, str]` | ~1 site(s) · start:Path |
| `flowcli.discovery:derive_module_name` | `(file: Path, anchor: Path)` | `str` | ~3 site(s) · file:Path, anchor:Path |
| `flowcli.discovery:discover` | `(root: Path, excludes: Sequence[str]=())` | `list[tuple[str, Path]]` | ~1 site(s) · root:Path, excludes=() |
| `flowcli.discovery:find_package_prefix` | `(root: Path)` | `tuple[Path, str]` | ~3 site(s) · root:Path |
| `flowcli.entrypoints:_console_scripts` | `(root: Path / None)` | `list[str]` | ~1 site(s) · root:Path |
| `flowcli.entrypoints:_defines_api` | `(mod: ModuleInfo)` | `bool` | ~1 site(s) · mod:ModuleInfo |
| `flowcli.entrypoints:_exported` | `(index: ProjectIndex)` | `set[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.entrypoints:_is_private_path` | `(mod_name: str, qual: str)` | `bool` | ~1 site(s) · mod_name:str, qual:str |
| `flowcli.entrypoints:_script_to_node` | `(spec: str, index: ProjectIndex)` | `str / None` | ~1 site(s) · spec:str, index:ProjectIndex |
| `flowcli.entrypoints:detect` | `(index: ProjectIndex, called: set[str], root: Path / None=None)` | `list[dict[str, Any]]` | ~1 site(s) · index:ProjectIndex, called:set[str], root=None |
| `flowcli.entrypoints:detect.add` | `(nid: str, kind: str, score: int, why: str)` | `None` | ~7 site(s) · nid:node_id, kind='script'/'main', score=100/95 |
| `flowcli.graph:_annotate_flow` | `(flow: list[dict], calls: list[tuple[int, str]])` | `None` | ~4 site(s) · flow:list[dict], calls:list |
| `flowcli.graph:_annotate_ret_types` | `(flow: list[dict], line_map: dict[int, str])` | `None` | ~4 site(s) · flow:list[dict], line_map:dict |
| `flowcli.graph:_apply_edges` | `(nodes: dict[str, Node], resolved: list[ResolvedCall], include_external: bool)` | `list[UnresolvedCall]` | ~1 site(s) · nodes:_make_nodes, resolved:list, include_external:bool |
| `flowcli.graph:_find_module` | `(mod_part: str, index: ProjectIndex)` | `ModuleInfo` | ~1 site(s) · mod_part:str, index:ProjectIndex |
| `flowcli.graph:_find_subtree` | `(mod_part: str, index: ProjectIndex)` | `tuple[str, list[str]] / None` | ~1 site(s) · mod_part:str, index:ProjectIndex |
| `flowcli.graph:_make_nodes` | `(index: ProjectIndex, resolved: list[ResolvedCall])` | `dict[str, Node]` | ~1 site(s) · index:ProjectIndex, resolved:list |
| `flowcli.graph:apply_runtime` | `(graph: Graph, runtime: dict)` | `int` | ~1 site(s) · graph:Graph, runtime:dict |
| `flowcli.graph:apply_simulation` | `(graph: Graph, index: ProjectIndex, resolved: list[ResolvedCall], entry_ids: list[str] / None=None)` | `list[list[str]]` | ~1 site(s) · graph:Graph, index:ProjectIndex, resolved:list[ResolvedCall] |
| `flowcli.graph:build_graph` | `(index: ProjectIndex, resolved: list[ResolvedCall], include_external: bool=False)` | `Graph` | ~1 site(s) · index:ProjectIndex, resolved:list[ResolvedCall], include_external=False |
| `flowcli.graph:compute_depths` | `(graph: Graph, entries: str / Sequence[str], max_depth: int / None=None)` | `int` | ~1 site(s) · graph:Graph, entries:list, max_depth=None |
| `flowcli.graph:parse_entry_spec` | `(spec: str, index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · spec:str, index:ProjectIndex |
| `flowcli.graph:parse_entry_specs` | `(specs: Sequence[str], index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · specs:Sequence[str], index:ProjectIndex |
| `flowcli.graph:prune_unreachable` | `(graph: Graph)` | `int` | ~1 site(s) · graph:Graph |
| `flowcli.graph:split_entry_spec` | `(spec: str)` | `tuple[str, str / None]` | ~2 site(s) · spec:str |
| `flowcli.infer:_raw_call_for` | `(parts: tuple[str, ...], fn: FunctionInfo)` | `RawCall` | ~2 site(s) · parts:tuple, fn:FunctionInfo |
| `flowcli.infer:_resolve_return_call` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...])` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.infer:_resolve_return_expr` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, tag: str, value: Any)` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.infer:infer_signatures` | `(index: ProjectIndex)` | `tuple[Signatures, RetLines]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.models:node_id` | `(module: str, qualname: str)` | `str` | ~20 site(s) · module:index.module_for, qualname:str |
| `flowcli.parser:_Collector.__init__` | `(self, info: ModuleInfo)` | `None` | ~1 site(s) · info:ModuleInfo |
| `flowcli.parser:_Collector._classify_attribute` | `(self, expr: ast.Attribute, lineno: int)` | `RawCall` | ~1 site(s) · expr:ast.Attribute, lineno:int |
| `flowcli.parser:_Collector._classify_callable_expr` | `(self, expr: ast.expr, lineno: int)` | `RawCall / None` | ~2 site(s) · expr:ast.expr, lineno:int |
| `flowcli.parser:_Collector._ensure_module_fn` | `(self)` | `FunctionInfo` | ~1 site(s) · no args |
| `flowcli.parser:_Collector._handle_function` | `(self, node: ast.FunctionDef / ast.AsyncFunctionDef)` | `None` | ~2 site(s) · node:ast.AsyncFunctionDef |
| `flowcli.parser:_Collector._mark_generator` | `(self, node: ast.Yield / ast.YieldFrom)` | `None` | ~0 site(s) · node:ast.Yield / ast.YieldFrom |
| `flowcli.parser:_Collector._nearest_class` | `(self)` | `str / None` | ~3 site(s) · no args |
| `flowcli.parser:_Collector._qual` | `(self, name: str)` | `str` | ~2 site(s) · name:str |
| `flowcli.parser:_Collector._record_call` | `(self, rc: RawCall)` | `None` | ~2 site(s) · rc:RawCall |
| `flowcli.parser:_Collector._record_field` | `(self, ci: ClassInfo, name: str, ann: str / None=None, parts: tuple[str, ...]=(), value: str / None=None, lineno: int=0, source: str='class')` | `None` | ~2 site(s) · ci:ClassInfo, name:str, ann=None |
| `flowcli.parser:_Collector._record_self_attr` | `(self, attr: str, parts: tuple[str, ...], ann: str / None=None, lineno: int=0, source: str='init')` | `None` | ~4 site(s) · attr:str, parts:_annotation_parts, ann=None |
| `flowcli.parser:_Collector._resolve_from_base` | `(self, node: ast.ImportFrom)` | `str / None` | ~1 site(s) · node:ast.ImportFrom |
| `flowcli.parser:_Collector._visit_decorators` | `(self, node: ast.FunctionDef / ast.AsyncFunctionDef /)` | `list[str]` | ~2 site(s) · node:ast.ClassDef |
| `flowcli.parser:_Collector.visit_AnnAssign` | `(self, node: ast.AnnAssign)` | `None` | ~0 site(s) · node:ast.AnnAssign |
| `flowcli.parser:_Collector.visit_Assign` | `(self, node: ast.Assign)` | `None` | ~0 site(s) · node:ast.Assign |
| `flowcli.parser:_Collector.visit_AsyncFunctionDef` | `(self, node: ast.AsyncFunctionDef)` | `None` | ~0 site(s) · node:ast.AsyncFunctionDef |
| `flowcli.parser:_Collector.visit_Call` | `(self, node: ast.Call)` | `None` | ~0 site(s) · node:ast.Call |
| `flowcli.parser:_Collector.visit_ClassDef` | `(self, node: ast.ClassDef)` | `None` | ~0 site(s) · node:ast.ClassDef |
| `flowcli.parser:_Collector.visit_FunctionDef` | `(self, node: ast.FunctionDef)` | `None` | ~0 site(s) · node:ast.FunctionDef |
| `flowcli.parser:_Collector.visit_If` | `(self, node: ast.If)` | `None` | ~0 site(s) · node:ast.If |
| `flowcli.parser:_Collector.visit_Import` | `(self, node: ast.Import)` | `None` | ~0 site(s) · node:ast.Import |
| `flowcli.parser:_Collector.visit_ImportFrom` | `(self, node: ast.ImportFrom)` | `None` | ~0 site(s) · node:ast.ImportFrom |
| `flowcli.parser:_Collector.visit_Return` | `(self, node: ast.Return)` | `None` | ~0 site(s) · node:ast.Return |
| `flowcli.parser:_annotation_parts` | `(node: ast.expr)` | `tuple[str, ...]` | ~7 site(s) · node:ast.expr |
| `flowcli.parser:_classify_arg_expr` | `(value: ast.expr)` | `tuple[str, Any]` | ~2 site(s) · value:ast.expr |
| `flowcli.parser:_classify_args` | `(node: ast.Call)` | `tuple[ArgAtom, ...]` | ~1 site(s) · node:ast.Call |
| `flowcli.parser:_classify_return_expr` | `(value: ast.expr / None)` | `tuple[str, Any]` | ~1 site(s) · value:ast.expr / None |
| `flowcli.parser:_dotted_parts` | `(node: ast.expr)` | `tuple[str, ...]` | ~8 site(s) · node:ast.expr |
| `flowcli.parser:_end` | `(stmt: ast.stmt)` | `int` | ~2 site(s) · stmt:ast.stmt |
| `flowcli.parser:_flow_of_body` | `(body: list[ast.stmt], budget: list[int])` | `list[dict]` | ~10 site(s) · body:list[ast.stmt], budget=[_MAX_FLOW_NODES] |
| `flowcli.parser:_flow_of_stmt` | `(stmt: ast.stmt, budget: list[int])` | `dict` | ~1 site(s) · stmt:ast.stmt, budget:list |
| `flowcli.parser:_flow_of_try` | `(stmt: ast.Try / ast.TryStar, budget: list[int])` | `dict` | ~1 site(s) · stmt:ast.Try / ast.TryStar, budget:list |
| `flowcli.parser:_is_main_guard` | `(test: ast.expr)` | `bool` | ~1 site(s) · test:ast.expr |
| `flowcli.parser:_is_overload_stub` | `(node: ast.FunctionDef / ast.AsyncFunctionDef)` | `bool` | ~1 site(s) · node:ast.FunctionDef |
| `flowcli.parser:_literal_arg` | `(value: ast.expr)` | `tuple[str, Any] / None` | ~1 site(s) · value:ast.expr |
| `flowcli.parser:_param_list` | `(args: ast.arguments)` | `list[dict[str, str / None]]` | ~1 site(s) · args:ast.arguments |
| `flowcli.parser:_param_list.entry` | `(arg: ast.arg, default: ast.expr / None, prefix: str='')` | `dict[str, str / None]` | ~4 site(s) · arg:ast.arg, default=None, prefix=''/'*' |
| `flowcli.parser:_safe_unparse` | `(node: ast.AST, limit: int=80)` | `str` | ~22 site(s) · node:ast.AST, limit=80/60 |
| `flowcli.parser:_short` | `(text: str)` | `str` | ~9 site(s) · text=f'{_safe_unparse(stmt.target)}/f'with {items}' |
| `flowcli.parser:parse_module` | `(module_name: str, file: Path)` | `ModuleInfo / ParseFailure` | ~1 site(s) · module_name:str, file:Path |
| `flowcli.parser:parse_source` | `(module_name: str, file: str, source: str, is_package: bool=False)` | `ModuleInfo / ParseFailure` | ~1 site(s) · module_name:str, file:str, source:fh.read |
| `flowcli.render_html:_class_payload` | `(class_graph: ClassGraph / None)` | `dict[str, Any]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.render_html:_module_of` | `(node_id: str)` | `str` | ~2 site(s) · node_id:str |
| `flowcli.render_html:_node_entry` | `(n: Node, module_index: int)` | `dict[str, Any]` | ~1 site(s) · n:Node, module_index:int |
| `flowcli.render_html:build_payload` | `(graph: Graph, meta: dict[str, Any], runtime: dict[str, Any] / None=None)` | `dict[str, Any]` | ~1 site(s) · graph:Graph, meta:dict, runtime=None |
| `flowcli.render_html:render_html` | `(graph: Graph, meta: dict[str, Any], out: Path, runtime: dict[str, Any] / None=None, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, out:Path |
| `flowcli.report:_by_out_degree` | `(graph: Graph)` | `list[Node]` | ~2 site(s) · graph:Graph |
| `flowcli.report:_cell` | `(text: str)` | `str` | ~7 site(s) · text=f"{node.dynamic.get('ncalls', /f'~{sites} site(s) · {detail}' |
| `flowcli.report:_classes_section` | `(class_graph: ClassGraph / None)` | `list[str]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.report:_loc` | `(node: Node, root: str)` | `str` | ~1 site(s) · node:Node, root:str |
| `flowcli.report:_most_called_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:_params_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.report:_returns_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.report:_runtime_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.report:_signatures_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:_unreachable_section` | `(graph: Graph, meta: dict[str, Any])` | `list[str]` | ~1 site(s) · graph:Graph, meta:dict |
| `flowcli.report:_unresolved_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.report:print_summary` | `(graph: Graph, meta: dict[str, Any])` | `None` | ~1 site(s) · graph:Graph, meta:_build_meta |
| `flowcli.report:write_json` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, out:Path |
| `flowcli.report:write_markdown` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict, out:Path |
| `flowcli.resolver:ProjectIndex.__init__` | `(self, modules: dict[str, ModuleInfo])` | `None` | ~1 site(s) · modules:dict[str, ModuleInfo] |
| `flowcli.resolver:ProjectIndex.module_for` | `(self, dotted: str)` | `str / None` | ~3 site(s) · dotted:str |
| `flowcli.resolver:_constructor` | `(index: ProjectIndex, module: str, class_qualname: str, expr: str)` | `Outcome` | ~5 site(s) · index:ProjectIndex, module:index.module_for, class_qualname:str |
| `flowcli.resolver:_external` | `(dotted: str)` | `Outcome` | ~2 site(s) · dotted=f'builtins.{name}' |
| `flowcli.resolver:_find_attr_type` | `(index: ProjectIndex, module: str, class_qualname: str, attr: str, _seen: set[tuple[str, str]] / None=None)` | `tuple[str, tuple[str, ...]] / None` | ~2 site(s) · index:ProjectIndex, module:str, class_qualname:str |
| `flowcli.resolver:_find_class_by_dotted` | `(index: ProjectIndex, dotted: str, _seen: set[str] / None=None)` | `tuple[str, str] / None` | ~3 site(s) · index:ProjectIndex, dotted:str, _seen=None |
| `flowcli.resolver:_internal` | `(target_id: str)` | `Outcome` | ~11 site(s) · target_id:resolve_method |
| `flowcli.resolver:_resolve_absolute` | `(index: ProjectIndex, dotted: str, expr: str, _seen: set[str] / None=None)` | `Outcome` | ~4 site(s) · index:ProjectIndex, dotted=f'{star_mod}.{rem}', expr:str |
| `flowcli.resolver:_resolve_class_ref` | `(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...])` | `tuple[str, str] / None` | ~12 site(s) · index:ProjectIndex, mod:ModuleInfo, parts:caller.local_types.get |
| `flowcli.resolver:_resolve_dotted` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_enclosing_scope` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, name: str, hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_local_class_dotted` | `(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, parts:tuple[str, ...] |
| `flowcli.resolver:_resolve_name` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_name_imported` | `(index: ProjectIndex, mod: ModuleInfo, name: str, hint: str)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, name:str |
| `flowcli.resolver:_resolve_one` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~3 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_resolve_self_attr_chain` | `(index: ProjectIndex, mod: ModuleInfo, class_qualname: str, call: RawCall)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, class_qualname:str |
| `flowcli.resolver:_resolve_typed_local` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.resolver:_unresolved` | `(expr: str, reason: str)` | `Outcome` | ~17 site(s) · expr:str, reason='instance-attr'/'not-found-in-hierarchy' |
| `flowcli.resolver:resolve_all` | `(index: ProjectIndex)` | `list[ResolvedCall]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.resolver:resolve_method` | `(index: ProjectIndex, module: str, class_qualname: str, method: str, skip_self: bool=False, _seen: set[tuple[str, str]] / None=None)` | `str / None` | ~8 site(s) · index:ProjectIndex, module:index.module_for, class_qualname:str |
| `flowcli.simulate:_Site.__init__` | `(self, caller: str, target: str, lineno: int, pairs: list[tuple[str, tuple[str, Any]]])` | `None` | ~1 site(s) · caller:str, target:str, lineno:int |
| `flowcli.simulate:_absorb` | `(slot: dict[str, Any], types: list[str], value: str / None, source: str)` | `bool` | ~3 site(s) · slot:dict[str, Any], types=[str(p['ann'])]/[], value=None |
| `flowcli.simulate:_bind_site` | `(rc: ResolvedCall, fns: dict[str, FunctionInfo])` | `_Site / None` | ~1 site(s) · rc:ResolvedCall, fns:_function_index |
| `flowcli.simulate:_eval_atom` | `(index: ProjectIndex, fns: dict[str, FunctionInfo], records: dict[str, dict[str, Any]], signatures: dict[str, dict[str, Any]], caller_id: str, atom: tuple[str, Any])` | `tuple[list[str], str / None]` | ~1 site(s) · index:ProjectIndex, fns:_function_index, records:dict |
| `flowcli.simulate:_function_index` | `(index: ProjectIndex)` | `dict[str, FunctionInfo]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.simulate:_param_names` | `(fn: FunctionInfo)` | `list[str]` | ~2 site(s) · fn:FunctionInfo |
| `flowcli.simulate:_returns_of_call` | `(index: ProjectIndex, mod: ModuleInfo, caller: FunctionInfo, signatures: dict[str, dict[str, Any]], parts: tuple[str, ...])` | `list[str]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, caller:FunctionInfo |
| `flowcli.simulate:_seed_entry` | `(rec: dict[str, Any] / None, fn: FunctionInfo / None)` | `None` | ~1 site(s) · rec:dict[str, Any] / None, fn:FunctionInfo / None |
| `flowcli.simulate:_simulated_events` | `(sites: list[_Site], entry_ids: list[str])` | `list[list[str]]` | ~1 site(s) · sites:list[_Site], entry_ids:list[str] |
| `flowcli.simulate:_walk` | `(node: str, out_edges: dict[str, list[tuple[int, str]]], stack: set[str], events: list[list[str]])` | `None` | ~2 site(s) · node:str, out_edges:dict, stack:set |
| `flowcli.simulate:module_entry_candidates` | `(index: ProjectIndex)` | `list[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.simulate:simulate` | `(index: ProjectIndex, resolved: list[ResolvedCall], signatures: dict[str, dict[str, Any]], entry_ids: list[str] / None=None)` | `tuple[dict[str, dict[str, Any]], list[list[str]]]` | ~1 site(s) · index:ProjectIndex, resolved:list, signatures:dict[str, dict[str, Any]] |
| `flowcli.tracer:_param_names` | `(code: CodeType)` | `list[tuple[str, str]]` | ~1 site(s) · code:CodeType |
| `flowcli.tracer:_safe_repr` | `(value: Any)` | `str` | ~2 site(s) · value:Any |
| `flowcli.tracer:_type_name` | `(value: Any)` | `str` | ~2 site(s) · value:Any |
| `flowcli.tracer:capture` | `(root: Path, samples: bool=True)` | `Iterator[RuntimeCapture]` | ~1 site(s) · root:Path, samples=True |
| `flowcli.tracer:capture.module_of` | `(filename: str)` | `str / None` | ~1 site(s) · filename:str |
| `flowcli.tracer:capture.node_for` | `(code: CodeType)` | `str / None` | ~2 site(s) · code:CodeType |
| `flowcli.tracer:capture.on_call` | `(frame: FrameType)` | `None` | ~1 site(s) · frame:FrameType |
| `flowcli.tracer:capture.on_return` | `(frame: FrameType, arg: Any)` | `None` | ~1 site(s) · frame:FrameType, arg:Any |
| `flowcli.tracer:capture.profiler` | `(frame: FrameType, event: str, arg: Any)` | `None` | ~0 site(s) · frame:FrameType, event:str, arg:Any |

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
| `flowcli.parser:_Collector` | class | ast.NodeVisitor | info, _stack: list[tuple[str, str]], _sink: FunctionInfo / None, visit_Yield, visit_YieldFrom | _sink → FunctionInfo |
| `flowcli.resolver:ProjectIndex` | class | — | modules | — |
| `flowcli.resolver:ResolvedCall` | dataclass | — | caller: str, lineno: int, status: str, target: str, reason: str, call: RawCall / None | call → RawCall |
| `flowcli.simulate:_Site` | class | — | __slots__, caller, target, lineno, pairs | — |
| `flowcli.tracer:RuntimeCapture` | dataclass | — | functions: dict[str, dict[str, Any]], events: list[list[str]], calls_total: int, events_truncated: bool | — |

## Unresolved calls

- **external**: 395
- **instance-attr**: 325
- **opaque**: 93
- **not-found-in-hierarchy**: 41
- **unknown-name**: 1

| Callee expression | Occurrences |
|---|---:|
| `builtins.len` | 71 |
| `builtins.isinstance` | 58 |
| `builtins.sorted` | 38 |
| `dataclasses.field` | 30 |
| `builtins.print` | 23 |
| `p.add_argument` | 18 |
| `builtins.str` | 18 |
| `builtins.set` | 17 |
| `'.'.join` | 17 |
| `builtins.list` | 16 |
| `meta.get` | 16 |
| `pathlib.Path` | 14 |
| `', '.join` | 14 |
| `dataclasses.dataclass` | 13 |
| `out.append` | 12 |
