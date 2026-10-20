# flowcli report

**28** modules · **171** nodes · **262** edges · **858** unresolved calls · entry `flowcli/ (28 modules)` (0 unreachable)

## Call graph

| Node | Kind | File:Line | Out | In | Depth |
|---|---|---|---:|---:|---:|
| `flowcli.pipeline:map_project` | function | pipeline.py:64 | 16 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_absolute` | function | analysis\resolver.py:234 | 8 | 3 | 0 |
| `flowcli.analysis.parser:_Collector._handle_function` | method | analysis\parser.py:136 | 8 | 2 | 0 |
| `flowcli.analysis.entrypoints:detect` | function | analysis\entrypoints.py:22 | 7 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_name` | function | analysis\resolver.py:120 | 7 | 1 | 0 |
| `flowcli.analysis.simulate:simulate` | function | analysis\simulate.py:47 | 7 | 1 | 0 |
| `flowcli.output.report:write_markdown` | function | output\report.py:45 | 7 | 1 | 0 |
| `flowcli.analysis.resolver:resolve_call` | function | analysis\resolver.py:65 | 6 | 2 | 0 |
| `flowcli.analysis.resolver:_resolve_name_imported` | function | analysis\resolver.py:159 | 6 | 1 | 0 |
| `flowcli.analysis.flow:_flow_of_stmt` | function | analysis\flow.py:47 | 5 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_self_attr_chain` | function | analysis\resolver.py:101 | 5 | 1 | 0 |
| `flowcli.cli:_cmd_map` | function | cli.py:106 | 5 | 1 | 0 |
| `flowcli.cli:_cmd_run` | function | cli.py:143 | 5 | 1 | 0 |
| `flowcli.cli:main` | function | cli.py:31 | 4 | 2 | 0 |
| `flowcli.analysis.classes:_make_node` | function | analysis\classes.py:70 | 4 | 1 | 0 |
| `flowcli.analysis.classes:build_class_graph` | function | analysis\classes.py:52 | 4 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_dotted` | function | analysis\resolver.py:175 | 4 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_local_class_dotted` | function | analysis\resolver.py:213 | 4 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_typed_local` | function | analysis\resolver.py:196 | 4 | 1 | 0 |
| `flowcli.graph.build:_make_nodes` | function | graph\build.py:22 | 4 | 1 | 0 |
| `flowcli.graph.entry:parse_entry_spec` | function | graph\entry.py:51 | 4 | 1 | 0 |
| `flowcli.runtime.tracer:capture.on_call` | function | runtime\tracer.py:114 | 4 | 1 | 0 |
| `flowcli.analysis.parser:_Collector.visit_Assign` | method | analysis\parser.py:277 | 4 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_ClassDef` | method | analysis\parser.py:178 | 4 | 0 | 0 |
| `flowcli.analysis.index:ProjectIndex.resolve_method` | method | analysis\index.py:49 | 3 | 8 | 0 |
| `flowcli.analysis.resolver:_constructor` | function | analysis\resolver.py:228 | 3 | 5 | 0 |
| `flowcli.analysis.parser:_Collector._visit_decorators` | method | analysis\parser.py:114 | 3 | 2 | 0 |
| `flowcli.analysis.discovery:discover` | function | analysis\discovery.py:104 | 3 | 1 | 0 |
| `flowcli.analysis.flow:_flow_of_try` | function | analysis\flow.py:106 | 3 | 1 | 0 |
| `flowcli.analysis.infer:_resolve_return_call` | function | analysis\infer.py:106 | 3 | 1 | 0 |
| `flowcli.analysis.resolver:_resolve_enclosing_scope` | function | analysis\resolver.py:140 | 3 | 1 | 0 |
| `flowcli.output.report:_signatures_section` | function | output\report.py:119 | 3 | 1 | 0 |
| `flowcli.pipeline:write_outputs` | function | pipeline.py:132 | 3 | 1 | 0 |
| `flowcli.analysis.parser:_Collector.visit_AnnAssign` | method | analysis\parser.py:297 | 3 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_Call` | method | analysis\parser.py:338 | 3 | 0 | 0 |
| `flowcli.analysis.parser:_annotation_parts` | function | analysis\parser.py:476 | 2 | 3 | 0 |
| `flowcli.analysis.index:ProjectIndex._find_class_by_dotted` | method | analysis\index.py:108 | 2 | 2 | 0 |
| `flowcli.analysis.index:ProjectIndex.attr_type` | method | analysis\index.py:84 | 2 | 2 | 0 |
| `flowcli.analysis.parser:_Collector._classify_callable_expr` | method | analysis\parser.py:83 | 2 | 2 | 0 |
| `flowcli.analysis.parser:_Collector._record_self_attr` | method | analysis\parser.py:244 | 2 | 2 | 0 |
| `flowcli.analysis.classes:_add_inheritance` | function | analysis\classes.py:121 | 2 | 1 | 0 |
| `flowcli.analysis.discovery:_namespace_prefix` | function | analysis\discovery.py:60 | 2 | 1 | 0 |
| `flowcli.analysis.entrypoints:_exported` | function | analysis\entrypoints.py:77 | 2 | 1 | 0 |
| `flowcli.analysis.infer:_resolve_return_expr` | function | analysis\infer.py:90 | 2 | 1 | 0 |
| `flowcli.analysis.infer:infer_signatures` | function | analysis\infer.py:25 | 2 | 1 | 0 |
| `flowcli.analysis.parser:_Collector._classify_attribute` | method | analysis\parser.py:92 | 2 | 1 | 0 |
| `flowcli.analysis.parser:_classify_arg_expr` | function | analysis\parser.py:419 | 2 | 1 | 0 |
| `flowcli.analysis.resolver:resolve_all` | function | analysis\resolver.py:30 | 2 | 1 | 0 |
| `flowcli.analysis.simulate:_bind_site` | function | analysis\simulate.py:103 | 2 | 1 | 0 |
| `flowcli.analysis.simulate:_eval_atom` | function | analysis\simulate.py:160 | 2 | 1 | 0 |
| `flowcli.analysis.simulate:_returns_of_call` | function | analysis\simulate.py:200 | 2 | 1 | 0 |
| `flowcli.graph.build:apply_simulation` | function | graph\build.py:129 | 2 | 1 | 0 |
| `flowcli.graph.build:build_graph` | function | graph\build.py:15 | 2 | 1 | 0 |
| `flowcli.output.html:build_payload` | function | output\html.py:61 | 2 | 1 | 0 |
| `flowcli.output.html:render_html` | function | output\html.py:134 | 2 | 1 | 0 |
| `flowcli.output.report:_classes_section` | function | output\report.py:71 | 2 | 1 | 0 |
| `flowcli.runtime.runner:execute` | function | runtime\runner.py:47 | 2 | 1 | 0 |
| `flowcli.runtime.tracer:capture.node_for` | function | runtime\tracer.py:99 | 2 | 1 | 0 |
| `flowcli.runtime.tracer:capture.on_return` | function | runtime\tracer.py:147 | 2 | 1 | 0 |
| `flowcli.runtime.tracer:capture.profiler` | function | runtime\tracer.py:162 | 2 | 0 | 0 |
| `flowcli.analysis.index:ProjectIndex.find_class` | method | analysis\index.py:28 | 1 | 9 | 0 |
| `flowcli.analysis.flow:_flow_of_body` | function | analysis\flow.py:36 | 1 | 3 | 0 |
| `flowcli.analysis.classes:_ref_id` | function | analysis\classes.py:102 | 1 | 2 | 0 |
| `flowcli.analysis.discovery:find_package_prefix` | function | analysis\discovery.py:29 | 1 | 2 | 0 |
| `flowcli.analysis.index:ProjectIndex.type_display` | method | analysis\index.py:44 | 1 | 2 | 0 |
| `flowcli.analysis.parser:_Collector._record_call` | method | analysis\parser.py:80 | 1 | 2 | 0 |
| `flowcli.analysis.resolver:resolve_parts` | function | analysis\resolver.py:51 | 1 | 2 | 0 |
| `flowcli.analysis.simulate:_walk` | function | analysis\simulate.py:237 | 1 | 2 | 0 |
| `flowcli.graph.build:_annotate_flow` | function | graph\build.py:80 | 1 | 2 | 0 |
| `flowcli.graph.build:_annotate_ret_types` | function | graph\build.py:99 | 1 | 2 | 0 |
| `flowcli.analysis.entrypoints:_script_to_node` | function | analysis\entrypoints.py:110 | 1 | 1 | 0 |
| `flowcli.analysis.flow:flow_of` | function | analysis\flow.py:26 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_classify_args` | function | analysis\parser.py:393 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_classify_return_expr` | function | analysis\parser.py:437 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_is_overload_stub` | function | analysis\parser.py:466 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_literal_arg` | function | analysis\parser.py:403 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_param_list` | function | analysis\parser.py:356 | 1 | 1 | 0 |
| `flowcli.analysis.parser:_param_list.entry` | function | analysis\parser.py:359 | 1 | 1 | 0 |
| `flowcli.analysis.parser:parse_module` | function | analysis\parser.py:24 | 1 | 1 | 0 |
| `flowcli.analysis.parser:parse_source` | function | analysis\parser.py:33 | 1 | 1 | 0 |
| `flowcli.analysis.simulate:_function_index` | function | analysis\simulate.py:95 | 1 | 1 | 0 |
| `flowcli.analysis.simulate:_seed_entry` | function | analysis\simulate.py:132 | 1 | 1 | 0 |
| `flowcli.analysis.simulate:_simulated_events` | function | analysis\simulate.py:216 | 1 | 1 | 0 |
| `flowcli.analysis.simulate:module_entry_candidates` | function | analysis\simulate.py:249 | 1 | 1 | 0 |
| `flowcli.cli:_entry_specs` | function | cli.py:101 | 1 | 1 | 0 |
| `flowcli.cli:_resolve_entry` | function | cli.py:90 | 1 | 1 | 0 |
| `flowcli.graph.entry:_find_subtree` | function | graph\entry.py:80 | 1 | 1 | 0 |
| `flowcli.graph.entry:parse_entry_specs` | function | graph\entry.py:13 | 1 | 1 | 0 |
| `flowcli.output.html:_module_of` | function | output\html.py:19 | 1 | 1 | 0 |
| `flowcli.output.report:_params_str` | function | output\report.py:145 | 1 | 1 | 0 |
| `flowcli.output.report:_returns_str` | function | output\report.py:158 | 1 | 1 | 0 |
| `flowcli.output.report:_runtime_str` | function | output\report.py:167 | 1 | 1 | 0 |
| `flowcli.output.report:print_summary` | function | output\report.py:184 | 1 | 1 | 0 |
| `flowcli.pipeline:_parse_all` | function | pipeline.py:143 | 1 | 1 | 0 |
| `flowcli.pipeline:_read_runtime` | function | pipeline.py:156 | 1 | 1 | 0 |
| `flowcli.runtime.tracer:capture` | function | runtime\tracer.py:74 | 1 | 1 | 0 |
| `flowcli.runtime.tracer:capture.module_of` | function | runtime\tracer.py:87 | 1 | 1 | 0 |
| `flowcli.__main__:<module>` | module | __main__.py:1 | 1 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_AsyncFunctionDef` | method | analysis\parser.py:133 | 1 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_FunctionDef` | method | analysis\parser.py:130 | 1 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_If` | method | analysis\parser.py:315 | 1 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_ImportFrom` | method | analysis\parser.py:216 | 1 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_Return` | method | analysis\parser.py:322 | 1 | 0 | 0 |
| `flowcli.analysis.model:node_id` | function | analysis\model.py:85 | 0 | 19 | 0 |
| `flowcli.analysis.astutil:safe_unparse` | function | analysis\astutil.py:8 | 0 | 11 | 0 |
| `flowcli.analysis.resolver:_internal` | function | analysis\resolver.py:89 | 0 | 9 | 0 |
| `flowcli.analysis.resolver:_unresolved` | function | analysis\resolver.py:97 | 0 | 9 | 0 |
| `flowcli.analysis.astutil:dotted_parts` | function | analysis\astutil.py:15 | 0 | 6 | 0 |
| `flowcli.analysis.model:split_node_id` | function | analysis\model.py:89 | 0 | 4 | 0 |
| `flowcli.output.report:_cell` | function | output\report.py:141 | 0 | 4 | 0 |
| `flowcli.analysis.index:ProjectIndex.module_for` | method | analysis\index.py:19 | 0 | 3 | 0 |
| `flowcli.analysis.parser:_Collector._nearest_class` | method | analysis\parser.py:62 | 0 | 3 | 0 |
| `flowcli.analysis.discovery:derive_module_name` | function | analysis\discovery.py:90 | 0 | 2 | 0 |
| `flowcli.analysis.flow:_short` | function | analysis\flow.py:31 | 0 | 2 | 0 |
| `flowcli.analysis.parser:_Collector._qual` | method | analysis\parser.py:59 | 0 | 2 | 0 |
| `flowcli.analysis.parser:_Collector._record_field` | method | analysis\parser.py:257 | 0 | 2 | 0 |
| `flowcli.analysis.resolver:_external` | function | analysis\resolver.py:93 | 0 | 2 | 0 |
| `flowcli.analysis.simulate:_absorb` | function | analysis\simulate.py:146 | 0 | 2 | 0 |
| `flowcli.analysis.simulate:_param_names` | function | analysis\simulate.py:29 | 0 | 2 | 0 |
| `flowcli.cli:_fail` | function | cli.py:173 | 0 | 2 | 0 |
| `flowcli.graph.entry:split_entry_spec` | function | graph\entry.py:35 | 0 | 2 | 0 |
| `flowcli.output.report:_by_out_degree` | function | output\report.py:41 | 0 | 2 | 0 |
| `flowcli.pipeline:MapError.__init__` | method | pipeline.py:37 | 0 | 2 | 0 |
| `flowcli.runtime.tracer:_safe_repr` | function | runtime\tracer.py:53 | 0 | 2 | 0 |
| `flowcli.runtime.tracer:_type_name` | function | runtime\tracer.py:46 | 0 | 2 | 0 |
| `flowcli.analysis.classes:_add_composition` | function | analysis\classes.py:128 | 0 | 1 | 0 |
| `flowcli.analysis.classes:_stereotype` | function | analysis\classes.py:106 | 0 | 1 | 0 |
| `flowcli.analysis.classes:scope_class_graph` | function | analysis\classes.py:141 | 0 | 1 | 0 |
| `flowcli.analysis.discovery:_excluded` | function | analysis\discovery.py:100 | 0 | 1 | 0 |
| `flowcli.analysis.discovery:_holds_modules` | function | analysis\discovery.py:52 | 0 | 1 | 0 |
| `flowcli.analysis.discovery:_is_project_root` | function | analysis\discovery.py:48 | 0 | 1 | 0 |
| `flowcli.analysis.entrypoints:_console_scripts` | function | analysis\entrypoints.py:93 | 0 | 1 | 0 |
| `flowcli.analysis.entrypoints:_defines_api` | function | analysis\entrypoints.py:66 | 0 | 1 | 0 |
| `flowcli.analysis.entrypoints:_is_private_path` | function | analysis\entrypoints.py:71 | 0 | 1 | 0 |
| `flowcli.analysis.entrypoints:detect.add` | function | analysis\entrypoints.py:26 | 0 | 1 | 0 |
| `flowcli.analysis.flow:_end` | function | analysis\flow.py:125 | 0 | 1 | 0 |
| `flowcli.analysis.index:ProjectIndex.__init__` | method | analysis\index.py:16 | 0 | 1 | 0 |
| `flowcli.analysis.parser:_Collector.__init__` | method | analysis\parser.py:52 | 0 | 1 | 0 |
| `flowcli.analysis.parser:_Collector._ensure_module_fn` | method | analysis\parser.py:68 | 0 | 1 | 0 |
| `flowcli.analysis.parser:_Collector._resolve_from_base` | method | analysis\parser.py:228 | 0 | 1 | 0 |
| `flowcli.analysis.parser:_is_main_guard` | function | analysis\parser.py:346 | 0 | 1 | 0 |
| `flowcli.analysis.simulate:_Site.__init__` | method | analysis\simulate.py:40 | 0 | 1 | 0 |
| `flowcli.cli:_add_map_parser` | function | cli.py:53 | 0 | 1 | 0 |
| `flowcli.cli:_add_run_parser` | function | cli.py:76 | 0 | 1 | 0 |
| `flowcli.graph.build:_apply_edges` | function | graph\build.py:54 | 0 | 1 | 0 |
| `flowcli.graph.build:apply_runtime` | function | graph\build.py:118 | 0 | 1 | 0 |
| `flowcli.graph.entry:_find_module` | function | graph\entry.py:103 | 0 | 1 | 0 |
| `flowcli.graph.scope:compute_depths` | function | graph\scope.py:11 | 0 | 1 | 0 |
| `flowcli.graph.scope:prune_unreachable` | function | graph\scope.py:39 | 0 | 1 | 0 |
| `flowcli.output.html:_class_payload` | function | output\html.py:101 | 0 | 1 | 0 |
| `flowcli.output.html:_node_entry` | function | output\html.py:24 | 0 | 1 | 0 |
| `flowcli.output.report:_loc` | function | output\report.py:31 | 0 | 1 | 0 |
| `flowcli.output.report:_most_called_section` | function | output\report.py:91 | 0 | 1 | 0 |
| `flowcli.output.report:_unreachable_section` | function | output\report.py:104 | 0 | 1 | 0 |
| `flowcli.output.report:_unresolved_section` | function | output\report.py:129 | 0 | 1 | 0 |
| `flowcli.output.report:write_json` | function | output\report.py:17 | 0 | 1 | 0 |
| `flowcli.runtime.runner:Program.parse` | method | runtime\runner.py:24 | 0 | 1 | 0 |
| `flowcli.runtime.runner:_exit_code_of` | function | runtime\runner.py:94 | 0 | 1 | 0 |
| `flowcli.runtime.runner:runtime_payload` | function | runtime\runner.py:73 | 0 | 1 | 0 |
| `flowcli.runtime.tracer:_param_names` | function | runtime\tracer.py:60 | 0 | 1 | 0 |
| `flowcli.analysis.classes:<module>` | module | analysis\classes.py:1 | 0 | 0 | 0 |
| `flowcli.analysis.model:<module>` | module | analysis\model.py:1 | 0 | 0 | 0 |
| `flowcli.analysis.parser:_Collector._mark_generator` | method | analysis\parser.py:328 | 0 | 0 | 0 |
| `flowcli.analysis.parser:_Collector.visit_Import` | method | analysis\parser.py:208 | 0 | 0 | 0 |
| `flowcli.analysis.resolver:<module>` | module | analysis\resolver.py:1 | 0 | 0 | 0 |
| `flowcli.graph.model:<module>` | module | graph\model.py:1 | 0 | 0 | 0 |
| `flowcli.pipeline:<module>` | module | pipeline.py:1 | 0 | 0 | 0 |
| `flowcli.runtime.runner:<module>` | module | runtime\runner.py:1 | 0 | 0 | 0 |
| `flowcli.runtime.runner:Program.argv` | method | runtime\runner.py:38 | 0 | 0 | 0 |
| `flowcli.runtime.runner:Program.home` | method | runtime\runner.py:42 | 0 | 0 | 0 |
| `flowcli.runtime.tracer:<module>` | module | runtime\tracer.py:1 | 0 | 0 | 0 |

