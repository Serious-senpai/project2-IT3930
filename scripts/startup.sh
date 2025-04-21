#! https://stackoverflow.com/a/246128
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
ROOT_DIR=$(realpath $SCRIPT_DIR/..)

cd $ROOT_DIR
pip install --no-cache-dir -r requirements.txt
python main.py --help
python main.py --log-level warning --cors
