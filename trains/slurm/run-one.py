import os, json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(THIS_DIR)

run_list_path = os.path.join(THIS_DIR, 'run-list.json')
with open(run_list_path, 'r') as f:
    run_list = json.load(f)

conda_path = '/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/slurm/main-conda.sh'

if len(run_list) == 0:
    print('No more runs to run.')
    exit(0)
current_run = run_list[0]
os.system('sbatch {cp} {cr}'.format(cp=conda_path, cr=current_run))

with open(run_list_path, 'w') as f:
    json.dump(run_list[1:], f)
