import os, sys, argparse
from fabric_cicd import change_log_level
from fabric_cicd._parameter._utils import validate_parameter_file

change_log_level("DEBUG")

parser = argparse.ArgumentParser(description='Process Debug parameters arguments.')
parser.add_argument('--target_env', type=str, help= 'target environment')
args = parser.parse_args()
tgtenv = args.target_env
print(f'Target environment set to {tgtenv}')

repository_directory = os.environ["GITDIRECTORY"]
item_type_in_scope = ["Notebook", "DataPipeline", "Lakehouse", "SemanticModel", "Report", "VariableLibrary"]

validate_parameter_file(
    repository_directory=repository_directory,
    item_type_in_scope=item_type_in_scope,
    environment=tgtenv,
)



