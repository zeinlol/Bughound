#!/usr/bin/python3

from datetime import datetime

from core import arguments
from core.elastic_api import check_elastic_connection
from core.functions.analyze_input import get_extension, check_language
from core.functions.data_processing import convert_findings_to_json, convert_findings_to_str
from core.functions.files import get_files_for_analyze, write_findings_to_file
from core.functions.print_output import print_banner, print_url, print_error, print_note, print_results, \
    print_results_as_json
from core.parser import Parser, get_total_findings

local_path = arguments.path
git_repo = arguments.git
project_name = arguments.name
verbose = arguments.verbose


def main():
    print_banner()

    language = arguments.language.lower()
    extension = get_extension()

    start_time = datetime.now()

    if not check_language(language):
        print_error(f"Language {language} not supported!")
        exit()

    # Check connection to Elastic
    if arguments.use_elastic:
        check_elastic_connection()

    if local_path is None and git_repo is None:
        print_error("Please specify the git repo or local path to scan")
        exit()

    if local_path and git_repo:
        print_error("Please specify one target source!'\nDon't use --git and --path arguments in one time!")
        exit()

    files = get_files_for_analyze(extension=extension)

    print_note(f"Scanning started at {start_time}!")
    for file in files:
        parser = Parser(file, project_name, language)
        file_metadata = parser.calculate_meta_data()
        functions = parser.get_functions(verbose)

    findings = get_total_findings()
    findings_length = len(findings)

    if arguments.json:
        findings = convert_findings_to_json(findings)
        if arguments.output:
            write_findings_to_file(findings=findings, file=arguments.output)
        else:
            print_results_as_json(findings)
    else:
        findings = convert_findings_to_str(findings)
        if arguments.output:
            write_findings_to_file(findings=findings, file=arguments.output)
        else:
            print_results(findings)

    if arguments.use_elastic:
        print_url(project_name)

    end_time = datetime.now()
    print_note(f"Scanning finished at {end_time}!")
    total_time = str(end_time - start_time)
    print_note(f"Total scan time is: {total_time} seconds.\nTotal issues found : {findings_length}")


if __name__ == '__main__':
    main()