## Top 10 most-called

| Node | In | Called by |
|---|---:|---|
| `flowcli.analysis.model:node_id` | 19 | `flowcli.analysis.classes:_make_node`, `flowcli.analysis.classes:_ref_id`, `flowcli.analysis.classes:build_class_graph`, `flowcli.analysis.entrypoints:_exported`, `flowcli.analysis.entrypoints:_script_to_node`, … +14 |
| `flowcli.analysis.astutil:safe_unparse` | 11 | `flowcli.analysis.flow:_flow_of_stmt`, `flowcli.analysis.flow:_flow_of_try`, `flowcli.analysis.parser:_Collector._classify_attribute`, `flowcli.analysis.parser:_Collector._classify_callable_expr`, `flowcli.analysis.parser:_Collector._handle_function`, … +6 |
| `flowcli.analysis.index:ProjectIndex.find_class` | 9 | `flowcli.analysis.classes:_add_inheritance`, `flowcli.analysis.classes:_make_node`, `flowcli.analysis.index:ProjectIndex.attr_type`, `flowcli.analysis.index:ProjectIndex.resolve_method`, `flowcli.analysis.index:ProjectIndex.type_display`, … +4 |
| `flowcli.analysis.resolver:_internal` | 9 | `flowcli.analysis.resolver:_constructor`, `flowcli.analysis.resolver:_resolve_absolute`, `flowcli.analysis.resolver:_resolve_enclosing_scope`, `flowcli.analysis.resolver:_resolve_local_class_dotted`, `flowcli.analysis.resolver:_resolve_name`, … +4 |
| `flowcli.analysis.resolver:_unresolved` | 9 | `flowcli.analysis.resolver:_constructor`, `flowcli.analysis.resolver:_resolve_absolute`, `flowcli.analysis.resolver:_resolve_dotted`, `flowcli.analysis.resolver:_resolve_local_class_dotted`, `flowcli.analysis.resolver:_resolve_name`, … +4 |
| `flowcli.analysis.index:ProjectIndex.resolve_method` | 8 | `flowcli.analysis.index:ProjectIndex.resolve_method`, `flowcli.analysis.resolver:_constructor`, `flowcli.analysis.resolver:_resolve_absolute`, `flowcli.analysis.resolver:_resolve_local_class_dotted`, `flowcli.analysis.resolver:_resolve_name`, … +3 |
| `flowcli.analysis.astutil:dotted_parts` | 6 | `flowcli.analysis.parser:_Collector.visit_Assign`, `flowcli.analysis.parser:_Collector.visit_ClassDef`, `flowcli.analysis.parser:_annotation_parts`, `flowcli.analysis.parser:_classify_arg_expr`, `flowcli.analysis.parser:_classify_return_expr`, … +1 |
| `flowcli.analysis.resolver:_constructor` | 5 | `flowcli.analysis.resolver:_resolve_absolute`, `flowcli.analysis.resolver:_resolve_enclosing_scope`, `flowcli.analysis.resolver:_resolve_local_class_dotted`, `flowcli.analysis.resolver:_resolve_name`, `flowcli.analysis.resolver:_resolve_name_imported` |
| `flowcli.analysis.model:split_node_id` | 4 | `flowcli.analysis.infer:_resolve_return_call`, `flowcli.output.html:_module_of`, `flowcli.output.report:_classes_section`, `flowcli.pipeline:map_project` |
| `flowcli.output.report:_cell` | 4 | `flowcli.output.report:_classes_section`, `flowcli.output.report:_params_str`, `flowcli.output.report:_returns_str`, `flowcli.output.report:_runtime_str` |

