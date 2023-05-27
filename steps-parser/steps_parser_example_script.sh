#SBATCH --ntasks=2
#SBATCH --gres=gpu:1 
#SBATCH --partition=short
#SBATCH --output=%j-steps_baseline-qtd_trde90_onlyfortrain_TEST_batchsize_8_es_200_08-11-output.out
#SBATCH --mail-type=ALL
# #SBATCH --mail-user=sbetulbilgin@gmail.com
#SBATCH --mem 70GB
#SBATCH -w sn01


################################################################################
source /etc/profile.d/z_compecta.sh
echo "source /etc/profile.d/z_compecta.sh"
################################################################################

# MODULES LOAD...
echo "CompecTA Pulsar..."
# module load compecta/pulsar


# module load gcc/7.3.0
# module load cudnn/7.1.1/cuda-9.0
# module load singularity/2.3.2
#module load /cta/users/bozates/anaconda3/bin/python
module load cudnn-8.0.4.30-11.0-linux-x64-gcc-10.2.0-m3wjmr4

 
################################################################################

echo ""
echo "============================== ENVIRONMENT VARIABLES ==============================="
env
echo "===================================================================================="
echo ""
echo ""

# PULSAR=/cta/apps/compecta/pulsar/pulsar



echo "Running Tensorflow command..."
echo "===================================================================================="


python3 src/train.py ../baseline-only-deps-qtd-2.8.json

RET=$?

echo ""
echo "===================================================================================="
echo "Solver exited with return code: $RET"
exit $RET