## Unreachable from `flowcli/ (28 modules)`

_0 function(s) outside this call graph were pruned from the report (rerun with --keep-unreachable to include them)._

## Signatures

| Node | Signature | Returns | Data flow |
|---|---|---|---|
| `flowcli.analysis.astutil:dotted_parts` | `(node: ast.expr)` | `tuple[str, ...]` | ~8 site(s) · node:ast.expr |
| `flowcli.analysis.astutil:safe_unparse` | `(node: ast.AST, limit: int=80)` | `str` | ~22 site(s) · node:ast.AST, limit=80/40 |
| `flowcli.analysis.classes:_add_composition` | `(node: ClassNode, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · node:ClassNode, nid:str, graph:ClassGraph |
| `flowcli.analysis.classes:_add_inheritance` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo, nid: str, graph: ClassGraph)` | `None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, ci:ClassInfo |
| `flowcli.analysis.classes:_make_node` | `(index: ProjectIndex, mod: ModuleInfo, ci: ClassInfo)` | `ClassNode` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, ci:ClassInfo |
| `flowcli.analysis.classes:_ref_id` | `(ref: ClassRef / None)` | `str / None` | ~3 site(s) · ref:ClassRef / None |
| `flowcli.analysis.classes:_stereotype` | `(ci: ClassInfo)` | `str` | ~1 site(s) · ci:ClassInfo |
| `flowcli.analysis.classes:build_class_graph` | `(index: ProjectIndex)` | `ClassGraph` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.classes:scope_class_graph` | `(graph: ClassGraph, keep_modules: set[str])` | `ClassGraph` | ~1 site(s) · graph:ClassGraph, keep_modules={split_node_id(nid)[0] for nid |
| `flowcli.analysis.discovery:_excluded` | `(rel_posix: str, name: str, excludes: Sequence[str])` | `bool` | ~2 site(s) · rel_posix:str, name:str, excludes:Sequence |
| `flowcli.analysis.discovery:_holds_modules` | `(path: Path)` | `bool` | ~1 site(s) · path:Path |
| `flowcli.analysis.discovery:_is_project_root` | `(path: Path)` | `bool` | ~3 site(s) · path:Path |
| `flowcli.analysis.discovery:_namespace_prefix` | `(start: Path)` | `tuple[Path, str]` | ~1 site(s) · start:Path |
| `flowcli.analysis.discovery:derive_module_name` | `(file: Path, anchor: Path)` | `str` | ~3 site(s) · file:Path, anchor:Path |
| `flowcli.analysis.discovery:discover` | `(root: Path, excludes: Sequence[str]=())` | `list[tuple[str, Path]]` | ~1 site(s) · root:Path, excludes=() |
| `flowcli.analysis.discovery:find_package_prefix` | `(root: Path)` | `tuple[Path, str]` | ~3 site(s) · root:Path |
| `flowcli.analysis.entrypoints:_console_scripts` | `(root: Path / None)` | `list[str]` | ~1 site(s) · root:Path |
| `flowcli.analysis.entrypoints:_defines_api` | `(mod: ModuleInfo)` | `bool` | ~1 site(s) · mod:ModuleInfo |
| `flowcli.analysis.entrypoints:_exported` | `(index: ProjectIndex)` | `set[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.entrypoints:_is_private_path` | `(mod_name: str, qual: str)` | `bool` | ~1 site(s) · mod_name:str, qual:str |
| `flowcli.analysis.entrypoints:_script_to_node` | `(spec: str, index: ProjectIndex)` | `str / None` | ~1 site(s) · spec:str, index:ProjectIndex |
| `flowcli.analysis.entrypoints:detect` | `(index: ProjectIndex, called: set[str], root: Path / None=None)` | `list[dict[str, Any]]` | ~1 site(s) · index:ProjectIndex, called={rc.target for rc in resolved , root=None |
| `flowcli.analysis.entrypoints:detect.add` | `(nid: str, kind: str, score: int, why: str)` | `None` | ~7 site(s) · nid:node_id, kind='script'/'main', score=100/95 |
| `flowcli.analysis.flow:_end` | `(stmt: ast.stmt)` | `int` | ~2 site(s) · stmt:ast.stmt |
| `flowcli.analysis.flow:_flow_of_body` | `(body: list[ast.stmt], budget: list[int])` | `list[dict]` | ~10 site(s) · body:list, budget=[MAX_FLOW_NODES] |
| `flowcli.analysis.flow:_flow_of_stmt` | `(stmt: ast.stmt, budget: list[int])` | `dict` | ~1 site(s) · stmt:ast.stmt, budget:list |
| `flowcli.analysis.flow:_flow_of_try` | `(stmt: ast.Try / ast.TryStar, budget: list[int])` | `dict` | ~1 site(s) · stmt:ast.Try / ast.TryStar, budget:list |
| `flowcli.analysis.flow:_short` | `(text: str)` | `str` | ~9 site(s) · text=f'{safe_unparse(stmt.target)} /f'with {items}' |
| `flowcli.analysis.flow:flow_of` | `(body: list[ast.stmt])` | `list[dict]` | ~1 site(s) · body:list[ast.stmt] |
| `flowcli.analysis.index:ProjectIndex.__init__` | `(self, modules: dict[str, ModuleInfo])` | `None` | ~1 site(s) · modules:dict[str, ModuleInfo] |
| `flowcli.analysis.index:ProjectIndex._find_class_by_dotted` | `(self, dotted: str, _seen: set[str] / None=None)` | `ClassRef / None` | ~3 site(s) · dotted:str, _seen=None |
| `flowcli.analysis.index:ProjectIndex.attr_type` | `(self, module: str, class_qualname: str, attr: str, _seen: set[ClassRef] / None=None)` | `tuple[str, tuple[str, ...]] / None` | ~2 site(s) · module:str, class_qualname:str, attr:str |
| `flowcli.analysis.index:ProjectIndex.find_class` | `(self, mod: ModuleInfo, parts: tuple[str, ...])` | `ClassRef / None` | ~10 site(s) · mod:ModuleInfo, parts:tuple |
| `flowcli.analysis.index:ProjectIndex.module_for` | `(self, dotted: str)` | `str / None` | ~3 site(s) · dotted:str |
| `flowcli.analysis.index:ProjectIndex.resolve_method` | `(self, module: str, class_qualname: str, method: str, skip_self: bool=False, _seen: set[ClassRef] / None=None)` | `str / None` | ~8 site(s) · module:index.module_for, class_qualname:str, method='__init__' |
| `flowcli.analysis.index:ProjectIndex.type_display` | `(self, mod: ModuleInfo, parts: tuple[str, ...])` | `str` | ~3 site(s) · mod:ModuleInfo, parts:caller.local_types.get |
| `flowcli.analysis.infer:_resolve_return_call` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...])` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.infer:_resolve_return_expr` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, tag: str, value: Any)` | `tuple[str / None, str / None]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.infer:infer_signatures` | `(index: ProjectIndex)` | `tuple[Signatures, RetLines]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.model:node_id` | `(module: str, qualname: str)` | `str` | ~24 site(s) · module:index.module_for, qualname:str |
| `flowcli.analysis.model:split_node_id` | `(nid: str)` | `tuple[str, str]` | ~4 site(s) · nid:str |
| `flowcli.analysis.parser:_Collector.__init__` | `(self, info: ModuleInfo)` | `None` | ~1 site(s) · info:ModuleInfo |
| `flowcli.analysis.parser:_Collector._classify_attribute` | `(self, expr: ast.Attribute, lineno: int)` | `RawCall` | ~1 site(s) · expr:ast.Attribute, lineno:int |
| `flowcli.analysis.parser:_Collector._classify_callable_expr` | `(self, expr: ast.expr, lineno: int)` | `RawCall / None` | ~2 site(s) · expr:ast.expr, lineno:int |
| `flowcli.analysis.parser:_Collector._ensure_module_fn` | `(self)` | `FunctionInfo` | ~1 site(s) · no args |
| `flowcli.analysis.parser:_Collector._handle_function` | `(self, node: ast.FunctionDef / ast.AsyncFunctionDef)` | `None` | ~2 site(s) · node:ast.AsyncFunctionDef |
| `flowcli.analysis.parser:_Collector._mark_generator` | `(self, node: ast.Yield / ast.YieldFrom)` | `None` | ~0 site(s) · node:ast.Yield / ast.YieldFrom |
| `flowcli.analysis.parser:_Collector._nearest_class` | `(self)` | `str / None` | ~3 site(s) · no args |
| `flowcli.analysis.parser:_Collector._qual` | `(self, name: str)` | `str` | ~2 site(s) · name:str |
| `flowcli.analysis.parser:_Collector._record_call` | `(self, rc: RawCall)` | `None` | ~2 site(s) · rc:RawCall |
| `flowcli.analysis.parser:_Collector._record_field` | `(self, ci: ClassInfo, name: str, ann: str / None=None, parts: tuple[str, ...]=(), value: str / None=None, lineno: int=0, source: str='class')` | `None` | ~2 site(s) · ci:ClassInfo, name:str, ann=None |
| `flowcli.analysis.parser:_Collector._record_self_attr` | `(self, attr: str, parts: tuple[str, ...], ann: str / None=None, lineno: int=0, source: str='init')` | `None` | ~4 site(s) · attr:str, parts:_annotation_parts, ann=None |
| `flowcli.analysis.parser:_Collector._resolve_from_base` | `(self, node: ast.ImportFrom)` | `str / None` | ~1 site(s) · node:ast.ImportFrom |
| `flowcli.analysis.parser:_Collector._visit_decorators` | `(self, node: ast.FunctionDef / ast.AsyncFunctionDef /)` | `list[str]` | ~2 site(s) · node:ast.ClassDef |
| `flowcli.analysis.parser:_Collector.visit_AnnAssign` | `(self, node: ast.AnnAssign)` | `None` | ~0 site(s) · node:ast.AnnAssign |
| `flowcli.analysis.parser:_Collector.visit_Assign` | `(self, node: ast.Assign)` | `None` | ~0 site(s) · node:ast.Assign |
| `flowcli.analysis.parser:_Collector.visit_AsyncFunctionDef` | `(self, node: ast.AsyncFunctionDef)` | `None` | ~0 site(s) · node:ast.AsyncFunctionDef |
| `flowcli.analysis.parser:_Collector.visit_Call` | `(self, node: ast.Call)` | `None` | ~0 site(s) · node:ast.Call |
| `flowcli.analysis.parser:_Collector.visit_ClassDef` | `(self, node: ast.ClassDef)` | `None` | ~0 site(s) · node:ast.ClassDef |
| `flowcli.analysis.parser:_Collector.visit_FunctionDef` | `(self, node: ast.FunctionDef)` | `None` | ~0 site(s) · node:ast.FunctionDef |
| `flowcli.analysis.parser:_Collector.visit_If` | `(self, node: ast.If)` | `None` | ~0 site(s) · node:ast.If |
| `flowcli.analysis.parser:_Collector.visit_Import` | `(self, node: ast.Import)` | `None` | ~0 site(s) · node:ast.Import |
| `flowcli.analysis.parser:_Collector.visit_ImportFrom` | `(self, node: ast.ImportFrom)` | `None` | ~0 site(s) · node:ast.ImportFrom |
| `flowcli.analysis.parser:_Collector.visit_Return` | `(self, node: ast.Return)` | `None` | ~0 site(s) · node:ast.Return |
| `flowcli.analysis.parser:_annotation_parts` | `(node: ast.expr)` | `tuple[str, ...]` | ~7 site(s) · node:ast.expr |
| `flowcli.analysis.parser:_classify_arg_expr` | `(value: ast.expr)` | `tuple[str, Any]` | ~2 site(s) · value:ast.expr |
| `flowcli.analysis.parser:_classify_args` | `(node: ast.Call)` | `tuple[ArgAtom, ...]` | ~1 site(s) · node:ast.Call |
| `flowcli.analysis.parser:_classify_return_expr` | `(value: ast.expr / None)` | `tuple[str, Any]` | ~1 site(s) · value:ast.expr / None |
| `flowcli.analysis.parser:_is_main_guard` | `(test: ast.expr)` | `bool` | ~1 site(s) · test:ast.expr |
| `flowcli.analysis.parser:_is_overload_stub` | `(node: ast.FunctionDef / ast.AsyncFunctionDef)` | `bool` | ~1 site(s) · node:ast.FunctionDef |
| `flowcli.analysis.parser:_literal_arg` | `(value: ast.expr)` | `tuple[str, Any] / None` | ~1 site(s) · value:ast.expr |
| `flowcli.analysis.parser:_param_list` | `(args: ast.arguments)` | `list[dict[str, str / None]]` | ~1 site(s) · args:ast.arguments |
| `flowcli.analysis.parser:_param_list.entry` | `(arg: ast.arg, default: ast.expr / None, prefix: str='')` | `dict[str, str / None]` | ~4 site(s) · arg:ast.arg, default=None, prefix=''/'*' |
| `flowcli.analysis.parser:parse_module` | `(module_name: str, file: Path)` | `ModuleInfo / ParseFailure` | ~1 site(s) · module_name:str, file:Path |
| `flowcli.analysis.parser:parse_source` | `(module_name: str, file: str, source: str, is_package: bool=False)` | `ModuleInfo / ParseFailure` | ~1 site(s) · module_name:str, file:str, source:fh.read |
| `flowcli.analysis.resolver:_constructor` | `(index: ProjectIndex, module: str, class_qualname: str, expr: str)` | `Outcome` | ~5 site(s) · index:ProjectIndex, module:index.module_for, class_qualname:str |
| `flowcli.analysis.resolver:_external` | `(dotted: str)` | `Outcome` | ~2 site(s) · dotted=f'builtins.{name}' |
| `flowcli.analysis.resolver:_internal` | `(target_id: str)` | `Outcome` | ~11 site(s) · target_id:index.resolve_method |
| `flowcli.analysis.resolver:_resolve_absolute` | `(index: ProjectIndex, dotted: str, expr: str, _seen: set[str] / None=None)` | `Outcome` | ~4 site(s) · index:ProjectIndex, dotted=f'{star_mod}.{rem}', expr:str |
| `flowcli.analysis.resolver:_resolve_dotted` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.resolver:_resolve_enclosing_scope` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, name: str, hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.resolver:_resolve_local_class_dotted` | `(index: ProjectIndex, mod: ModuleInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, parts:tuple[str, ...] |
| `flowcli.analysis.resolver:_resolve_name` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.resolver:_resolve_name_imported` | `(index: ProjectIndex, mod: ModuleInfo, name: str, hint: str)` | `Outcome` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, name:str |
| `flowcli.analysis.resolver:_resolve_self_attr_chain` | `(index: ProjectIndex, mod: ModuleInfo, class_qualname: str, call: RawCall)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, class_qualname:str |
| `flowcli.analysis.resolver:_resolve_typed_local` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...], hint: str)` | `Outcome / None` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.resolver:_unresolved` | `(expr: str, reason: str)` | `Outcome` | ~17 site(s) · expr:str, reason='instance-attr'/'not-found-in-hierarchy' |
| `flowcli.analysis.resolver:resolve_all` | `(index: ProjectIndex)` | `list[ResolvedCall]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.resolver:resolve_call` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, call: RawCall)` | `Outcome` | ~2 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.resolver:resolve_parts` | `(index: ProjectIndex, mod: ModuleInfo, fn: FunctionInfo, parts: tuple[str, ...])` | `Outcome` | ~2 site(s) · index:ProjectIndex, mod:ModuleInfo, fn:FunctionInfo |
| `flowcli.analysis.simulate:_Site.__init__` | `(self, caller: str, target: str, lineno: int, pairs: list[tuple[str, tuple[str, Any]]])` | `None` | ~1 site(s) · caller:str, target:str, lineno:int |
| `flowcli.analysis.simulate:_absorb` | `(slot: dict[str, Any], types: list[str], value: str / None, source: str)` | `bool` | ~3 site(s) · slot:dict[str, Any], types=[str(p['ann'])]/[], value=None |
| `flowcli.analysis.simulate:_bind_site` | `(rc: ResolvedCall, fns: dict[str, FunctionInfo])` | `_Site / None` | ~1 site(s) · rc:ResolvedCall, fns:_function_index |
| `flowcli.analysis.simulate:_eval_atom` | `(index: ProjectIndex, fns: dict[str, FunctionInfo], records: dict[str, dict[str, Any]], signatures: dict[str, dict[str, Any]], caller_id: str, atom: tuple[str, Any])` | `tuple[list[str], str / None]` | ~1 site(s) · index:ProjectIndex, fns:_function_index, records:dict |
| `flowcli.analysis.simulate:_function_index` | `(index: ProjectIndex)` | `dict[str, FunctionInfo]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.simulate:_param_names` | `(fn: FunctionInfo)` | `list[str]` | ~2 site(s) · fn:FunctionInfo |
| `flowcli.analysis.simulate:_returns_of_call` | `(index: ProjectIndex, mod: ModuleInfo, caller: FunctionInfo, signatures: dict[str, dict[str, Any]], parts: tuple[str, ...])` | `list[str]` | ~1 site(s) · index:ProjectIndex, mod:ModuleInfo, caller:FunctionInfo |
| `flowcli.analysis.simulate:_seed_entry` | `(rec: dict[str, Any] / None, fn: FunctionInfo / None)` | `None` | ~1 site(s) · rec:dict[str, Any] / None, fn:FunctionInfo / None |
| `flowcli.analysis.simulate:_simulated_events` | `(sites: list[_Site], entry_ids: list[str])` | `list[list[str]]` | ~1 site(s) · sites:list[_Site], entry_ids:list[str] |
| `flowcli.analysis.simulate:_walk` | `(node: str, out_edges: dict[str, list[tuple[int, str]]], stack: set[str], events: list[list[str]])` | `None` | ~2 site(s) · node:str, out_edges:dict, stack:set |
| `flowcli.analysis.simulate:module_entry_candidates` | `(index: ProjectIndex)` | `list[str]` | ~1 site(s) · index:ProjectIndex |
| `flowcli.analysis.simulate:simulate` | `(index: ProjectIndex, resolved: list[ResolvedCall], signatures: dict[str, dict[str, Any]], entry_ids: list[str] / None=None)` | `tuple[dict[str, dict[str, Any]], list[list[str]]]` | ~1 site(s) · index:ProjectIndex, resolved:list, signatures:dict[str, dict[str, Any]] |
| `flowcli.cli:_add_map_parser` | `(sub: argparse._SubParsersAction)` | `None` | ~1 site(s) · sub:argparse._SubParsersAction |
| `flowcli.cli:_add_run_parser` | `(sub: argparse._SubParsersAction)` | `None` | ~1 site(s) · sub:argparse._SubParsersAction |
| `flowcli.cli:_cmd_map` | `(args: argparse.Namespace)` | `int` | ~1 site(s) · args:argparse.Namespace |
| `flowcli.cli:_cmd_run` | `(args: argparse.Namespace)` | `int` | ~1 site(s) · args:argparse.Namespace |
| `flowcli.cli:_entry_specs` | `(raw: list[str], root: Path)` | `list[str]` | ~1 site(s) · raw:list[str], root:Path |
| `flowcli.cli:_fail` | `(message: str, code: int=1, prefix: str='error: ')` | `int` | ~5 site(s) · message=f'path not found: {args.path}'/f"unknown format(s): {', '.joi, code=1, prefix='error: ' |
| `flowcli.cli:_resolve_entry` | `(entry: str, root: Path)` | `str` | ~1 site(s) · entry:str, root:Path |
| `flowcli.cli:main` | `(argv: list[str] / None=None)` | `int` | ~2 site(s) · argv=None |
| `flowcli.graph.build:_annotate_flow` | `(flow: list[dict], calls: list[tuple[int, str]])` | `None` | ~4 site(s) · flow:list[dict], calls:list |
| `flowcli.graph.build:_annotate_ret_types` | `(flow: list[dict], line_map: dict[int, str])` | `None` | ~4 site(s) · flow:list[dict], line_map:dict |
| `flowcli.graph.build:_apply_edges` | `(nodes: dict[str, Node], resolved: list[ResolvedCall], include_external: bool)` | `list[UnresolvedCall]` | ~1 site(s) · nodes:_make_nodes, resolved:list, include_external:bool |
| `flowcli.graph.build:_make_nodes` | `(index: ProjectIndex, resolved: list[ResolvedCall])` | `dict[str, Node]` | ~1 site(s) · index:ProjectIndex, resolved:list |
| `flowcli.graph.build:apply_runtime` | `(graph: Graph, runtime: dict)` | `int` | ~1 site(s) · graph:Graph, runtime:dict |
| `flowcli.graph.build:apply_simulation` | `(graph: Graph, index: ProjectIndex, resolved: list[ResolvedCall], entry_ids: list[str] / None=None)` | `list[list[str]]` | ~1 site(s) · graph:Graph, index:ProjectIndex, resolved:list[ResolvedCall] |
| `flowcli.graph.build:build_graph` | `(index: ProjectIndex, resolved: list[ResolvedCall], include_external: bool=False)` | `Graph` | ~1 site(s) · index:ProjectIndex, resolved:list[ResolvedCall], include_external=False |
| `flowcli.graph.entry:_find_module` | `(mod_part: str, index: ProjectIndex)` | `ModuleInfo` | ~1 site(s) · mod_part:str, index:ProjectIndex |
| `flowcli.graph.entry:_find_subtree` | `(mod_part: str, index: ProjectIndex)` | `tuple[str, list[str]] / None` | ~1 site(s) · mod_part:str, index:ProjectIndex |
| `flowcli.graph.entry:parse_entry_spec` | `(spec: str, index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · spec:str, index:ProjectIndex |
| `flowcli.graph.entry:parse_entry_specs` | `(specs: Sequence[str], index: ProjectIndex)` | `tuple[str, list[str]]` | ~1 site(s) · specs:Sequence[str], index:ProjectIndex |
| `flowcli.graph.entry:split_entry_spec` | `(spec: str)` | `tuple[str, str / None]` | ~2 site(s) · spec:str |
| `flowcli.graph.scope:compute_depths` | `(graph: Graph, entries: str / Sequence[str], max_depth: int / None=None)` | `int` | ~1 site(s) · graph:Graph, entries:list, max_depth=None |
| `flowcli.graph.scope:prune_unreachable` | `(graph: Graph)` | `int` | ~1 site(s) · graph:Graph |
| `flowcli.output.html:_class_payload` | `(class_graph: ClassGraph / None)` | `dict[str, Any]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.output.html:_module_of` | `(nid: str)` | `str` | ~2 site(s) · nid:str |
| `flowcli.output.html:_node_entry` | `(n: Node, module_index: int)` | `dict[str, Any]` | ~1 site(s) · n:Node, module_index:int |
| `flowcli.output.html:build_payload` | `(graph: Graph, meta: dict[str, Any], runtime: dict[str, Any] / None=None)` | `dict[str, Any]` | ~1 site(s) · graph:Graph, meta:dict, runtime=None |
| `flowcli.output.html:render_html` | `(graph: Graph, meta: dict[str, Any], out: Path, runtime: dict[str, Any] / None=None, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict[str, Any], out:Path |
| `flowcli.output.report:_by_out_degree` | `(graph: Graph)` | `list[Node]` | ~2 site(s) · graph:Graph |
| `flowcli.output.report:_cell` | `(text: str)` | `str` | ~7 site(s) · text=f"{node.dynamic.get('ncalls', /f'~{sites} site(s) · {detail}' |
| `flowcli.output.report:_classes_section` | `(class_graph: ClassGraph / None)` | `list[str]` | ~1 site(s) · class_graph:ClassGraph |
| `flowcli.output.report:_loc` | `(node: Node, root: str)` | `str` | ~1 site(s) · node:Node, root:str |
| `flowcli.output.report:_most_called_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.output.report:_params_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.output.report:_returns_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.output.report:_runtime_str` | `(node: Node)` | `str` | ~1 site(s) · node:Node |
| `flowcli.output.report:_signatures_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.output.report:_unreachable_section` | `(graph: Graph, meta: dict[str, Any])` | `list[str]` | ~1 site(s) · graph:Graph, meta:dict |
| `flowcli.output.report:_unresolved_section` | `(graph: Graph)` | `list[str]` | ~1 site(s) · graph:Graph |
| `flowcli.output.report:print_summary` | `(graph: Graph, meta: dict[str, Any])` | `None` | ~1 site(s) · graph:Graph, meta:dict[str, Any] |
| `flowcli.output.report:write_json` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict[str, Any], out:Path |
| `flowcli.output.report:write_markdown` | `(graph: Graph, meta: dict[str, Any], out: Path, class_graph: ClassGraph / None=None)` | `None` | ~1 site(s) · graph:Graph, meta:dict[str, Any], out:Path |
| `flowcli.pipeline:MapError.__init__` | `(self, message: str, exit_code: int=1)` | `None` | ~4 site(s) · message=f'no Python files found under /'no parseable Python files', exit_code=1/2 |
| `flowcli.pipeline:_parse_all` | `(files: list[tuple[str, Path]])` | `tuple[dict[str, ModuleInfo], list[ParseFailure]]` | ~1 site(s) · files:discover |
| `flowcli.pipeline:_read_runtime` | `(path: Path)` | `dict[str, Any]` | ~1 site(s) · path:Path |
| `flowcli.pipeline:map_project` | `(opts: MapOptions)` | `MapResult` | ~1 site(s) · opts:MapOptions |
| `flowcli.pipeline:write_outputs` | `(result: MapResult, formats: set[str], out_dir: Path)` | `None` | ~1 site(s) · result:MapResult, formats:set[str], out_dir:Path |
| `flowcli.runtime.runner:Program.argv` | `(self)` | `list[str]` | — |
| `flowcli.runtime.runner:Program.home` | `(self)` | `Path` | — |
| `flowcli.runtime.runner:Program.parse` | `(cls, prog: list[str])` | `Program` | ~1 site(s) · prog:list[str] |
| `flowcli.runtime.runner:_exit_code_of` | `(exc: SystemExit)` | `int` | ~1 site(s) · exc:SystemExit |
| `flowcli.runtime.runner:execute` | `(program: Program, root: Path, samples: bool)` | `tuple[RuntimeCapture, int]` | ~1 site(s) · program:Program, root:Path, samples:bool |
| `flowcli.runtime.runner:runtime_payload` | `(cap: RuntimeCapture, program: Program, root: Path, exit_code: int, samples: bool)` | `dict[str, Any]` | ~1 site(s) · cap:RuntimeCapture, program:Program, root:Path |
| `flowcli.runtime.tracer:_param_names` | `(code: CodeType)` | `list[tuple[str, str]]` | ~1 site(s) · code:CodeType |
| `flowcli.runtime.tracer:_safe_repr` | `(value: Any)` | `str` | ~2 site(s) · value:Any |
| `flowcli.runtime.tracer:_type_name` | `(value: Any)` | `str` | ~2 site(s) · value:Any |
| `flowcli.runtime.tracer:capture` | `(root: Path, samples: bool=True)` | `Iterator[RuntimeCapture]` | ~1 site(s) · root:Path, samples=True |
| `flowcli.runtime.tracer:capture.module_of` | `(filename: str)` | `str / None` | ~1 site(s) · filename:str |
| `flowcli.runtime.tracer:capture.node_for` | `(code: CodeType)` | `str / None` | ~2 site(s) · code:CodeType |
| `flowcli.runtime.tracer:capture.on_call` | `(frame: FrameType)` | `None` | ~1 site(s) · frame:FrameType |
| `flowcli.runtime.tracer:capture.on_return` | `(frame: FrameType, arg: Any)` | `None` | ~1 site(s) · frame:FrameType, arg:Any |
| `flowcli.runtime.tracer:capture.profiler` | `(frame: FrameType, event: str, arg: Any)` | `None` | ~0 site(s) · frame:FrameType, event:str, arg:Any |

## Classes

| Class | Kind | Inherits | Properties | Holds |
|---|---|---|---|---|
| `flowcli.analysis.classes:ClassEdge` | dataclass | — | source: str, target: str, kind: str, label: str | — |
| `flowcli.analysis.classes:ClassGraph` | dataclass | — | nodes: dict[str, ClassNode], edges: list[ClassEdge] | — |
| `flowcli.analysis.classes:ClassNode` | dataclass | — | id: str, module: str, name: str, file: str, lineno: int, stereotype: str, … +4 | — |
| `flowcli.analysis.index:ProjectIndex` | class | — | modules | — |
| `flowcli.analysis.model:CallKind` | enum | enum.Enum | NAME, DOTTED, SELF_ATTR, CLS_ATTR, SUPER_ATTR, OPAQUE | — |
| `flowcli.analysis.model:ClassInfo` | dataclass | — | qualname: str, module: str, lineno: int, bases: list[tuple[str, ...]], base_reprs: list[str], methods: dict[str, str], … +3 | — |
| `flowcli.analysis.model:FunctionInfo` | dataclass | — | qualname: str, module: str, file: str, lineno: int, class_qualname: str / None, raw_calls: list[RawCall], … +8 | — |
| `flowcli.analysis.model:ModuleInfo` | dataclass | — | name: str, file: str, is_package: bool, imports: dict[str, str], star_imports: list[str], functions: dict[str, FunctionInfo], … +2 | — |
| `flowcli.analysis.model:ParseFailure` | dataclass | — | file: str, error: str | — |
| `flowcli.analysis.model:RawCall` | dataclass | — | kind: CallKind, parts: tuple[str, ...], lineno: int, repr_hint: str, args: tuple[ArgAtom, ...] | kind → CallKind |
| `flowcli.analysis.parser:_Collector` | class | ast.NodeVisitor | info, _stack: list[tuple[str, str]], _sink: FunctionInfo / None, visit_Yield, visit_YieldFrom | _sink → FunctionInfo |
| `flowcli.analysis.resolver:ResolvedCall` | dataclass | — | caller: str, lineno: int, status: str, target: str, reason: str, call: RawCall / None | call → RawCall |
| `flowcli.analysis.simulate:_Site` | class | — | __slots__, caller, target, lineno, pairs | — |
| `flowcli.graph.model:Graph` | dataclass | — | nodes: dict[str, Node], unresolved: list[UnresolvedCall], entry: str / None | — |
| `flowcli.graph.model:Node` | dataclass | — | id: str, file: str, lineno: int, calls: list[str], called_by: list[str], depth: int / None, … +7 | — |
| `flowcli.graph.model:UnresolvedCall` | dataclass | — | caller: str, callee_expr: str, lineno: int, reason: str | — |
| `flowcli.pipeline:MapError` | class | Exception | exit_code | — |
| `flowcli.pipeline:MapOptions` | dataclass | — | root: Path, entries: list[str], exclude: list[str], depth: int / None, keep_unreachable: bool, include_external: bool, … +3 | — |
| `flowcli.pipeline:MapResult` | dataclass | — | graph: Graph, meta: dict[str, Any], class_graph: ClassGraph / None, replay: list[list[str]], suggestions: list[dict[str, Any]] | class_graph → ClassGraph, graph → Graph |
| `flowcli.runtime.runner:Program` | dataclass | — | mode: str, target: str, args: tuple[str, ...] | — |
| `flowcli.runtime.tracer:RuntimeCapture` | dataclass | — | functions: dict[str, dict[str, Any]], events: list[list[str]], calls_total: int, events_truncated: bool | — |

## Unresolved calls

- **external**: 402
- **instance-attr**: 324
- **opaque**: 88
- **not-found-in-hierarchy**: 43
- **unknown-name**: 1

| Callee expression | Occurrences |
|---|---:|
| `builtins.len` | 71 |
| `builtins.isinstance` | 58 |
| `builtins.sorted` | 38 |
| `dataclasses.field` | 32 |
| `builtins.str` | 21 |
| `p.add_argument` | 18 |
| `builtins.set` | 17 |
| `dataclasses.dataclass` | 16 |
| `builtins.list` | 16 |
| `meta.get` | 16 |
| `'.'.join` | 15 |
| `pathlib.Path` | 14 |
| `', '.join` | 14 |
| `builtins.print` | 14 |
| `out.append` | 12 |
